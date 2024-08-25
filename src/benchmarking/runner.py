import os
import abc
import subprocess
import pathlib
import pickle
import itertools
import logging
import tempfile
from dataclasses import dataclass

from benchmarking.harness import harnesses

logger = logging.getLogger(__name__)

_script_format = r"""\
. {venv}/bin/activate {venv}/
set -euo pipefail
{venv}/bin/python {python_flags} {script}"""

_samply_script_format = r"""\
. {venv}/bin/activate {venv}/
set -euo pipefail
samply record --save-only --reuse-threads --profile-name {output} --rate 500 -o {output} -- {venv}/bin/python {python_flags} {script}"""

_memray_script_format = r"""\
. {venv}/bin/activate {venv}/
set -euo pipefail
{venv}/bin/python {python_flags} -m memray run --native --trace-python-allocators --aggregate --quiet --follow-fork --force -o {output} -- {script}
"""

_external_run_config_format = """\
Running {lib}."""

_report_format = """\
{lib} process finished:
\tstdout (unpickled): {stdout!s}
\tstderr: '{stderr}'"""

_python_run_config_format = (
    _external_run_config_format[:-1]
    + """ with:
\tconfig: {run_config}
\tvenv: {venv}
\tflags: {flags}
\tenv vars: {env}"""
)

_python_run_config_sum_format = """
Running with Python libraries:
\t{libs}

Python run configuration:
\tBenchmarking?: {benchmark}
\tCPU profiling?: {cpu}
\tMemory profiling?: {mem}
\tVirtual environments: {venvs}
\tGarbage collection?: {gc}
\tInterpreter flags: {flags}"""

_external_run_config_sum_format = """
Running with external libraries:
\t{libs}"""


class Runner(abc.ABC):
    subprocess_args = {
        "stdin": subprocess.PIPE,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
    }

    def __init__(self, library: str, flags: list[str], verbose, output_dir):
        assert library in self.libraries
        self.library = library
        self.env = os.environ | self.libraries[library]["env"]

        if flags is None:
            flags = []

        self.flags = flags
        self.log_file = tempfile.NamedTemporaryFile(delete=False, dir=output_dir, prefix=(self.library + "-")) if verbose else None

    @abc.abstractmethod
    def start():
        pass

    @abc.abstractmethod
    def collect():
        pass

    def dump_dict(self):
        return {
            "library": self.library,
            "flags": self.flags,
            "gc": self.run_config["gc"],
        }


class PythonRunner(Runner):
    libraries = harnesses["python"]
    run_config_format = _python_run_config_format
    report_format = _report_format

    def __init__(
        self,
        *,
        virtual_env: pathlib.Path,
        library: str,
        run_list: list[str],
        polys: dict,
        type: str,
        gc: bool,
        repeats: int,
        output_dir: pathlib.Path,
        flags: list[str] = None,
        verbose: bool = False,
    ):
        super().__init__(library, flags, verbose, output_dir)

        self.venv = virtual_env

        if type == "cpu":
            self.profile_file = output_dir / f"{self.library}_{virtual_env.stem}_samply_profile.json"
            self.script = _samply_script_format.format(
                venv=virtual_env,
                python_flags=" ".join(self.flags + ["-X", "perf"]),
                script=self.libraries[library]["file"],
                output=self.profile_file,
            )
        elif type == "mem":
            self.profile_file = output_dir / f"{self.library}_{virtual_env.stem}_memray_profile.bin"
            self.script = _memray_script_format.format(
                venv=virtual_env,
                python_flags=" ".join(self.flags),
                script=self.libraries[library]["file"],
                output=self.profile_file,
            )
        else:
            self.profile_file = None
            self.script = _script_format.format(
                venv=virtual_env, python_flags=" ".join(self.flags), script=self.libraries[library]["file"]
            )

        self.run_config = {
            "type": type,
            "run_list": run_list,
            "polys": polys,
            "gc": gc,
            "repeats": repeats,
            "log_file": self.log_file.name if self.log_file is not None else None,
        }

    def start(self):
        logger.info(
            self.run_config_format.format(
                lib=self.library,
                run_config={k: v for k, v in self.run_config.items() if k != "polys"},
                venv=self.venv,
                flags=self.flags,
                env=self.libraries[self.library]["env"],
            )
        )

        self.process = subprocess.Popen(
            self.script,
            shell=True,
            env=self.env,
            **self.subprocess_args,
        )

        self.process.stdin.write(pickle.dumps(self.run_config))
        self.process.stdin.flush()
        self.process.stdin.close()

    def collect(self):
        stdout = self.process.stdout.read()
        self.stderr = self.process.stderr.read().decode("utf-8").strip()
        try:
            self.stdout = pickle.loads(stdout) if stdout else None
        except pickle.UnpicklingError as e:
            try:
                e.add_note(f"Received stdout: '{stdout.decode('utf-8')}'")
            except Exception:
                pass
            e.add_note(f"Received stderr: '{self.stderr}'")
            raise e

        if self.profile_file is not None and self.stdout is not None:
            self.stdout["profile_file"] = self.profile_file.name

        logger.debug(
            self.report_format.format(
                lib=self.library,
                run_config=self.run_config,
                venv=self.venv,
                stdout=self.stdout,
                stderr=self.stderr,
                flags=self.flags,
            )
        )

        return self.process

    def dump_dict(self):
        return super().dump_dict() | {
            "stdout": self.stdout,
            "venv": self.venv,
        }


class MathematicaRunner(Runner):
    libraries = harnesses["external"]
    run_config_format = _external_run_config_format
    report_format = _report_format


@dataclass
class RunSpec:
    verbose: bool
    libs: list[str]
    benchmark: bool
    repeats: int
    run_list: list[str]
    polys: dict
    output_dir: pathlib.Path

    def run(self):
        self.processes = [x.run() for x in self.runners]


@dataclass
class PythonRunSpec(RunSpec):
    venvs: list[pathlib.Path]
    cpu: bool
    mem: bool
    gc: list[bool]
    flags: list[str]

    def __post_init__(self):
        assert 0 < len(self.gc) <= 2
        logger.info(
            _python_run_config_sum_format.format(
                libs=", ".join(self.libs),
                benchmark=self.benchmark,
                cpu=self.cpu,
                mem=self.mem,
                venvs=[str(x.absolute()) for x in self.venvs],
                gc=self.gc,
                flags=self.flags,
            )
            if self.libs
            else "Running with no Python libraries."
        )

        types = (
            (["benchmark"] if self.benchmark else []) +
            (["cpu"] if self.cpu else []) +
            (["mem"] if self.mem else [])
        )

        self.runners = [
            PythonRunner(
                virtual_env=venv,
                library=lib,
                run_list=self.run_list,
                type=type,
                polys=self.polys,
                gc=gc,
                repeats=self.repeats,
                verbose=self.verbose,
                flags=self.flags,
                output_dir=self.output_dir,
            )
            for lib, venv, gc, type in itertools.product(self.libs, self.venvs, self.gc, types)
        ]


@dataclass
class ExternalRunSpec(RunSpec):
    def __post_init__(self):
        logger.info(
            _external_run_config_sum_format.format(
                libs=", ".join(self.libs),
            )
            if self.libs
            else "Running with no external libraries."
        )
        self.runners = []


# def create_runners(python_libs, venvs, external_)
