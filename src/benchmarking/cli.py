import argparse
import logging
import pathlib
from benchmarking.harness import harnesses
from benchmarking.runner import PythonRunSpec, ExternalRunSpec


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

    python_run_spec = PythonRunSpec(
        libs=python_libs,
        venvs=venvs,
        benchmark=args.benchmark,
        cpu=args.cpu,
        mem=args.mem,
        run_list=[]
    )

    external_run_spec = ExternalRunSpec(
        libs=external_libs,
        benchmark=args.benchmark,
        run_list=[]
    )

    python_run_spec.run()
    external_run_spec.run()


def gen_polys():
    pass


def from_script():
    logging.basicConfig(level=logging.INFO)
    main()
