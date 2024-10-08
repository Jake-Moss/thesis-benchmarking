import timeit
import abc
import logging
import pickle
import multiprocessing as mp
import functools
import queue
import tempfile
import fileinput

logger = logging.getLogger(__name__)


def _run(func, setup, repeats, q):
    q.put(timeit.repeat(stmt=func, setup=setup, repeat=repeats, number=1))


def _run_memray(func, setup, repeats, q, file):
    import memray
    import time

    dest = memray.FileDestination(file, overwrite=True)
    before = time.perf_counter_ns()

    with memray.Tracker(
        destination=dest,
        native_traces=True,
        trace_python_allocators=True,
        file_format=memray.FileFormat.ALL_ALLOCATIONS,
    ):
        func()

    after = time.perf_counter_ns()
    q.put((after - before) / 10e9)


def _run_mathematica(func, setup, repeats):
    return timeit.repeat(stmt=func, setup=setup, repeat=repeats, number=1)


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
            p.terminate()
        finally:
            logger.info(f"joining pid: {p.pid}")
            p.join()
            q.close()


class MemrayExecutor(Executor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run = _run_memray

    def execute(self, name, func):
        from memray import FileReader
        from memray.reporters.summary import SummaryReporter
        import os

        q = mp.Queue()

        with tempfile.NamedTemporaryFile(suffix=".bin") as file:
            try:
                p = mp.Process(target=self.run, args=(func, self.setup, self.repeats, q, file.name))
                p.start()
                q.get(timeout=self.timeout)
            except queue.Empty:
                logger.error(f"timed out on {name} after {self.timeout}s")
                p.terminate()
            finally:
                logger.info(f"joining pid: {p.pid}")
                p.join()
                q.close()

            logger.info("starting memray processing")
            # Below section is canalised from
            # https://github.com/bloomberg/memray/blob/58adb8677ddece233ec61bab0d72611d9a08c906/src/memray/reporters/summary.py#L64
            # on 26/Aug/2024
            reader = FileReader(os.fspath(file.name), report_progress=False)
            logger.info("read file")
            snapshot = iter(
                reader.get_temporary_allocation_records(
                    threshold=1,
                    merge_threads=False,
                )
            )
            logger.info("created snapshot")

            reporter = SummaryReporter.from_snapshot(
                snapshot,
                native=reader.metadata.has_native_traces,
            )
            logger.info("created reporter")

            sorted_allocations = sorted(
                reporter.snapshot_data.items(),
                key=lambda item: getattr(item[1], "n_allocations"),
                reverse=True,
            )
            logger.info(f"sorted {len(reporter.snapshot_data)} allocations")

            res = []
            logger.info("building results")
            for location, result in sorted_allocations:
                percent_total = result.total_memory / reporter.current_memory_size * 100
                percent_own = result.own_memory / reporter.current_memory_size * 100

                res.append(
                    (
                        location.function,
                        location.file,
                        result.total_memory,
                        percent_total,
                        result.own_memory,
                        percent_own,
                        result.n_allocations,
                    )
                )

            self.results[name] = res
            logger.info("finished memray processing")


class MathematicaExecutor(Executor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run = _run_mathematica

    def execute(self, name, func):
        from sage.all import alarm
        import cysignals
        try:
            alarm(self.timeout)
            self.results[name] = self.run(func, self.setup, self.repeats)
            logger.info("finished in time")
        except (cysignals.signals.AlarmInterrupt, KeyboardInterrupt):
            self.results[name] = [float("inf")]
            logger.error(f"timed out on {name} after {self.timeout}s")


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
    def main(cls, Executor_cls=Executor):
        run_config_file, results_file = (line.rstrip("\n") for line in fileinput.input())

        with open(run_config_file, "rb") as f:
            stdin = pickle.load(f)

        repeats = stdin["repeats"]
        gc_enabled = stdin["gc"]

        if stdin["log_file"] is not None:
            logging.basicConfig(
                handlers=[
                    logging.FileHandler(stdin["log_file"]),
                    # logging.StreamHandler()
                ],
                encoding="utf-8",
                level=logging.DEBUG
            )

        logging.info(f"Run config file: {run_config_file}")
        logging.info(f"Results file: {results_file}")

        if stdin["type"] != "benchmark":
            repeats = 1

        timeout = stdin["timeout"]

        if stdin["type"] == "mem":
            profiler = MemrayExecutor(repeats, gc_enabled, timeout)
        else:
            profiler = Executor_cls(repeats, gc_enabled, timeout)

        d = cls(profiler)
        d.parse_polys(stdin["polys"])
        logger.info(f"finished parsing, running {type(profiler).__name__}")
        d.run(stdin["run_list"])
        logger.info(f"finished running, dumping results to {results_file}")
        with open(results_file, "wb") as f:
            pickle.dump(d.results, f)
        logger.info("dumped, exiting")
