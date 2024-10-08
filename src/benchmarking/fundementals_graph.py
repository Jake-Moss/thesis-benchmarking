import pandas as pd
import pickle
import matplotlib.pyplot as plt
from matplotlib import colormaps
import seaborn as sns
import math
from src.benchmarking.gen_polys import PolynomialGenerator
from benchmarking.post_process import load_python_results, load_external_results


sns.set_theme("notebook", font_scale=1, rc={'figure.figsize': (8, 6)})
cmap = colormaps["binary"]



bench_df, cpu_df, mem_df = load_python_results("results/results_2024-10-08_23-34-10/results.pickle")

with open("./polys.pickle", "rb") as f:
    polys = PolynomialGenerator.parse_to_df(pickle.load(f))
polys.index = polys.index.astype("category")

coeff_map = dict((range(*k), v) for k, v in zip(polys["coeff_range"].unique().sort_values(), ["small coeff", "large coeff"]))
exp_map = dict((range(*k), v) for k, v in zip(polys["exp_range"].unique().sort_values(), ["small exp", "large exp"]))

bench_df["args"] = bench_df.args.apply(lambda args: tuple((x[0], x[1], exp_map[x[2]], coeff_map[x[3]]) for x in args))

bench_df = bench_df[bench_df["gc"] & (bench_df["venv"] == "3.12.4")].drop(columns=["gc", "venv"])

tmp = bench_df["args"].apply(len) == 1
unary_functions = bench_df[tmp]
binary_functions = bench_df[~tmp]
del tmp

# Not correct
# binary_functions[["Generators", "Terms", "Exponent size", "Coefficient size"]] = binary_functions.args.apply(lambda x: x[0]).apply(pd.Series)
# binary_functions = binary_functions.drop(columns="args")

# unary_functions[["Generators", "Terms", "Exponent size", "Coefficient size"]] = unary_functions.args.apply(lambda x: x[0]).apply(pd.Series)
# unary_functions = unary_functions.drop(columns="args")




# Fixed gens
fixed_gens = binary_functions[binary_functions["Generators"] == 5]
fixed_terms = binary_functions[binary_functions["Generators"] != 5]



sns_kwargs = {
    "x": "function",
    "y": "timings",
    "hue": "library",
}


# for k, df in binary_functions.groupby(["Exponent size", "Coefficient size"]):
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




bench_df = load_external_results("results/results_2024-10-08_23-34-10/results.pickle")

coeff_map = dict((range(*k), v) for k, v in zip(polys["coeff_range"].unique().sort_values(), ["small coeff", "large coeff"]))
exp_map = dict((range(*k), v) for k, v in zip(polys["exp_range"].unique().sort_values(), ["small exp", "large exp"]))

bench_df["args"] = bench_df.args.apply(lambda args: tuple((x[0], x[1], exp_map[x[2]], coeff_map[x[3]]) for x in args))

bench_df = bench_df.drop(columns=["gc", "venv"])

tmp = bench_df["args"].apply(len) == 1
unary_functions = bench_df[tmp]
binary_functions = bench_df[~tmp]
del tmp

first_arg = binary_functions.args.apply(lambda x: x[0])
second_arg = binary_functions.args.apply(lambda x: x[1])
