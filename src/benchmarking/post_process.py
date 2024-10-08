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
    polys.index = polys.index.astype("category")

    res = pd.DataFrame(results["external"])
    res = pd.concat([res[["results", "flags"]], res.drop(columns=["results", "flags"]).astype("category")], axis=1)
    print(res.head())
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
    polys.index = polys.index.astype("category")

    res = pd.DataFrame(results["python"])
    res["venv"] = res["venv"].apply(str)
    res = pd.concat([res[["results", "flags"]], res.drop(columns=["results", "flags"]).astype("category")], axis=1)
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



# Fundementals



# bench_df, cpu_df, mem_df = load_results("results/results_2024-10-08_01-29-50/results.pickle")

# with open("./polys.pickle", "rb") as f:
#     polys = PolynomialGenerator.parse_to_df(pickle.load(f))

# coeff_map = dict((range(*k), v) for k, v in zip(polys["coeff_range"].unique().sort_values(), ["small coeff", "large coeff"]))
# exp_map = dict((range(*k), v) for k, v in zip(polys["exp_range"].unique().sort_values(), ["small exp", "large exp"]))

# bench_df["args"] = bench_df.args.apply(lambda args: tuple((x[0], x[1], exp_map[x[2]], coeff_map[x[3]]) for x in args))

# gb = bench_df.groupby(by=["library", "function", "args"], observed=True)
# bench_df = gb["timings"].min().reset_index()
# gb = bench_df.groupby("function")

# unary_functions = pd.concat([gb.get_group("factor"), gb.get_group("leading_coefficient")])
# binary_functions = pd.concat([gb.get_group(func) for func in ["add", "sub", "mult", "divmod", "gcd"]])

# unary_functions[["Generators", "Terms", "Exponent size", "Coefficient size"]] = unary_functions.args.apply(lambda x: x[0]).apply(pd.Series)
# unary_functions = unary_functions.drop(columns="args")


# sns_kwargs = {
#     "x": "function",
#     "y": "timings",
#     "hue": "library",
# }


# for k, df in unary_functions.groupby(["Exponent size", "Coefficient size"]):
#     pivot = df.pivot(index=["library", "Generators", "Terms"], columns="function", values="timings")
#     # ax = sns.heatmap(
#     #     pivot,
#     #     annot=True,
#     #     fmt=".1f",
#     #     vmin=0,
#     #     # vmax=(max_finite_normalised),
#     #     square=True,
#     #     xticklabels=True,
#     #     yticklabels=True,
#     #     cmap=cmap,
#     # )
#     # ax.set(xlabel="Polynomial System", ylabel="Factors of normalised time", title="Factors of normalised time")
#     # plt.tight_layout()
#     # plt.show()


#     facet = sns.FacetGrid(
#         pivot,
#         col="function",
#     )
#     facet.map_dataframe(
#         lambda *args, **kwargs: sns.heatmap(
#             pivot,
#             *args,
#             annot=True,
#             fmt=".1f",
#             vmin=0,
#             # vmax=(max_finite_normalised),
#             square=True,
#             xticklabels=True,
#             yticklabels=True,
#             cmap=cmap,
#             **kwargs
#         ),
#         **sns_kwargs
#     )
#     facet.add_legend()
#     facet.figure.suptitle("Time delta (s) from enabling garbage collection")
#     facet.set_ylabels("Relative time")
#     facet.set_xlabels("Polynomial system")
#     facet.set_titles(row_template="{row_name}")
#     facet.tight_layout()
#     facet.tick_params(axis="x", labelrotation=70)
#     plt.show()
#     break



# raise Exception()

### Groebner stuff


with open("polynomial_db/polys_df.pickle", "rb") as f:
    polys = pickle.load(f)

# mem_df["usage"] = mem_df["usage"].apply(lambda x: pd.DataFrame(x, columns=["function", "file", "total", "% total", "own", "% own", "allocations"]))
# mem_df["allocations"] = mem_df["usage"].apply(lambda x: x["allocations"].max())

bench_df, cpu_df, mem_df = load_python_results("results/results_2024-10-08_01-06-21/results.pickle")

