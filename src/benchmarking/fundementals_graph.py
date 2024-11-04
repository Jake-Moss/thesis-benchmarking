import pandas as pd
import pickle
import matplotlib.pyplot as plt
from matplotlib import colormaps
from matplotlib.legend import Legend
import matplotlib.gridspec as gridspec
import seaborn as sns
import pathlib
from src.benchmarking.gen_polys import PolynomialGenerator
from benchmarking.post_process import load_python_results, load_external_results


sns.set_theme("notebook", font_scale=1, rc={
    'figure.figsize': (8, 6),
    # "text.usetex": True,
    # "text.latex.preamble": r"\usepackage{libertine}",
    'font.family': 'serif',
})
cmap = colormaps["inferno_r"]

f = pathlib.Path("results/results_2024-11-01_16-07-14")


bench_df, _, _ = load_python_results(f / "results.pickle")
external_bench_df = load_external_results(f / "results.pickle")

with open("./polys.pickle", "rb") as f:
    polys = PolynomialGenerator.parse_to_df(pickle.load(f))
polys.index = polys.index.astype("category")

coeff_map = dict((range(*k), v) for k, v in zip(polys["coeff_range"].unique().sort_values(), ["small coeff", "large coeff"]))
exp_map = dict((range(*k), v) for k, v in zip(polys["exp_range"].unique().sort_values(), ["Small exponent", "Large exponent"]))

bench_df = bench_df[(~bench_df["gc"]) & (bench_df["venv"] == "3.12.4")].drop(columns=["gc", "venv"])

merged = pd.concat([bench_df, external_bench_df.drop(columns=["gc", "venv"])], axis=0)

merged["exp"] = merged.args.apply(lambda args: exp_map[args[0][2]])
merged["args"] = merged.args.apply(lambda args: tuple((x[0], x[1], exp_map[x[2]], coeff_map[x[3]]) for x in args))


tmp = merged["args"].apply(len) == 1
unary_functions = merged[tmp].copy()
binary_functions = merged[~tmp].copy()
del tmp

unary_functions[["Generators", "Terms"]] = unary_functions.args.apply(lambda x: x[0][:2]).apply(pd.Series)
unary_functions = unary_functions.drop(columns="args")

binary_functions[["Generators", "Terms"]] = binary_functions.args.apply(lambda x: ((x[0][0], x[1][0]), (x[0][1], x[1][1]))).apply(pd.Series)
binary_functions = binary_functions.drop(columns="args")

assert binary_functions["Generators"].apply(lambda x: x[0] == x[1]).all()
assert binary_functions["Terms"].apply(lambda x: x[0] == x[1]).all()

binary_functions["Generators"] = binary_functions["Generators"].apply(lambda x: x[0])
binary_functions["Terms"] = binary_functions["Terms"].apply(lambda x: x[0])


fixed_gens = pd.concat([
    unary_functions[unary_functions["Generators"] == 3],
    binary_functions[binary_functions["Generators"] == 3]
]).drop(columns="Generators").reset_index(drop=True).sort_values(by=["library", "function", "Terms"])

fixed_terms = pd.concat([
    unary_functions[unary_functions["Terms"] == 10],
    binary_functions[binary_functions["Terms"] == 10]
]).drop(columns="Terms").reset_index(drop=True).sort_values(by=["library", "function", "Generators"])

fixed_gens = pd.concat([fixed_gens[(fixed_gens["library"] != "mathematica")], fixed_gens[(fixed_gens["library"] == "mathematica")]])
fixed_terms = pd.concat([fixed_terms[(fixed_terms["library"] != "mathematica")], fixed_terms[(fixed_terms["library"] == "mathematica")]])

# sns_kwargs = {
#     "x": "Terms",
#     "y": "timings",
#     "hue": "library",
# }

# facet = sns.FacetGrid(
#     fixed_gens,
#     # row="library",
#     col="function",
# )
# facet.map_dataframe(
#     sns.scatterplot,
#     **sns_kwargs
# )
# facet.add_legend()
# facet.figure.suptitle("Time delta (s) from enabling garbage collection")
# facet.set_ylabels("Relative time")
# facet.set_xlabels("Polynomial system")
# facet.set_titles(row_template="{row_name}")
# facet.tight_layout()
# facet.tick_params(axis="x", labelrotation=70)
# plt.show()


