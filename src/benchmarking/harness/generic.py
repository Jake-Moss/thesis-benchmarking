import cProfile
import tracemalloc  # NOTE: check that this import doesn't slow things down
import timeit
import abc
import tempfile
import gc
import sys


class Base(abc.ABC):
    def __init__(self, repeats: int = 3, gc: bool = False):
        self.results = {}
        self.gc = gc

    @abc.abstractmethod
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

    def execute(self, name, func, repeats: int):
        pr = cProfile.Profile()

        try:
            if not self.gc:
                gc.disable()
            pr.enable()
            for _ in range(repeats):
                func()
            pr.disable()
        finally:
            if not self.gc:
                gc.enable()

        f = tempfile.NamedTemporaryFile(suffix=".prof", delete=False)
        pr.dump_stats(f.name)

        self.results[name] = f.name


class MemoryProfile(Base):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # tracemalloc.start(65535)

    def execute(self, name, func, repeats: int):

        try:
            if not self.gc:
                gc.disable()
            # tracemalloc.clear_traces()
            tracemalloc.start(1000)

            for _ in range(repeats):
                func()
        finally:
            snapshot = tracemalloc.take_snapshot()
            tracemalloc.stop()
            if not self.gc:
                gc.enable()

        f = tempfile.NamedTemporaryFile(suffix=".tracemalloc", delete=False)
        snapshot.dump(f.name)
        print(f.name, file=sys.stderr)
        print(*snapshot.statistics("traceback")[:10], sep="\n", file=sys.stderr)
        self.results[name] = f.name
