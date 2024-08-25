import pandas as pd
import pickle
import matplotlib.pyplot as plt
import pstats

# def main():
with open("results.pickle", "rb") as f:
    results = pickle.load(f)

with open("polynomial_db/polys.pickle", "rb") as f:
    polys = pickle.load(f)


flattened_data = [(*k, v) for k, values in polys.items() for v in values]
poly_df = pd.DataFrame(flattened_data, columns=["generators", "sparsity", "exp_range", "coeff_range", "poly"])
poly_df["exp_range"] = poly_df["exp_range"].apply(lambda x: (x.start, x.stop, x.step)).astype("category")
poly_df["coeff_range"] = poly_df["coeff_range"].apply(lambda x: (x.start, x.stop, x.step)).astype("category")
poly_df["len"] = poly_df["poly"].apply(len)
poly_df = poly_df.set_index(["generators", "sparsity", "exp_range", "coeff_range"])


flattened_data = []
for lang, runners in results.items():
    for runner in runners:
        for profiler, runs in runner["stdout"].items():
            for (func, poly_key, idx), res in runs.items():
                flattened_data.append(
                    (
                        runner["library"],
                        runner["flags"],
                        runner["gc"],
                        runner["venv"],
                        profiler,
                        func,
                        poly_key,
                        # (
                        #     *poly_key[:2],
                        #     (poly_key[2].start, poly_key[2].stop, poly_key[2].step),
                        #     (poly_key[3].start, poly_key[3].stop, poly_key[3].step),
                        # ),
                        idx,
                        res,
                    )
                )


res_df = pd.DataFrame(
    flattened_data, columns=["library", "flags", "gc", "venv", "profiler", "function", "poly_key", "poly_idx", "res"]
)

tmp = res_df[["poly_key", "poly_idx", "res"]]
res_df = res_df.drop(columns=tmp.columns).astype("category")
res_df = pd.concat([res_df, tmp], axis=1)

benchmarks = res_df[res_df["profiler"] == "benchmark"].copy()
benchmarks["min"] = benchmarks["res"].apply(min)
benchmarks = benchmarks.drop(columns=["flags", "venv", "profiler", "poly_key", "poly_idx", "res"]).set_index(
    ["library", "gc", "function"]
)
gb = benchmarks.groupby(by=["function", "library", "gc"])
means = gb.mean().reset_index(level=0).groupby("function")
# NOTE: this isn't accounting for the poly key andf is just plain wrong

cpu_res = res_df[res_df["profiler"] == "cpu"].copy()
p = pstats.Stats(*cpu_res.res)
# p.strip_dirs().sort_stats("tottime").print_stats()

# if __name__ == "__main__":
#     main()
