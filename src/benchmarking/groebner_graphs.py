import pandas as pd
import pickle
import matplotlib.pyplot as plt
from matplotlib import colormaps
import seaborn as sns
import math
import numpy as np
import itertools
from benchmarking.gen_polys import PolynomialGenerator
from benchmarking.post_process import load_python_results, load_external_results


sns.set_theme("notebook", font_scale=1, rc={
    'figure.figsize': (8, 6),
    "text.usetex": True,
    # "text.latex.preamble": r"\usepackage{libertine}",
    # "text.latex.preamble": "",
    'font.family': 'serif',
})

cmap = colormaps["inferno_r"]

### Groebner stuff


with open("polynomial_db/polys_df.pickle", "rb") as f:
    polys = pickle.load(f)
polys.index = polys.index.astype("category")

# bench_df, cpu_df, mem_df = load_python_results("results/results_2024-10-09_11-16-51/results.pickle")
# bench_df, cpu_df, mem_df = load_python_results("results/results_2024-11-01_11-53-13/results.pickle")
bench_df, cpu_df, mem_df = load_python_results("results/results_2024-11-02_21-42-02/results.pickle")

# external_groebner = load_external_results("results/results_2024-10-09_11-16-51/results.pickle")
external_groebner = load_external_results("results/results_2024-11-01_11-53-13/results.pickle")
external_groebner = external_groebner.drop(columns=["gc", "venv"])
external_groebner["system"] = external_groebner["args"].apply(lambda x: x[0]).astype("category")
external_groebner = external_groebner.drop(columns=["function", "args"])
external_groebner = external_groebner.set_index(["system", "library"]).sort_index()

groebner = bench_df.copy()[bench_df["function"] == "groebner"].drop(columns="function")
groebner["system"] = groebner["args"].apply(lambda x: x[0]).astype("category")
groebner = groebner.drop(columns="args")
groebner = groebner.set_index(["system", "library", "gc", "venv"]).sort_index()



groebner["dnf"] = groebner["timings"] == float("inf")
external_groebner["dnf"] = external_groebner["timings"] == float("inf")

gb = groebner.reset_index().groupby(["system", "gc", "venv"], observed=False)
groebner_with_finished = gb.filter(lambda x: not x["dnf"].all())
groebner_with_unfinished = gb.filter(lambda x: x["dnf"].any() and not x["dnf"].all())
groebner_unfinished_libraries = groebner_with_unfinished[groebner_with_unfinished["dnf"]].set_index(
    ["system", "gc", "venv"]
)["library"]
groebner = groebner_with_finished.drop(columns=["dnf"]).set_index(["system", "library", "gc", "venv"]).sort_index()

gb = external_groebner.reset_index().groupby(["system"], observed=False)
external_groebner_with_finished = gb.filter(lambda x: not x["dnf"].all())
external_groebner_with_unfinished = gb.filter(lambda x: x["dnf"].any() and not x["dnf"].all())
external_groebner_unfinished_libraries = external_groebner_with_unfinished[external_groebner_with_unfinished["dnf"]].set_index(
    ["system"]
)["library"]
external_groebner = external_groebner_with_finished.drop(columns=["dnf"]).set_index(["system", "library"]).sort_index()

merged_groebner = pd.concat([groebner.reset_index(), external_groebner.reset_index()], axis=0).set_index(groebner.index.names)
merged_groebner = merged_groebner.groupby(by=["system", "library"], observed=True).min()

# merged_groebner = merged_groebner.reset_index()[merged_groebner.reset_index()["library"] != "mathematica"].set_index(["system", "library"]).sort_index()


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

merged_pivot = merged_groebner.reset_index().pivot(index="library", columns="system", values="timings")[order]
merged_max = merged_pivot.replace(float("inf"), float("NaN")).max()
merged_min = merged_pivot.min()