# sns.relplot(fixed_gens, x="Terms", y="timings", hue="library", col="function")
# plt.show()

# sns.relplot(fixed_terms, x="Generators", y="timings", hue="library", col="function")
# plt.show()


# worst_fixed_terms_pivot = fixed_terms[
#     fixed_terms["Generators"] == fixed_terms["Generators"].max()
# ].pivot(index="library", columns="function", values="timings")

# worst_fixed_gens_pivot = fixed_gens[
#     fixed_gens["Terms"] == fixed_gens["Terms"].max()
# ].pivot(index="library", columns="function", values="timings")

# worst_fixed_gens_pivot.replace(float("inf"), float("NaN")).max()


# ax = sns.heatmap(
#     worst_fixed_terms_pivot / worst_fixed_terms_pivot.replace(float("inf"), float("NaN")).max(),
#     # annot=max_labels,
#     fmt="",
#     vmin=0,
#     square=True,
#     xticklabels=True,
#     yticklabels=True,
#     cmap=cmap,
# )
# ax.set(xlabel="Function", ylabel="Factors of normalised time", title="Fixed terms")
# plt.tight_layout()
# plt.show()


# ax = sns.heatmap(
#     worst_fixed_gens_pivot / worst_fixed_gens_pivot.replace(float("inf"), float("NaN")).max(),
#     # annot=max_labels,
#     fmt="",
#     vmin=0,
#     square=True,
#     xticklabels=True,
#     yticklabels=True,
#     cmap=cmap,
# )
# ax.set(xlabel="Function", ylabel="Factors of normalised time", title="Fixed gens")
# plt.tight_layout()
# plt.show()










def make_big_plot(df, x_col, title, layout, size, header=True):
    n = max(v[0] for v in layout.values()) + 1 + header
    m = max(v[1] for v in layout.values()) + 1

    fig = plt.figure(figsize=size)
    gs = gridspec.GridSpec(n, m, hspace=0.6, wspace=0.5)

    if header:
        gs00 = gridspec.GridSpecFromSubplotSpec(2, 1, subplot_spec=gs[0, :])
        ax_legend = fig.add_subplot(gs00[0])
        ax_legend.axis('off')

        ax_colorbar = fig.add_subplot(gs00[1])
        ax_colorbar.axis('off')

    df_norm = df.copy()
    df_norm["timings"] = df_norm["timings"].replace(float("inf"), float("NaN"))

    res = []
    gb = df_norm.reset_index().groupby(by=["function", x_col], observed=True)
    for (k, tmp), m in zip(gb, gb.max(numeric_only=True).dropna()["timings"].values):
        tmp["timings"] /= m
        res.append(tmp)

    df_norm = pd.concat(res)
    del res

    gb1 = df.groupby("function")
    gb2 = df_norm.groupby("function")

    scatter_legend = None

    for col, (i, j, name) in layout.items():
        df1 = gb1.get_group(col)
        df2 = gb2.get_group(col)

        df1 = pd.concat([df1[(df1["library"] != "mathematica")], df1[(df1["library"] == "mathematica")]])
        df2 = pd.concat([df2[(df2["library"] != "mathematica")], df2[(df2["library"] == "mathematica")]])

        gs00 = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=gs[header + i, j], hspace=0.6, wspace=0.2)

        rot = 0
        # Scatter plot
        ax_scatter = fig.add_subplot(gs00[0])
        sns.scatterplot(data=df1, x=x_col, y="timings", hue="library", style="library", ax=ax_scatter, s=75)
        ax_scatter.set_ylabel("Time (s) per 50")
        ax_scatter.tick_params(axis="x", labelrotation=rot)
        ax_scatter.set_box_aspect(1)
        legend = ax_scatter.get_legend()

        pivot = df2.pivot(index="library", columns=x_col, values="timings")
        try:
            pivot = pd.concat([pivot.drop("mathematica"), pivot.loc[["mathematica"]]])
        except KeyError:
            pass

        ax_heatmap = fig.add_subplot(gs00[1])
        sns.heatmap(
            pivot,
            ax=ax_heatmap,
            cbar=False,
            cmap=cmap,
            yticklabels=False,
            square=True
        )
        ax_heatmap.set_ylabel("Library", labelpad=20.0)
        ax_heatmap.tick_params(axis="x", labelrotation=rot)
        ax_heatmap.yaxis.set_label_position("right")

        ax = fig.add_subplot(gs00[:])
        ax.axis('off')
        ax.set_title(name, pad=10.0, fontsize="large")

        ax_scatter.set_xticks(df1[x_col].unique()[:len(ax_heatmap.get_xticklabels())], ax_heatmap.get_xticklabels())

        new_legend = Legend(
            ax_heatmap,
            legend.legend_handles,
            ["" for x in legend.texts],
            title="",
            loc='center left',
            frameon=False,
            bbox_to_anchor=(0.9, 0.5),
            labelspacing=0.3,
        )
        ax_heatmap.add_artist(new_legend)

        if scatter_legend is None and header:
            scatter_legend = legend
        else:
            legend.remove()


    if header:
        new_legend = Legend(
            ax_legend,
            scatter_legend.legend_handles,
            [x.get_text() for x in scatter_legend.texts],
            title="Library",
            loc='center',
            frameon=True,
        )
        ax_legend.add_artist(new_legend)
        scatter_legend.remove()

        norm = plt.Normalize(vmin=0.0, vmax=1.0)
        sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
        sm.set_array([])

        cbar = fig.colorbar(sm, ax=ax_colorbar, orientation='horizontal')
        cbar.set_label('Relative runtime')

    fig.suptitle(title)
    return fig