external_res = load_external_results("results/results_2024-10-08_01-06-21/results.pickle")

groebner = bench_df.copy()[bench_df["function"] == "groebner"].drop(columns="function")
groebner["system"] = groebner["args"].apply(lambda x: x[0]).astype("category")
groebner = groebner.drop(columns="args")
groebner = groebner.set_index(["system", "library", "gc", "venv"]).sort_index()

groebner["dnf"] = groebner["timings"] == float("inf")


# groebner_mem = mem_df.copy().loc[mem_df["function"].apply(lambda x: x[0]).index]
# groebner_mem["system"] = groebner_mem["function"].apply(lambda x: x[1][0]).astype("category")
# groebner_mem = groebner_mem.drop(columns=["function"])
# groebner_mem = groebner_mem.set_index(["system", "library", "gc", "venv"]).sort_index()


gb = groebner.reset_index().groupby(["system", "gc", "venv"], observed=False)
groebner_with_finished = gb.filter(lambda x: not x["dnf"].all())
groebner_with_unfinished = gb.filter(lambda x: x["dnf"].any() and not x["dnf"].all())
groebner_unfinished_libraries = groebner_with_unfinished[groebner_with_unfinished["dnf"]].set_index(
    ["system", "gc", "venv"]
)["library"]
groebner = groebner_with_finished.drop(columns=["dnf"]).set_index(["system", "library", "gc", "venv"]).sort_index()


# groebner_mem_with_finished = groebner_with_finished.merge(
#     groebner_mem, left_on=["system", "library", "gc", "venv"], right_index=True, how="left"
# ).drop(columns="timings")

order = (
    groebner.merge(
        polys.reset_index().reset_index()[["index", "name"]].rename(columns={"name": "system"}),
        on="system",
        how="left",
        validate="many_to_one",
    )
    .sort_values(by="index")["system"]
    .unique()
)


res = []
gb = groebner.reset_index().groupby(by=["system", "gc", "venv"], observed=False)
for (k, df), m in zip(gb, gb.max(numeric_only=True).dropna()["timings"].values):
    df["timings"] /= m
    res.append(df)

groebner_normalised = pd.concat(res).set_index(["system", "library", "gc", "venv"]).sort_index()
del res

max_finite = groebner_with_finished["timings"][groebner_with_finished["timings"] != float("inf")].max()
max_finite_normalised = groebner_normalised["timings"][groebner_normalised["timings"] != float("inf")].max()
# groebner_normalised["timings"] = groebner_normalised["timings"].apply(lambda x: 2 * max_finite_normalised if x == float("inf") else x )

sns_kwargs = {
    "x": "system",
    "y": "timings",
    "hue": "library",
    "order": order,
}

# g = sns.barplot(groebner_with_finished.groupby(["system", "library"], observed=False).min(numeric_only=True).dropna().drop(columns="dnf").reset_index(), y="timings", legend=True)
# g.figure.suptitle("Time (s) to construct reduced Gröbner basis")
# g.set_ylabel("Factors of fastest")
# g.set_xlabel("Polynomial system")
# g.tick_params(axis="x", labelrotation=70)
# plt.tight_layout()
# plt.show()

# g = sns.FacetGrid(
#     groebner_with_finished.reset_index(),
#     col="gc",
#     row="venv",
#     aspect=4 / 3,
# )
# g.map_dataframe(sns.barplot, **sns_kwargs)
# g.add_legend()
# g.figure.suptitle("Time (s) to construct reduced Gröbner basis")
# g.set_ylabels("Factors of fastest")
# g.set_xlabels("Polynomial system")
# g.set_titles(row_template="{row_name}")
# g.tight_layout()
# g.tick_params(axis="x", labelrotation=70)
# # g.set(ylim=(0, max_finite_normalised * 1.1))
# plt.show()