max_labels = pd.concat([merged_pivot.replace(float("inf"), float("NaN")).idxmax(), merged_pivot.replace(float("inf"), float("NaN")).max()], axis=1).reset_index()
max_labels.columns = ["system", "library", "timings"]
max_labels = max_labels.set_index(["system", "library"])
max_labels = merged_groebner.drop(columns="timings").join(max_labels, how="left")
max_labels["timings"] = max_labels["timings"].apply(lambda x: "{:.1f}".format(x) if np.isfinite(x) else "")
max_labels = max_labels.reset_index().pivot(index="library", columns="system", values="timings")[order]


res = []
gb = groebner.reset_index().groupby(by=["system", "gc", "venv"], observed=True)
for (k, df), m in zip(gb, gb.max(numeric_only=True).dropna()["timings"].values):
    df["timings"] /= m
    res.append(df)

groebner_normalised = pd.concat(res).set_index(["system", "library", "gc", "venv"]).sort_index()
del res

res = []
gb = merged_groebner.reset_index().groupby(by=["system"], observed=True)
for (k, df), m in zip(gb, gb.max(numeric_only=True).dropna()["timings"].values):
    df["timings"] /= m
    res.append(df)

merged_groebner_normalised = pd.concat(res).set_index(["system", "library"]).sort_index()
del res


max_finite = groebner_with_finished["timings"][groebner_with_finished["timings"] != float("inf")].max()
max_finite_normalised = groebner_normalised["timings"][groebner_normalised["timings"] != float("inf")].max()

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



# gc_diff = (groebner.loc[:, :, True, :] - groebner.loc[:, :, False, :]) / groebner.loc[:, :, False, :]
# gc_facet = sns.FacetGrid(
#     gc_diff.reset_index(),
#     col="venv",
# )
# gc_facet.map_dataframe(sns.barplot, **sns_kwargs)
# gc_facet.add_legend()
# gc_facet.figure.suptitle("Time delta (s) from enabling garbage collection")
# gc_facet.set_ylabels("Relative time")
# gc_facet.set_xlabels("Polynomial system")
# gc_facet.set_titles(row_template="{row_name}")
# gc_facet.tight_layout()
# gc_facet.tick_params(axis="x", labelrotation=70)
# plt.show()


# version_diff = (groebner.loc[:, :, :, "3.13.0rc1"] / groebner.loc[:, :, :, "3.12.4"]) - 1.0
# version_facet = sns.FacetGrid(
#     version_diff.reset_index(),
#     col="gc",
# )
# version_facet.map_dataframe(sns.barplot, **sns_kwargs)
# version_facet.add_legend()
# version_facet.figure.suptitle("Time delta (s) from 3.12.4 to 3.13.0rc")
# version_facet.set_ylabels("Relative time")
# version_facet.set_xlabels("Polynomial system")
# version_facet.set_titles(row_template="{row_name}")
# version_facet.tight_layout()
# version_facet.tick_params(axis="x", labelrotation=70)
# version_facet.set_yticklabels(version_facet.axes[0][0].get_yticks() + 1.0)
# plt.show()



# pivot = groebner_normalised.reset_index().pivot(index=["library", "venv", "gc"], columns="system", values="timings")[
#     order
# ]
# ax = sns.heatmap(
#     pivot,
#     annot=True,
#     fmt=".1f",
#     vmin=0,
#     vmax=(max_finite_normalised),
#     square=True,
#     xticklabels=True,
#     yticklabels=True,
#     cmap=cmap,
# )
# ax.set(xlabel="Polynomial System", ylabel="Factors of normalised time", title="Factors of normalised time")
# plt.tight_layout()
# plt.show()

pivot = (merged_pivot / merged_max)
pivot = pd.concat([pivot.drop("mathematica"), pivot.loc[["mathematica"]]])

fig = plt.figure(figsize=(8, 3))
ax = fig.add_subplot()
sns.heatmap(
    pivot,
    # annot=max_labels,
    fmt="",
    vmin=0,
    vmax=(max_finite_normalised),
    square=True,
    xticklabels=True,
    yticklabels=True,
    cmap=cmap,
    ax=ax,
    # cbar_kws={"fraction": 0.015},
)
ax.set(xlabel="Polynomial System", ylabel="Library")
ax.tick_params(axis="x", labelrotation=70)
fig.suptitle("Minimum factors of normalised time")
plt.tight_layout()
plt.savefig('images/groebner_heat_map.pdf', dpi=300, bbox_inches='tight')
plt.show()







