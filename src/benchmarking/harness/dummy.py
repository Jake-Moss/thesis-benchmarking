import pickle
import sys
from benchmarking.harness.generic import Benchmark, CPUProfile, MemoryProfile
from inspect import signature
import logging
import itertools

ID = {"dummy": {"file": __file__, "env": {}}}

logger = logging.getLogger(__name__)


class Dummy:
    def __init__(self, profilers: dict):
        self.profilers = profilers

    def run(self, repeats):
        self.results = {}
        for profiler_name, profiler in self.profilers.items():
            for name, func, args, poly_key in self.funcs:
                for idxs in itertools.combinations(range(len(self.poly_dict[poly_key])), args):
                    ps = tuple(self.poly_dict[poly_key][i] for i in idxs)
                    logger.debug(f"running {profiler} on {name} with arguments {ps}")
                    def f(func=func, ps=ps):
                        return func(*ps)
                    profiler.execute((name, poly_key, idxs), f, repeats=repeats)

            self.results[profiler_name] = profiler.results

    def generate_spec(self, run_list: dict, polys: dict):
        funcs = []
        for name in run_list:
            func = getattr(self, name)
            for k in polys.keys():
                funcs.append((name, func, len(signature(func).parameters), k))
        self.funcs = funcs

    def parse_polys(self, polys_collection: dict):
        self.poly_dict = polys_collection

    @staticmethod
    def merge(p1, p2):
        a = list(range(1000))
        a + list(p1 | p2) + list(p2 | p1)
        return p1 | p2


def main():
    stdin = pickle.load(sys.stdin.buffer)
    print("Received:", {k: v if k != "polys" else "..." for k, v in stdin.items()}, file=sys.stderr)

    repeats = stdin["repeats"]
    gc = stdin["gc"]

    if stdin["log_file"] is not None:
        logging.basicConfig(filename=stdin["log_file"], encoding='utf-8', level=logging.DEBUG)

    profilers = {}
    if stdin["benchmark"]:
        profilers["benchmark"] = Benchmark(repeats, gc)
    if stdin["cpu"]:
        profilers["cpu"] = CPUProfile(repeats, gc)
    if stdin["mem"]:
        profilers["mem"] = MemoryProfile(repeats, gc)

    d = Dummy(profilers)
    d.generate_spec(stdin["run_list"], stdin["polys"])
    d.parse_polys(stdin["polys"])
    d.run(stdin["repeats"])
    pickle.dump(d.results, sys.stdout.buffer)


if __name__ == "__main__":
    main()
