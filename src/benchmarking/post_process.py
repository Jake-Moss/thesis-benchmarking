import pandas as pd
import pickle
import matplotlib.pyplot as plt
import seaborn as sns


with open("/tmp/results_2024-08-27_20:35:43/results.pickle", "rb") as f:
    results = pickle.load(f)

with open("polynomial_db/polys_df.pickle", "rb") as f:
    polys = pickle.load(f)

polys.index = polys.index.astype("category")

res = pd.DataFrame(results["python"])
res["venv"] = res["venv"].apply(str)
res = pd.concat([res[["stdout", "flags"]], res.drop(columns=["stdout", "flags"]).astype("category")], axis=1)
res["venv"] = res["venv"].map({".venv-312": "3.12.4", ".venv-313": "3.13.0rc1"})
gb = res.groupby(by="type", observed=False)


(_, bench_df), (_, cpu_df), (_, mem_df) = list(gb)
bench_df = bench_df.drop(columns=["type"])
cpu_df = cpu_df.drop(columns=["type"])
mem_df = mem_df.drop(columns=["type"])

bench_df["function"] = bench_df["stdout"].apply(dict.keys)
tmp = bench_df.explode("function")
tmp["timings"] = bench_df["stdout"].apply(dict.values).explode()
tmp["timings"] = tmp["timings"].apply(min)
tmp = tmp.drop(columns=["stdout", "flags"])
bench_df = tmp.reset_index(drop=True)
del tmp

mem_df["function"] = mem_df["stdout"].apply(dict.keys)
tmp = mem_df.explode("function")
tmp["usage"] = mem_df["stdout"].apply(dict.values).explode()
tmp = tmp.drop(columns=["stdout", "flags"])
mem_df = tmp.reset_index(drop=True)
del tmp

mem_df["usage"] = mem_df["usage"].apply(lambda x: pd.DataFrame(x, columns=["function", "file", "total", "% total", "own", "% own", "allocations"]))
mem_df["allocations"] = mem_df["usage"].apply(lambda x: x["allocations"].max())




groebner = bench_df.copy().iloc[bench_df["function"].apply(lambda x: x[0]).index]
groebner["system"] = groebner["function"].apply(lambda x: x[1][0]).astype("category")
groebner = groebner.drop(columns=["function"])
groebner = groebner.set_index(["system", "library", "gc", "venv"]).sort_index()
order = groebner.merge(
    polys.reset_index().reset_index()[["index", "name"]].rename(columns={"name": "system"}),
    on="system",
    how="left",
    validate="many_to_one"
).sort_values(by="index")["system"].unique()


res = []
gb = groebner.reset_index().groupby(by=["system", "gc", "venv"], observed=False)
for (k, df), m in zip(gb, gb.min(numeric_only=True)["timings"].values):
    df["timings"] /= m
    res.append(df)

groebner_normalised = pd.concat(res).set_index(["system", "library", "gc", "venv"]).sort_index()
del res

sns_kwargs = {
    "x": "system",
    "y": "timings",
    "hue": "library",
    "palette": "flare",
    "order": order,
}

g = sns.FacetGrid(
    groebner_normalised.reset_index(),
    col="gc",
    row="venv",
    aspect=4/3,
)
g.map_dataframe(sns.barplot, **sns_kwargs)
g.add_legend()
g.figure.suptitle("Time (s) to construct reduced Gröbner basis")
g.set_ylabels("Factors of fastest solve")
g.set_xlabels("Polynomial system")
g.set_titles(row_template="{row_name}")
g.tight_layout()
plt.show()

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
plt.show()


version_diff = (groebner.loc[:, :, :, "3.13.0rc1"] - groebner.loc[:, :, :, "3.12.4"]) / groebner.loc[:, :, :, "3.13.0rc1"]
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
plt.show()

groebner_mean = groebner_normalised.groupby(by=["library"]).mean(numeric_only=True)
g = sns.barplot(
    groebner_mean.reset_index(),
    x="library",
    y="timings",
    hue="library",
    palette="flare",
    legend=True
)
g.figure.suptitle("Mean relative runtime to construct reduced Gröbner basis")
g.set_ylabel("Mean relative runtime")
g.set_xlabel("Polynomial system")
plt.tight_layout()
plt.show()






groebner_mem = mem_df.copy().iloc[mem_df["function"].apply(lambda x: x[0]).index]
groebner_mem["system"] = groebner_mem["function"].apply(lambda x: x[1][0]).astype("category")
groebner_mem = groebner_mem.drop(columns=["function", "usage"])
groebner_mem = groebner_mem.groupby(by=["library", "system"]).mean(numeric_only=True)


g = sns.barplot(
    groebner_mem.reset_index(),
    x="system",
    y="allocations",
    hue="library",
    palette="flare",
    order=order,
    legend=True
)
g.figure.suptitle("Number of Python and native allocations to construct reduced Gröbner basis")
g.set_ylabel("Number of allocations")
g.set_xlabel("Polynomial system")
plt.tight_layout()
plt.show()