# raise Exception()
_, _, mem_df = load_python_results("results/results_2024-11-01_12-18-22/results.pickle")

##  Memory graphs

# mem_df["usage"] = mem_df["usage"].apply(lambda x: pd.DataFrame(x, columns=["function", "file", "total", "% total", "own", "% own", "allocations"]))
# mem_df["allocations"] = mem_df["usage"].apply(lambda x: x["allocations"].max())

groebner_mem = mem_df.copy().loc[mem_df["function"].apply(lambda x: x[0]).index]
groebner_mem["system"] = groebner_mem["function"].apply(lambda x: x[1][0]).astype("category")
groebner_mem = groebner_mem.drop(columns=["function", "gc", "venv"])
groebner_mem = groebner_mem.groupby(by=["system", "library"], observed=True).min().sort_index()



res = []
gb = groebner_mem.drop(columns="max_allocations").groupby(by=["system"], observed=True)
for (k, df), m in zip(gb, gb.max(numeric_only=True).dropna()["max_bytes"].values):
    df["max_bytes"] /= m
    res.append(df)

bytes_normalised = pd.concat(res)
del res


res = []
gb = groebner_mem.drop(columns="max_bytes").groupby(by=["system"], observed=True)
for (k, df), m in zip(gb, gb.max(numeric_only=True).dropna()["max_allocations"].values):
    df["max_allocations"] /= m
    res.append(df)

allocs_normalised = pd.concat(res)
del res



max_bytes = bytes_normalised.reset_index().pivot(index="library", columns="system", values="max_bytes")
max_allocs = allocs_normalised.reset_index().pivot(index="library", columns="system", values="max_allocations")


fig = plt.figure(figsize=(12, 3))
ax = fig.add_subplot()
sns.heatmap(max_bytes, vmin=0, square=True, xticklabels=True, yticklabels=True, cmap=cmap, ax=ax)
ax.set(xlabel="Polynomial System", ylabel="Library", title="Normalised max total bytes allocated")
ax.tick_params(axis="x", labelrotation=70)
plt.tight_layout()
plt.savefig('images/groebner_heat_map_bytes_full.pdf', dpi=300, bbox_inches='tight')
plt.show()

fig = plt.figure(figsize=(12, 3))
ax = fig.add_subplot()
sns.heatmap(max_allocs, vmin=0, square=True, xticklabels=True, yticklabels=True, cmap=cmap, ax=ax)
ax.set(xlabel="Polynomial System", ylabel="Library", title="Normalised max number of allocations")
ax.tick_params(axis="x", labelrotation=70)
plt.tight_layout()
plt.savefig('images/groebner_heat_map_allocs_full.pdf', dpi=300, bbox_inches='tight')
plt.show()


fig = plt.figure(figsize=(8, 3))
ax = fig.add_subplot()
sns.heatmap(max_bytes[order], vmin=0, square=True, xticklabels=True, yticklabels=True, cmap=cmap, ax=ax)
ax.set(xlabel="Polynomial System", ylabel="Library", title="Normalised max total bytes allocated (only solved systems)")
ax.tick_params(axis="x", labelrotation=70)
plt.tight_layout()
plt.savefig('images/groebner_heat_map_bytes.pdf', dpi=300, bbox_inches='tight')
plt.show()

fig = plt.figure(figsize=(8, 3))
ax = fig.add_subplot()
sns.heatmap(max_allocs[order], vmin=0, square=True, xticklabels=True, yticklabels=True, cmap=cmap, ax=ax)
ax.set(xlabel="Polynomial System", ylabel="Library", title="Normalised max number of allocations (only solved systems)")
ax.tick_params(axis="x", labelrotation=70)
plt.tight_layout()
plt.savefig('images/groebner_heat_map_allocs.pdf', dpi=300, bbox_inches='tight')
plt.show()
