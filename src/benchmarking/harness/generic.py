import cProfile
import timeit
import abc
import tempfile
import gc
# import memray
import logging
import pickle
import sys


logger = logging.getLogger(__name__)


class Base:
    def __init__(self, repeats: int = 3, gc: bool = False):
        self.results = {}
        self.gc = gc

    def execute(name, func, repeats: int):
        pass

class Benchmark(Base):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setup = "gc.enable()" if self.gc else "pass"

    def execute(self, name, func, *, repeats: int):
        self.results[name] = timeit.repeat(stmt=func, setup=self.setup, repeat=repeats, number=1)


class CPUProfile(Base):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def execute(self, name, func, **_):
        # pr = cProfile.Profile()

        try:
            if not self.gc:
                gc.disable()
            sys.activate_stack_trampoline("perf")
            func()
        finally:
            sys.deactivate_stack_trampoline()
            if not self.gc:
                gc.enable()

        # f = tempfile.NamedTemporaryFile(suffix=".prof", delete=False)
        # pr.dump_stats(f.name)

        # self.results[name] = f.name


class MemoryProfile(Base):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def execute(self, name, func, **_):
        f = tempfile.NamedTemporaryFile(suffix=".memray", delete=False)
        try:
            if not self.gc:
                gc.disable()

            with memray.Tracker(destination=memray.FileDestination(f.name, overwrite=True)):
                func()
        finally:
            if not self.gc:
                gc.enable()

        self.results[name] = f.name


class Library(abc.ABC):
    def __init__(self, profilers: dict):
        self.profilers = profilers
        self.poly_dict = {}

    def run(self, run_list, repeats):
        self.results = {}
        for profiler_name, profiler in self.profilers.items():
            for name, poly_keys in run_list.items():
                for poly_key in poly_keys:
                    args = tuple(self.poly_dict[k] for k in poly_key)
                    logger.debug(f"running {type(profiler).__name__} on {name} with arguments {poly_key}")

                    func = getattr(self, name)
                    def foo(func=func, args=args):
                        return func(*args)

                    profiler.execute((name, poly_key), foo, repeats=repeats)

            self.results[profiler_name] = profiler.results

    @abc.abstractmethod
    def parse_polys(self, polys_collection: dict):
        pass

    @classmethod
    def main(cls):
        stdin = pickle.load(sys.stdin.buffer)
        print("Received:", {k: v if k != "polys" else "..." for k, v in stdin.items()}, file=sys.stderr)

        repeats = stdin["repeats"]
        gc_enabled = stdin["gc"]

        if stdin["log_file"] is not None:
            logging.basicConfig(filename=stdin["log_file"], encoding="utf-8", level=logging.DEBUG)

        profilers = {}
        if stdin["benchmark"]:
            profilers["benchmark"] = Benchmark(repeats, gc_enabled)

        if stdin["cpu"]:
            profilers["cpu"] = CPUProfile(repeats, gc_enabled)

        # if stdin["mem"]:
        #     profilers["mem"] = MemoryProfile(repeats, gc_enabled)

        d = cls(profilers)
        d.parse_polys(stdin["polys"])
        d.run(stdin["run_list"], repeats)
        pickle.dump(d.results, sys.stdout.buffer)

