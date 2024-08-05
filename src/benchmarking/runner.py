import abc
import subprocess
import pathlib
import pickle
import itertools
import logging
from dataclasses import dataclass

from benchmarking.harness import harnesses

logger = logging.getLogger(__name__)

_script_format = r"""\
. {venv}/bin/activate {venv}/
set -euo pipefail
{venv}/bin/python {python_flags} {script}"""

_external_run_config_format = """\
Running {lib}."""

_report_format = """\
{lib} process finished:
\tstdout: '{stdout}'
\tstderr: '{stderr}'"""

_python_run_config_format = (
    _external_run_config_format[:-1]
    + """ with:
\tconfig: {run_config}
\tvenv: {venv}
\tflags: {flags}"""
)

_python_run_config_sum_format = """
Running with Python libraries:
\t{libs}

Python run configuration:
\tBenchmarking?: {benchmark}
\tCPU profiling?: {cpu}
\tMemory profiling?: {mem}
\tVirtual environments: {venvs}"""

_external_run_config_sum_format = """
Running with external libraries:
\t{libs}"""


class Runner(abc.ABC):
    subprocess_args = {
        "capture_output": True,
        # "check": True,
    }

    @abc.abstractmethod
    def run():
        pass


class PythonRunner(Runner):
    libraries = harnesses["python"]
    script_format = _script_format
    run_config_format = _python_run_config_format
    report_format = _report_format

    def __init__(
        self,
        *,
        virtual_env: pathlib.Path,
        library: str,
        run_list: dict[str, list],
        polys: dict,
        benchmark: bool,
        cpu_profiling: bool,
        mem_profiling: bool,
        flags: list[str] = None,
    ):
        assert library in self.libraries
        if flags is None:
            flags = []

        self.library = library
        self.flags = flags
        self.venv = virtual_env

        self.script = self.script_format.format(
            venv=virtual_env, python_flags=" ".join(flags), script=self.libraries[library]
        )

        self.run_config = {
            "benchmark": benchmark,
            "cpu": cpu_profiling,
            "mem": mem_profiling,
            "run_list": run_list,
            "polys": polys,
        }

    def run(self):
        logger.info(
            self.run_config_format.format(
                lib=self.library,
                run_config=self.run_config,
                venv=self.venv,
                flags=self.flags,
            )
        )

        self.process = subprocess.run(
            self.script,
            shell=True,
            input=pickle.dumps(self.run_config),
            **self.subprocess_args,
        )

        logger.info(
            self.report_format.format(
                lib=self.library,
                run_config=self.run_config,
                venv=self.venv,
                stdout=self.process.stdout.decode("utf-8").strip(),
                stderr=self.process.stderr.decode("utf-8").strip(),
                flags=self.flags,
            )
        )

        return self.process


class MathematicaRunner(Runner):
    libraries = harnesses["external"]
    run_config_format = _external_run_config_format
    report_format = _report_format


@dataclass
class RunSpec:
    libs: list[str]
    benchmark: bool
    run_list: list[str]
    # polys: dict[]

    def run(self):
        self.processes = [x.run() for x in self.runners]


@dataclass
class PythonRunSpec(RunSpec):
    venvs: list[pathlib.Path]
    cpu: bool
    mem: bool

    def __post_init__(self):
        logger.info(
            _python_run_config_sum_format.format(
                libs=", ".join(self.libs),
                benchmark=self.benchmark,
                cpu=self.cpu,
                mem=self.mem,
                venvs=[str(x.absolute()) for x in self.venvs],
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
            )
            for lib, venv in itertools.product(self.libs, self.venvs)
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
