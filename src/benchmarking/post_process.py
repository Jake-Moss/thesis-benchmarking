import pandas as pd
import pickle
import matplotlib.pyplot as plt
from matplotlib import colormaps
import seaborn as sns
import math
from src.benchmarking.gen_polys import PolynomialGenerator


sns.set_theme("notebook", font_scale=1, rc={'figure.figsize': (8, 6)})
cmap = colormaps["binary"]


# with open("small_int_benchmark.txt") as f:
#     flint_timings = []
#     gmp_timings = []
#     flint_timings_vec = []
#     gmp_timings_vec = []

#     for (a, b, c, d) in itertools.batched((eval(x) for x in f.read().split("\n") if x), 4):
#         flint_timings.append(a)
#         gmp_timings.append(b)
#         flint_timings_vec.append(c)
#         gmp_timings_vec.append(d)

#     n = len(flint_timings)
#     flint_timings = [sum(x) / n for x in zip(*flint_timings)]
#     gmp_timings = [sum(x) / n for x in zip(*gmp_timings)]
#     flint_timings_vec = [sum(x) / n for x in zip(*flint_timings_vec)]
#     gmp_timings_vec = [sum(x) / n for x in zip(*gmp_timings_vec)]

# with open("small_int_benchmark_cython.txt") as f:
#     cython_timings = []
#     cython_timings_vec = []

#     for (a, b) in itertools.batched((eval(x) for x in f.read().split("\n") if x), 2):
#         cython_timings.append(a)
#         cython_timings_vec.append(b)

#     n = len(cython_timings)
#     cython_timings = [sum(x) / n for x in zip(*cython_timings)]
#     cython_timings_vec = [sum(x) / n for x in zip(*cython_timings_vec)]

# x = list(range(1, len(flint_timings) + 1))
# # Oscillations might be context switches on CPU
# f, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
# sns.lineplot(x=x, y=flint_timings, ax=ax2, label="FLINT")
# sns.lineplot(x=x, y=gmp_timings, ax=ax2, label="GMP")
# sns.lineplot(x=x, y=cython_timings, ax=ax2, label="Python")
# sns.lineplot(x=x, y=flint_timings_vec, ax=ax1, label="FLINT vector[1000]")
# sns.lineplot(x=x, y=gmp_timings_vec, ax=ax1, label="GMP vector[1000]")
# sns.lineplot(x=x, y=cython_timings_vec, ax=ax1, label="Python vector[1000]")
# ax1.set_yscale('log')
# ax2.set_yscale('log')
# f.supxlabel('Number of multiplications by 2')
# f.supylabel('Reference cycles')
# f.suptitle('Reference cycles to execute repeated multiplications by 2 (stalled and memory fenced)')
# plt.tight_layout()
# plt.savefig('images/small_int_benchmark.pdf', dpi=300, bbox_inches='tight')
# plt.show()

# n = 62 * 2
# f, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
# sns.lineplot(x=x[:n], y=flint_timings[:n], ax=ax2, label="FLINT")
# sns.lineplot(x=x[:n], y=gmp_timings[:n], ax=ax2, label="GMP")
# sns.lineplot(x=x[:n], y=cython_timings[:n], ax=ax2, label="Python")
# sns.lineplot(x=x[:n], y=flint_timings_vec[:n], ax=ax1, label="FLINT vector[1000]")
# sns.lineplot(x=x[:n], y=gmp_timings_vec[:n], ax=ax1, label="GMP vector[1000]")
# sns.lineplot(x=x[:n], y=cython_timings_vec[:n], ax=ax1, label="Python vector[1000]")
# ax1.set_yscale('log')
# ax2.set_yscale('log')
# f.supxlabel('Number of multiplications by 2')
# f.supylabel('Reference cycles')
# f.suptitle('Reference cycles to execute repeated multiplications by 2 (stalled and memory fenced)')
# plt.tight_layout()
# plt.savefig('images/small_int_benchmark_focused.pdf', dpi=300, bbox_inches='tight')
# plt.show()


# f, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
# sns.lineplot(x=x, y=[x / y for x, y in zip(flint_timings, gmp_timings)], ax=ax2, label="FLINT / GMP")
# sns.lineplot(x=x, y=[x / y for x, y in zip(flint_timings_vec, gmp_timings_vec)], ax=ax1, label="FLINT / GMP vector[1000]")
# f.supxlabel('Number of multiplications by 2')
# f.supylabel('Ratio of reference cycles')
# f.suptitle('Ratio of reference cycles to execute repeated multiplications by 2 (stalled and memory fenced)')
# plt.tight_layout()
# plt.savefig('images/small_int_benchmark_ratio.pdf', dpi=300, bbox_inches='tight')
# plt.show()

