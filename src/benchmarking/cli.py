import argparse
import logging
import pathlib
import itertools
from benchmarking.harness import harnesses
from benchmarking.runner import PythonRunner

logger = logging.getLogger(__name__)

report_format = """\
{lib} process finished:
\tconfig: {run_config}
\tvenv: {venv}
\tflags: {flags}
\tstdout: '{stdout}'
\tstderr: '{stderr}'
"""

python_run_config_format = """
Running with Python libraries:
\t{libs}

Python run configuration:
\tCPU profiling: {cpu}
\tMemory profiling: {mem}
\tVirtual environments: {venvs}"""

external_run_config_format = """
Running with external libraries:
\t{libs}"""

default_venvs = [pathlib.Path().parent / ".venv-311", pathlib.Path().parent / ".venv-313"]


def main():
    parser = argparse.ArgumentParser(
        prog="Thesis benchmarking",
        description=(
            "Benchmark SymPy and python-flint on suite of tests with CPU and memory profiles as well as Mathematica."
        ),
        epilog="No one else should ever really be using this",
    )

    parser.add_argument(
        "--benchmark",
        dest="benchmark",
        action="store_true",
        default=False,
        help="Enable benchmarking",
    )

    parser.add_argument(
        "--cpu-profiling",
        dest="cpu",
        action="store_true",
        default=False,
        help="enable CPU profiling on the Python based libraries",
    )

    parser.add_argument(
        "--memory-profiling",
        dest="mem",
        action="store_true",
        default=False,
        help="enable memory profiling on the Python based libraries",
    )

    parser.add_argument(
        "--libraries",
        dest="libs",
        default=[x for v in harnesses.values() for x in v.keys()],
        choices=[x for v in harnesses.values() for x in v.keys()],
        help="libraries to benchmark",
        nargs="+",
    )

    parser.add_argument(
        "--venvs",
        dest="venvs",
        default=default_venvs,
        type=pathlib.Path,
        help="virtual enviroments to use for Python libraries",
        nargs="*",
    )

    args = parser.parse_args()

    python_libs = []
    external_libs = []
    for lib in args.libs:
        (python_libs if lib in harnesses["python"] else external_libs).append(lib)

    if len(args.venvs) == 0 and len(python_libs) != 0:
        raise ValueError("cannot run a python-based benchmark without at least one venv")
    elif len(args.venvs) != 0 and len(python_libs) == 0:
        raise ValueError("venv provided but no python libraries specified")

    venvs = []
    for venv in args.venvs:
        if not venv.exists():
            raise ValueError(f"venv does not exist ({venv})")
        elif not venv.is_dir():
            raise ValueError(f"venv is not a directory ({venv})")
        venvs.append(venv)

    logger.info(
        python_run_config_format.format(
            libs=", ".join(python_libs),
            cpu=args.cpu,
            mem=args.mem,
            venvs=[str(x.absolute()) for x in venvs],
        )
        if python_libs
        else "Running with no Python libraries."
    )
    logger.info(
        external_run_config_format.format(
            libs=", ".join(external_libs),
        )
        if external_libs
        else "Running with no external libraries."
    )

    for lib, venv in itertools.product(python_libs, venvs):
        runner = PythonRunner(
            virtual_env=venv,
            library=lib,
            run_list=[],
            benchmark=args.benchmark,
            cpu_profiling=args.cpu,
            mem_profiling=args.mem,
        )

        process = runner.run()
        logger.info(
            report_format.format(
                lib=runner.library,
                run_config=runner.run_config,
                venv=venv,
                stdout=process.stdout.strip(),
                stderr=process.stderr.strip(),
                flags=[],
            )
        )


def from_script():
    logging.basicConfig(level=logging.INFO)
    main()