layout = {
    'add':                 (0, 0, "Addition"),
    'mult':                (0, 1, "Multiplication"),
    'divmod':              (1, 0, "Pseudo-division"),
    'leading_coefficient': (1, 1, "Leading coefficient"),
    'gcd':                 (2, 0, "GCD"),
    'resultant':           (2, 1, "Resultant"),
}

poster_layout = {
    'add':                 (0, 0, "Addition"),
    'mult':                (0, 1, "Multiplication"),
    'divmod':              (1, 0, "Pseudo-division"),
    'leading_coefficient': (1, 1, "Leading coefficient"),
}

# layout = {
#     'add': (0, 0, "Addition"),
#     'leading_coefficient': (1, 0, "Leading coefficienft"),
# }


# fig = make_big_plot(
#     fixed_gens[fixed_gens["library"] != "mathematica"],
#     "Terms",
#     "Minimum absolute and relative time for fundamental operations with 5 generators",
#     poster_layout,
#     # (11, 12),
#     (11, 10),
# )
# fig.savefig('images/fundamentals_fixed_gens.pdf', dpi=300, bbox_inches='tight')
# fig.show()

# fig = make_big_plot(
#     fixed_terms[fixed_terms["library"] != "mathematica"],
#     "Generators",
#     "Minimum absolute and relative time for fundamental operations with 10 terms",
#     poster_layout,
#     # (11, 12),
#     (11, 10),
# )
# fig.savefig('images/fundamentals_fixed_terms.pdf', dpi=300, bbox_inches='tight')
# fig.show()

# fig = make_big_plot(
#     fixed_terms[fixed_terms["library"] != "mathematica"],
#     "Generators",
#     "Minimum absolute and relative time for fundamental operations with 10 terms",
#     poster_layout,
#     # (11, 8),
#     (11, 6),
#     header=False
# )
# fig.savefig('images/fundamentals_fixed_terms_no_header.pdf', dpi=300, bbox_inches='tight')
# fig.show()



fig = make_big_plot(
    fixed_gens[fixed_gens["exp"] == "Small exponent"],
    "Terms",
    "Minimum absolute and relative time for fundamental operations\nwith 3 generators and small exponents",
    layout,
    (11, 13),
)
fig.savefig('images/fundamentals_fixed_gens_full_small.pdf', dpi=300, bbox_inches='tight')
fig.show()

fig = make_big_plot(
    fixed_terms[fixed_gens["exp"] == "Small exponent"],
    "Generators",
    "Minimum absolute and relative time for fundamental operations\nwith 10 terms and small exponents",
    layout,
    (11, 13),
)
fig.savefig('images/fundamentals_fixed_terms_full_small.pdf', dpi=300, bbox_inches='tight')
fig.show()




