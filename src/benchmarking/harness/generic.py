import timeit
import abc
import logging
import pickle
import multiprocessing as mp
import sys
import functools
import queue


logger = logging.getLogger(__name__)


def _run(func, setup, repeats, q):
    q.put(timeit.repeat(stmt=func, setup=setup, repeat=repeats, number=1))


class Executor:
    def __init__(self, repeats: int = 3, gc: bool = False, timeout: int = 30):
        self.results = {}
        self.gc = gc
        self.timeout = timeout
        self.setup = "gc.enable()" if self.gc else "pass"
        self.repeats = repeats
        self.run = _run

    def execute(self, name, func):
        q = mp.Queue()
        try:
            p = mp.Process(target=self.run, args=(func, self.setup, self.repeats, q))
            p.start()
            self.results[name] = q.get(timeout=self.timeout)
        except queue.Empty:
            self.results[name] = [float("inf")]
            logger.error(f"timed out on {name} after {self.timeout}s")
        finally:
            p.terminate()
            q.close()


class Library(abc.ABC):
    def __init__(self, profiler: dict):
        self.profiler = profiler
        self.poly_dict = {}

    def run(self, run_list):
        self.results = {}
        for name, poly_keys in run_list.items():
            for poly_key in poly_keys:
                args = tuple(self.poly_dict[k] for k in poly_key)
                logger.debug(f"running {type(self.profiler).__name__} on {name} with arguments {poly_key}")

                func = getattr(self, name)
                foo = functools.partial(func, *args)

                self.profiler.execute((name, poly_key), foo)

        self.results = self.profiler.results

    @abc.abstractmethod
    def parse_polys(self, polys_collection: dict):
        pass

    @classmethod
    def main(cls):
        mp.set_start_method('fork')
        stdin = pickle.load(sys.stdin.buffer)
        print("Received:", {k: v if k != "polys" else "..." for k, v in stdin.items()}, file=sys.stderr)

        repeats = stdin["repeats"]
        gc_enabled = stdin["gc"]

        if stdin["log_file"] is not None:
            logging.basicConfig(filename=stdin["log_file"], encoding="utf-8", level=logging.DEBUG)

        if stdin["type"] != "benchmark":
            repeats = 1

        profiler = Executor(repeats, gc_enabled)

        d = cls(profiler)
        d.parse_polys(stdin["polys"])
        d.run(stdin["run_list"])
        pickle.dump(d.results, sys.stdout.buffer)
