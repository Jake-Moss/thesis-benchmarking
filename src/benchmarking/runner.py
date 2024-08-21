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

_perf_script_format = r"""\
. {venv}/bin/activate {venv}/
set -euo pipefail
samply record --save-only -o {output} -- {venv}/bin/python {python_flags} {script}"""

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
        "capture_output": True,
    }

    def __init__(self, library: str, flags: list[str], verbose):
        assert library in self.libraries
        self.library = library
        self.env = os.environ | self.libraries[library]["env"]

        if flags is None:
            flags = tuple()

        self.flags = flags
        self.log_file = tempfile.NamedTemporaryFile(delete=False) if verbose else None

    @abc.abstractmethod
    def run():
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
        benchmark: bool,
        cpu_profiling: bool,
        mem_profiling: bool,
        gc: bool,
        repeats: int,
        flags: list[str] = None,
        verbose: bool = False,
    ):
        super().__init__(library, flags, verbose)

        self.venv = virtual_env
        if cpu_profiling:
            self.samply_file = tempfile.NamedTemporaryFile(delete=False) if verbose else None
            self.script = _perf_script_format.format(
                venv=virtual_env,
                python_flags=" ".join(self.flags),
                script=self.libraries[library]["file"],
                output=self.samply_file.name,
            )
        else:
            self.samply_file = None
            self.script = _script_format.format(
                venv=virtual_env, python_flags=" ".join(self.flags), script=self.libraries[library]["file"]
            )

        self.run_config = {
            "benchmark": benchmark,
            "cpu": cpu_profiling,
            "mem": mem_profiling,
            "run_list": run_list,
            "polys": polys,
            "gc": gc,
            "repeats": repeats,
            "log_file": self.log_file.name if self.log_file is not None else None,
        }

    def run(self):
        logger.info(
            self.run_config_format.format(
                lib=self.library,
                run_config={k: v for k, v in self.run_config.items() if k != "polys"},
                venv=self.venv,
                flags=self.flags,
                env=self.libraries[self.library]["env"],
            )
        )

        self.process = subprocess.run(
            self.script,
            shell=True,
            input=pickle.dumps(self.run_config),
            env=self.env,
            **self.subprocess_args,
        )

        self.stdout = pickle.loads(self.process.stdout) if self.process.stdout else None

        if self.samply_file is not None:
            self.stdout["samply_file"] = self.samply_file.name

        logger.debug(
            self.report_format.format(
                lib=self.library,
                run_config=self.run_config,
                venv=self.venv,
                stdout=self.stdout,
                stderr=self.process.stderr.decode("utf-8").strip(),
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

        self.runners = [
            PythonRunner(
                virtual_env=venv,
                library=lib,
                run_list=self.run_list,
                benchmark=self.benchmark,
                cpu_profiling=self.cpu,
                mem_profiling=self.mem,
                polys=self.polys,
                gc=gc,
                repeats=self.repeats,
                verbose=self.verbose,
                flags=self.flags,
            )
            for lib, venv, gc in itertools.product(self.libs, self.venvs, self.gc)
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