fig = make_big_plot(
    fixed_gens[fixed_gens["exp"] != "Small exponent"],
    "Terms",
    "Minimum absolute and relative time for fundamental operations\nwith 3 generators and large exponents",
    layout,
    (11, 13),
)
fig.savefig('images/fundamentals_fixed_gens_full_large.pdf', dpi=300, bbox_inches='tight')
fig.show()

fig = make_big_plot(
    fixed_terms[fixed_gens["exp"] != "Small exponent"],
    "Generators",
    "Minimum absolute and relative time for fundamental operations\nwith 10 terms and large exponents",
    layout,
    (11, 13),
)
fig.savefig('images/fundamentals_fixed_terms_full_large.pdf', dpi=300, bbox_inches='tight')
fig.show()







fig = make_big_plot(
    fixed_gens[(fixed_gens["exp"] == "Small exponent") & (fixed_gens["library"] != "mathematica")],
    "Terms",
    "Minimum absolute and relative time for fundamental operations\nwith 3 generators and small exponents, sans Mathematica",
    layout,
    (11, 13),
)
fig.savefig('images/fundamentals_fixed_gens_full_small_sans_mathematica.pdf', dpi=300, bbox_inches='tight')
fig.show()

fig = make_big_plot(
    fixed_terms[(fixed_terms["exp"] == "Small exponent") & (fixed_terms["library"] != "mathematica")],
    "Generators",
    "Minimum absolute and relative time for fundamental operations\nwith 10 terms and small exponents, sans Mathematica",
    layout,
    (11, 13),
)
fig.savefig('images/fundamentals_fixed_terms_full_small_sans_mathematica.pdf', dpi=300, bbox_inches='tight')
fig.show()




fig = make_big_plot(
    fixed_gens[(fixed_gens["exp"] != "Small exponent") & (fixed_gens["library"] != "mathematica")],
    "Terms",
    "Minimum absolute and relative time for fundamental operations\nwith 3 generators and large exponents, sans Mathematica",
    {k: layout[k] for k in (layout.keys() - {"resultant"})},
    (11, 13),
)
fig.savefig('images/fundamentals_fixed_gens_full_large_sans_mathematica.pdf', dpi=300, bbox_inches='tight')
fig.show()

fig = make_big_plot(
    fixed_terms[(fixed_terms["exp"] != "Small exponent") & (fixed_terms["library"] != "mathematica")],
    "Generators",
    "Minimum absolute and relative time for fundamental operations\nwith 10 terms and large exponents, sans Mathematica",
    {k: layout[k] for k in (layout.keys() - {"resultant"})},
    (11, 13),
)
fig.savefig('images/fundamentals_fixed_terms_full_large_sans_mathematica.pdf', dpi=300, bbox_inches='tight')
fig.show()










raise Exception()

_, _, mem_df = load_python_results("results/results_2024-11-01_16-21-38/results.pickle")

##  Memory graphs

# mem_df["usage"] = mem_df["usage"].apply(lambda x: pd.DataFrame(x, columns=["function", "file", "total", "% total", "own", "% own", "allocations"]))
# mem_df["allocations"] = mem_df["usage"].apply(lambda x: x["allocations"].max())

mem = mem_df.copy().loc[mem_df["function"].apply(lambda x: x[0]).index]
mem["args"] = mem["function"].apply(lambda x: x[1][0]).astype("category")
mem["function"] = mem["function"].apply(lambda x: x[0]).astype("category")

mem["exp"] = mem.args.apply(lambda args: exp_map[args[2]])
mem = mem.drop(columns=["args", "gc", "venv"])



res = []
gb = mem.drop(columns="max_allocations").groupby(by=["function"], observed=True)
for (k, df), m in zip(gb, gb.max(numeric_only=True).dropna()["max_bytes"].values):
    df["max_bytes"] /= m
    res.append(df)

bytes_normalised = pd.concat(res)
del res


res = []
gb = mem.drop(columns="max_bytes").groupby(by=["function"], observed=True)
for (k, df), m in zip(gb, gb.max(numeric_only=True).dropna()["max_allocations"].values):
    df["max_allocations"] /= m
    res.append(df)

allocs_normalised = pd.concat(res)
del res



max_bytes = bytes_normalised.pivot(index="library", columns="function", values="max_bytes")
max_allocs = allocs_normalised.pivot(index="library", columns="function", values="max_allocations")
