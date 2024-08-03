import abc
import subprocess
import pathlib
import json

from benchmarking.harness import harnesses


script_format = r"""\
. {venv}/bin/activate {venv}/
set -euo pipefail
{venv}/bin/python {python_flags} {script}
"""

class Runner(abc.ABC):
    subprocess_args = {
        "capture_output": True,
        "check": True,
        "text": True,
    }

    @abc.abstractmethod
    def run():
        pass


class PythonRunner(Runner):
    libraries = harnesses["python"]

    def __init__(
            self,
            *,
            virtual_env: pathlib.Path,
            library: str,
            run_list: dict[str, list],
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

        self.script = script_format.format(
            venv=virtual_env,
            python_flags=" ".join(flags),
            script=self.libraries[library]
        )

        self.run_config = {
            "benchmark": benchmark,
            "cpu": cpu_profiling,
            "mem": mem_profiling,
            "run_list": run_list,
        }

    def run(self):
        return subprocess.run(
            self.script,
            shell=True,
            input=json.dumps(self.run_config),
            **self.subprocess_args,
        )


class MathematicaRunner(Runner):
    pass
