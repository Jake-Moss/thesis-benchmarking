import argparse
import logging
import pathlib
import pickle
import pandas as pd
import time
from datetime import datetime
import subprocess
import sys

sys.path.insert(0, str((pathlib.Path() / "src").absolute()))

from benchmarking.harness import harnesses
from benchmarking.runner import PythonRunSpec, ExternalRunSpec
from benchmarking.gen_polys import PolynomialGenerator


logger = logging.getLogger(__name__)
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
        "polys",
        default=pathlib.Path() / "polys.pickle",
        type=pathlib.Path,
        help="pickled polynomials to use",
    )

    parser.add_argument(
        "run_list",
        default=pathlib.Path() / "run_list.pickle",
        type=pathlib.Path,
        help="pickled run list, function name to polynomial key",
    )

    parser.add_argument(
        "output",
        default=pathlib.Path() / "results",
        type=pathlib.Path,
        help="output dir",
    )

    parser.add_argument(
        "--run_list_filter",
        default=None,
        nargs="*",
        help="function name to polynomial key, unset for all",
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
        default=[x for v in harnesses.values() for x in v.keys() if x != "dummy"],
        choices=[x for v in harnesses.values() for x in v.keys()],
        help="libraries to benchmark",
        nargs="+",
    )

    parser.add_argument(
        "--venvs",
        dest="venvs",
        default=[],
        type=pathlib.Path,
        help="virtual enviroments to use for Python libraries",
        nargs="*",
    )

    parser.add_argument(
        "--gc",
        dest="gc",
        default=[True],
        type=eval,
        help="gc enabled or not or both",
        nargs="+",
    )

    parser.add_argument(
        "--repeats",
        dest="repeats",
        default=3,
        type=int,
        help="number of repeats for benchmarking",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="count",
        default=0,
    )

    parser.add_argument(
        "--cores",
        dest="cores",
        type=int,
        default=4,
    )

    parser.add_argument(
        "--timeout",
        dest="timeout",
        type=int,
        default=30,
    )

    args = parser.parse_args()

    if args.verbose == 1:
        logging.basicConfig(level=logging.INFO)
    elif args.verbose >= 2:
        logging.basicConfig(level=logging.DEBUG)

    python_libs = []
    external_libs = []
    for lib in args.libs:
        (python_libs if lib in harnesses["python"] else external_libs).append(lib)

    if len(args.venvs) == 0 and len(python_libs) != 0:
        raise ValueError("cannot run a python-based benchmark without at least one venv")
    elif len(args.venvs) != 0 and len(python_libs) == 0:
        raise ValueError("venv provided but no python libraries specified")
    elif len(args.gc) > 2:
        raise ValueError("don't supply more than two gc options")

    venvs = []
    for venv in args.venvs:
        if not venv.exists():
            raise ValueError(f"venv does not exist ({venv})")
        elif not venv.is_dir():
            raise ValueError(f"venv is not a directory ({venv})")
        venvs.append(venv)

    with open(args.polys, "rb") as f:
        polys = pickle.load(f)

    with open(args.run_list, "rb") as f:
        run_list = pickle.load(f)

    if args.run_list_filter is not None:
        run_list = {k: run_list[k] for k in args.run_list_filter}

    output = args.output / ("results_" + str(datetime.now().replace(microsecond=0)).replace(" ", "_").replace(":", "-"))
    output.mkdir(parents=True)

    python_run_spec = PythonRunSpec(
        verbose=args.verbose,
        libs=python_libs,
        venvs=venvs,
        benchmark=args.benchmark,
        repeats=3,
        cpu=args.cpu,
        mem=args.mem,
        run_list=run_list,
        polys=polys,
        gc=args.gc,
        flags=[],
        output_dir=output,
        timeout=args.timeout,
    )

    external_run_spec = ExternalRunSpec(
        verbose=args.verbose,
        libs=external_libs,
        benchmark=args.benchmark,
        repeats=3,
        run_list=run_list,
        polys=polys,
        output_dir=output,
        timeout=args.timeout,
    )

    res = {}

    todo = []
    running = set()
    completed = []
    todo.extend(reversed(external_run_spec.runners))
    todo.extend(reversed(python_run_spec.runners))

    something_broke = False
    try:
        cores = min(args.cores, len(todo))
        while todo or running:
            if cores > 0 and todo and not something_broke:
                cores = cores - 1
                proc = todo.pop()
                proc.start()
                running.add(proc)
                continue

            for proc in running:
                time.sleep(0.5)
                if proc.process.poll() is not None:
                    cores = cores + 1
                    if proc.process.returncode == 0:
                        proc.collect()
                    else:
                        something_broke = True
                        logger.error(f"{proc.library} exited with code {proc.process.returncode}")
                    running.remove(proc)
                    completed.append(proc)
                    logger.info(f"{len(completed)}/{len(todo) + len(running) + len(completed)} completed. Currently running: {len(running)}")
                    break

    except KeyboardInterrupt as e:
        for proc in running:
            proc.process.terminate()
        raise e

    if not something_broke:
        res["python"] = [x.dump_dict() for x in python_run_spec.runners]
        res["external"] = [x.dump_dict() for x in external_run_spec.runners]

        with open(output / "results.pickle", "wb") as f:
            pickle.dump(res, f)

        print("Wrote results to:", str(output))
    else:
        logger.error("Something broke! Didn't collect results!")


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
                result.append(range(eval(start), eval(end), eval(step)))
            else:
                start, end = part.split("-")
                result.append(range(eval(start), eval(end)))
        else:
            result.append(range(eval(part), eval(part) + 1))

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
        default=pathlib.Path(),
        type=pathlib.Path,
        help="directory output the polynomials into",
    )

    parser.add_argument(
        "--generators",
        dest="gens",
        type=parse_ranges,
        help="range of the number of generators to use",
        default=parse_ranges("1-10"),
    )

    parser.add_argument(
        "--terms",
        dest="terms",
        type=parse_ranges,
        help="range of terms of the polynomial",
        default=parse_ranges("50"),
    )

    parser.add_argument(
        "--coefficients",
        dest="coefficients",
        type=parse_ranges,
        help="range of coefficients of the polynomial, sampled uniformly",
        default=parse_ranges("0-1000"),
    )

    parser.add_argument(
        "--exponents",
        dest="exponents",
        type=parse_ranges,
        help="range of exponents of the polynomial, sampled uniformly",
        default=parse_ranges("0-10,100-1000:101"),
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

    parser.add_argument(
        "--describe",
        dest="describe",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="count",
        default=0,
    )

    args = parser.parse_args()

    if args.verbose == 1:
        logging.basicConfig(level=logging.INFO)
    elif args.verbose >= 2:
        logging.basicConfig(level=logging.DEBUG)

    if args.describe:
        with open(args.output, "rb") as f:
            existing = pickle.load(f)

        df = PolynomialGenerator.parse_to_df(existing)
        print(df.to_string(max_rows=10, max_colwidth=20))

    else:
        if args.append:
            with open(args.output / "polys.pickle", "rb") as f:
                existing_polys = pickle.load(f)
            with open(args.output / "run_list.pickle", "rb") as f:
                existing_run_list = pickle.load(f)
        else:
            existing_polys = {}
            existing_run_list = {}

        generator = PolynomialGenerator(
            generators=args.gens,
            terms=args.terms,
            coefficients=args.coefficients,
            exponents=args.exponents,
            number=args.number,
            seed=args.seed,
        )

        generator.generate()

        merged = {
            k: existing_run_list.get(k, generator.run_list.get(k))
            for k in existing_run_list.keys() ^ generator.run_list.keys()
        }
        merged.update({
            k: existing_run_list[k] + generator.run_list[k]
            for k in existing_run_list.keys() & generator.run_list.keys()
        })

        with open(args.output / "polys.pickle", "wb") as f:
            pickle.dump((existing_polys | generator.results), f)

        with open(args.output / "run_list.pickle", "wb") as f:
            pickle.dump(merged, f)


def from_script():
    main()


def from_script_gen_poly():
    gen_polys()
