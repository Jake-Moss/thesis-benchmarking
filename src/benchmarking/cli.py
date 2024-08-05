import argparse
import logging
import pathlib
import pickle
from benchmarking.harness import harnesses
from benchmarking.runner import PythonRunSpec, ExternalRunSpec
from benchmarking.gen_polys import PolynomialGenerator


default_venvs = [pathlib.Path().parent / ".venv-311", pathlib.Path().parent / ".venv-313"]


def main():
    parser = argparse.ArgumentParser(
        prog="benchmarking-cli",
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
        libs=python_libs, venvs=venvs, benchmark=args.benchmark, cpu=args.cpu, mem=args.mem, run_list=[], polys={},
    )

    external_run_spec = ExternalRunSpec(libs=external_libs, benchmark=args.benchmark, run_list=[])

    python_run_spec.run()
    external_run_spec.run()


def parse_ranges(range_str):
    """
    Example:
        >>> parse_ranges("1-3, 5, 7-9:2")
        [range(1, 4), range(5, 6), range(7, 10, 2)]
    """
    result = []
    parts = range_str.split(",")

    for part in parts:
        if "-" in part:
            if ":" in part:
                start, rest = part.split("-")
                end, step = rest.split(":")
                result.append(range(int(start), int(end), int(step)))
            else:
                start, end = part.split("-")
                result.append(range(int(start), int(end)))
        else:
            result.append(range(int(part), int(part) + 1))

    return result


def gen_polys():
    parser = argparse.ArgumentParser(
        prog="benchmarking-gen-polys",
        description=(
            "Generate polynomials for benchmarking. Will use the product of all range arguments. "
            "Options take range arguments i.e. '1-3, 5, 7-9:2' will be interpreted as [range(1, 4), range(5, 6), range(7, 10, 2)]"
        ),
        epilog="No one else should ever really be using this",
    )

    parser.add_argument(
        "output",
        default=pathlib.Path() / "output.pickle",
        type=pathlib.Path,
        help="pickle file to output the polynomials into",
    )

    parser.add_argument(
        "--generators",
        dest="gens",
        type=parse_ranges,
        help="range of the number of generators to use",
        required=True,
    )

    parser.add_argument(
        "--sparsity",
        dest="sparsity",
        type=parse_ranges,
        help="range of sparsities of the polynomial as an integer percentage (0 - 100) of all possible monomials",
        required=True,
    )

    parser.add_argument(
        "--coefficients",
        dest="coefficients",
        type=parse_ranges,
        help="range of coefficients of the polynomial, sampled uniformly",
        required=True,
    )

    parser.add_argument(
        "--exponents",
        dest="exponents",
        type=parse_ranges,
        help="range of exponents of the polynomial, sampled uniformly",
        required=True,
    )

    parser.add_argument(
        "--number",
        dest="number",
        type=int,
        default=10,
        help="number of polynomials to generate per combination, default is 10",
    )

    parser.add_argument(
        "--append",
        dest="append",
        action="store_true",
        default=False,
        help="append to the output file, default will overwrite existing file",
    )

    parser.add_argument(
        "--seed",
        dest="seed",
        type=int,
        default=False,
        help="seed provided to random.seed, default will not seed",
    )

    args = parser.parse_args()

    if args.append:
        with open(args.output, "rb") as f:
            existing = pickle.load(f)
    else:
        existing = {}

    generator = PolynomialGenerator(
        generators=args.gens,
        sparsity=args.sparsity,
        coefficients=args.coefficients,
        exponents=args.exponents,
        number=args.number,
        seed=args.seed,
    )

    generator.generate()

    with open(args.output, "wb") as f:
        pickle.dump((existing | generator.results), f)


def from_script():
    logging.basicConfig(level=logging.INFO)
    main()


def from_script_gen_poly():
    logging.basicConfig(level=logging.INFO)
    gen_polys()