# f, (ax1, ax2) = plt.subplots(2, 1, sharex=True)
# sns.lineplot(x=x[:n], y=[x / y for x, y in zip(flint_timings[:n], gmp_timings[:n])], ax=ax2, label="FLINT / GMP")
# sns.lineplot(x=x[:n], y=[x / y for x, y in zip(flint_timings_vec[:n], gmp_timings_vec[:])], ax=ax1, label="FLINT / GMP vector[1000]")
# f.supxlabel('Number of multiplications by 2')
# f.supylabel('Ratio of reference cycles')
# f.suptitle('Ratio of reference cycles to execute repeated multiplications by 2 (stalled and memory fenced)')
# plt.tight_layout()
# plt.savefig('images/small_int_benchmark_ratio_focused.pdf', dpi=300, bbox_inches='tight')
# plt.show()


# raise Exception()

def load_external_results(path):
    with open(path, "rb") as f:
        results = pickle.load(f)

    res = pd.DataFrame(results["external"])
    res = pd.concat([res[["results", "flags"]], res.drop(columns=["results", "flags"]).astype("category")], axis=1)
    gb = res.groupby(by="type", observed=False)

    try:
        bench_df = gb.get_group("benchmark")
        bench_df = bench_df.drop(columns=["type"])

        bench_df["function"] = bench_df["results"].apply(dict.keys)
        tmp = bench_df.explode("function")
        tmp["timings"] = bench_df["results"].apply(dict.values).explode()
        tmp["timings"] = tmp["timings"].apply(min)
        tmp = tmp.drop(columns=["results", "flags"])
        tmp["args"] = tmp.function.apply(lambda x: x[1])
        tmp["function"] = tmp.function.apply(lambda x: x[0])
        bench_df = tmp.reset_index(drop=True)
        # bench_df = bench_df[bench_df["timings"] != float("inf")]
        del tmp
    except KeyError:
        bench_df = pd.DataFrame()

    return bench_df

def load_python_results(path):
    with open(path, "rb") as f:
        results = pickle.load(f)

    res = pd.DataFrame(results["python"])
    res["venv"] = res["venv"].apply(str)
    res = pd.concat([res[["results", "flags", "gc"]], res.drop(columns=["results", "flags", "gc"]).astype("category")], axis=1)
    res["venv"] = res["venv"].map({".venv-312": "3.12.4", ".venv-313": "3.13.0rc1"})
    gb = res.groupby(by="type", observed=False)

    try:
        bench_df = gb.get_group("benchmark")
        bench_df = bench_df.drop(columns=["type"])

        bench_df["function"] = bench_df["results"].apply(dict.keys)
        tmp = bench_df.explode("function")
        tmp["timings"] = bench_df["results"].apply(dict.values).explode()
        tmp["timings"] = tmp["timings"].apply(min)
        tmp = tmp.drop(columns=["results", "flags"])
        tmp["args"] = tmp.function.apply(lambda x: x[1])
        tmp["function"] = tmp.function.apply(lambda x: x[0])
        bench_df = tmp.reset_index(drop=True)
        # bench_df = bench_df[bench_df["timings"] != float("inf")]
        del tmp
    except KeyError:
        bench_df = pd.DataFrame()

    try:
        cpu_df = gb.get_group("cpu")
        cpu_df = cpu_df.drop(columns=["type"])
    except KeyError:
        cpu_df = pd.DataFrame()

    try:
        mem_df = gb.get_group("mem")
        mem_df = mem_df.drop(columns=["type"])

        mem_df = mem_df.dropna().copy()
        mem_df["function"] = mem_df["results"].apply(dict.keys)
        tmp = mem_df.explode("function")
        tmp["usage"] = mem_df["results"].apply(dict.values).explode()
        tmp = tmp.drop(columns=["results", "flags"])
        mem_df = tmp.reset_index(drop=True)
        mem_df["max_allocations"] = mem_df["usage"].apply(lambda x: max(y[6] for y in x))
        mem_df["max_bytes"] = mem_df["usage"].apply(lambda x: max(y[2] for y in x))
        mem_df = mem_df.drop(columns="usage")
        del tmp
    except KeyError:
        mem_df = pd.DataFrame()

    return bench_df, cpu_df, mem_df

