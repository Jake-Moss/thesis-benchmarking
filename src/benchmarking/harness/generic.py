import cProfile
import timeit
import abc
import tempfile
import gc
# import memray
import logging
import pickle
import sys
import multiprocessing
import queue


logger = logging.getLogger(__name__)


class Base:
    def __init__(self, repeats: int = 3, gc: bool = False, timeout: int = 30):
        self.results = {}
        self.gc = gc
        self.timeout = timeout
        self.setup = "gc.enable()" if self.gc else "pass"

    def run(func=None, **_):
        def foo(queue):
            func()
            queue.put(1)
        return foo

    def execute(self, name, func, **kwargs):
        try:
            q = multiprocessing.Queue()
            p = multiprocessing.Process(target=self.run(func, **kwargs), args=(q,))
            p.start()
            self.results[name] = q.get(block=True, timeout=self.timeout)
        except queue.Empty:
            self.results[name] = "timeout"
            logger.error(f"timed out on {name} after {self.timeout}s")
            p.terminate()
            p.join()
        finally:
            q.close()


class Benchmark(Base):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, func, *, repeats: int):
        def foo(queue):
            queue.put(timeit.repeat(stmt=func, setup=self.setup, repeat=repeats, number=1))
        return foo


class CPUProfile(Base):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, func=None, **_):
        def foo(queue):
            sys.activate_stack_trampoline("perf")
            queue.put(timeit.repeat(stmt=func, setup=self.setup, repeat=1, number=1))
            sys.deactivate_stack_trampoline()
        return foo


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
    def __init__(self, profiler: dict):
        self.profiler = profiler
        self.poly_dict = {}

    def run(self, run_list, repeats):
        self.results = {}
        for name, poly_keys in run_list.items():
            for poly_key in poly_keys:
                args = tuple(self.poly_dict[k] for k in poly_key)
                logger.debug(f"running {type(self.profiler).__name__} on {name} with arguments {poly_key}")

                func = getattr(self, name)
                def foo(func=func, args=args):
                    return func(*args)

                self.profiler.execute((name, poly_key), foo, repeats=repeats)

        self.results = self.profiler.results

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

        profiler = None
        if stdin["type"] == "benchmark":
            profiler = Benchmark(repeats, gc_enabled)
        elif stdin["type"] == "cpu":
            profiler = CPUProfile(repeats, gc_enabled)
        elif stdin["type"] == "mem":
            profiler = MemoryProfile(repeats, gc_enabled)

        d = cls(profiler)
        d.parse_polys(stdin["polys"])
        d.run(stdin["run_list"], repeats)
        pickle.dump(d.results, sys.stdout.buffer)