gc_diff = (groebner.loc[:, :, True, :] - groebner.loc[:, :, False, :]) / groebner.loc[:, :, False, :]
gc_facet = sns.FacetGrid(
    gc_diff.reset_index(),
    col="venv",
)
gc_facet.map_dataframe(sns.barplot, **sns_kwargs)
gc_facet.add_legend()
gc_facet.figure.suptitle("Time delta (s) from enabling garbage collection")
gc_facet.set_ylabels("Relative time")
gc_facet.set_xlabels("Polynomial system")
gc_facet.set_titles(row_template="{row_name}")
gc_facet.tight_layout()
gc_facet.tick_params(axis="x", labelrotation=70)
plt.show()


version_diff = (groebner.loc[:, :, :, "3.13.0rc1"] - groebner.loc[:, :, :, "3.12.4"]) / groebner.loc[:, :, :, "3.12.4"]
version_facet = sns.FacetGrid(
    version_diff.reset_index(),
    col="gc",
)
version_facet.map_dataframe(sns.barplot, **sns_kwargs)
version_facet.add_legend()
version_facet.figure.suptitle("Time delta (s) from 3.13.0rc to 3.12.4")
version_facet.set_ylabels("Relative time")
version_facet.set_xlabels("Polynomial system")
version_facet.set_titles(row_template="{row_name}")
version_facet.tight_layout()
version_facet.tick_params(axis="x", labelrotation=70)
plt.show()

groebner_mean = groebner_normalised.groupby(by=["library"], observed=False).mean(numeric_only=True)
g = sns.barplot(groebner_mean.reset_index(), x="library", y="timings", hue="library", palette="flare", legend=True)
g.figure.suptitle("Mean relative runtime to construct reduced Gröbner basis")
g.set_ylabel("Mean relative runtime")
g.set_xlabel("Polynomial system")
g.tick_params(axis="x", labelrotation=70)
plt.tight_layout()
plt.show()


pivot = groebner_normalised.reset_index().pivot(index=["library", "venv", "gc"], columns="system", values="timings")[
    order
]
ax = sns.heatmap(
    pivot,
    annot=True,
    fmt=".1f",
    vmin=0,
    vmax=(max_finite_normalised),
    square=True,
    xticklabels=True,
    yticklabels=True,
    cmap=cmap,
)
ax.set(xlabel="Polynomial System", ylabel="Factors of normalised time", title="Factors of normalised time")
plt.tight_layout()
plt.show()

groebner_normalised_pivot = (
    groebner_normalised.groupby(["system", "library"], observed=False)
    .min(numeric_only=True)
    .dropna()
    .reset_index()
    .pivot(index="library", columns="system", values="timings")[order]
)
ax = sns.heatmap(
    groebner_normalised_pivot,
    annot=True,
    fmt=".1f",
    vmin=0,
    vmax=(max_finite_normalised),
    square=True,
    xticklabels=True,
    yticklabels=True,
    cmap=cmap,
)
ax.set(xlabel="Polynomial System", ylabel="Factors of normalised time", title="Minimum factors of normalised time")
plt.tight_layout()
plt.show()


pivot = groebner_mem_with_finished.pivot(index=["library", "venv", "gc"], columns="system", values="max_bytes")[
    order
].map(math.log)
ax = sns.heatmap(pivot, vmin=0, square=True, xticklabels=True, yticklabels=True, cmap=cmap)
ax.set(xlabel="Polynomial System", ylabel="Library", title="log(Max total bytes allocated)")
plt.tight_layout()
plt.show()

pivot = (
    groebner_mem_with_finished.groupby(["system", "library"], observed=False)
    .max(numeric_only=True)
    .dropna()
    .reset_index()
    .pivot(index="library", columns="system", values="max_bytes")
    .map(math.log)[order]
)
ax = sns.heatmap(pivot, vmin=0, square=True, xticklabels=True, yticklabels=True, cmap=cmap)
ax.set(xlabel="Polynomial System", ylabel="Library", title="log(Max total bytes allocated)")
plt.tight_layout()
plt.show()


# groebner_mem = mem_df.copy().iloc[mem_df["function"].apply(lambda x: x[0]).index]
# groebner_mem["system"] = groebner_mem["function"].apply(lambda x: x[1][0]).astype("category")
# groebner_mem = groebner_mem.drop(columns=["function", "usage"])
# groebner_mem = groebner_mem.groupby(by=["library", "system"]).mean(numeric_only=True)
