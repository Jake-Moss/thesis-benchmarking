import logging
import pathlib
import sympy
import pandas as pd
import pickle

logger = logging.getLogger(__name__)

with open(pathlib.Path("polynomial_db") / "poly_list") as f:
    lines = [x.split("\n") for x in f.read().split("\n\n")]

descriptions = []
for line in lines[0]:
    if not line:
        continue
    name, desc = line.split(":")
    descriptions.append((name.strip(), desc.strip()))
descriptions = pd.DataFrame(descriptions, columns=["name", "description"]).set_index("name")


stats = []
for line in lines[1]:
    if not line:
        continue
    name, *nums = line.split(":")
    stats.append((name.strip(), *(int(x.strip()) for x in nums)))
stats = pd.DataFrame(stats, columns=["name", "n", "D", "bz", "bs", "mv", "#sols"]).set_index("name")


timings = []
for line in lines[2]:
    if not line:
        continue
    name, *times, _ = line.split("|")
    timings.append((name.strip(), *(pd.Timedelta(x.strip()) for x in times)))
timings = pd.DataFrame(timings, columns=["name", "root counts", "start system", "continuation", "total"]).set_index(
    "name"
)


polys = []
for filename in descriptions.index:
    file = pathlib.Path("polynomial_db") / filename
    if not file.exists():
        print("Missing file:", filename)

    with open(file, "r") as f:
        lines = f.read()

    pos = lines.find("\n")
    num_polys = int(lines[:pos])
    lines = lines[pos + 1 :]

    pos = lines.find("\n\n")
    system = lines[:pos]
    lines = lines[pos + 1 :]

    system = [(poly.strip().replace("\n", "").replace("^", "**").replace("i", "I")) for poly in system.split(";")][:-1]
    system = [sympy.parse_expr(poly, evaluate=False) for poly in system]

    gens = set()
    for poly in system:
        gens |= poly.free_symbols

    system = [poly.as_poly(*gens) for poly in system]
    try:
        system = [poly.set_domain("ZZ") for poly in system]
    except sympy.CoercionFailed:
        print("failed to set domain for", filename)
        continue

    polys.append((filename, list(sorted(gens, key=str)), system))
polys = pd.DataFrame(polys, columns=["name", "generators", "system"]).set_index("name")

df = polys.join([descriptions, stats, timings], how="left").sort_values("total")

# NOTE
# df = df[df["total"] < pd.Timedelta(10, "s")]

gens_dict = df["generators"].apply(lambda gens: [str(x) for x in gens]).to_dict()
polys_dict = df["system"].apply(
    lambda system: [{k: str(v) for k, v in x.as_dict().items()} for x in system]
).to_dict()

polys_dict = {k: (gens_dict[k], polys_dict[k]) for k in polys_dict.keys()}

run_list = {"groebner": [(x,) for x in polys_dict.keys()]}

with open(pathlib.Path("polynomial_db") / "polys.pickle", "wb") as f:
    pickle.dump(polys_dict, f)

with open(pathlib.Path("polynomial_db") / "run_list.pickle", "wb") as f:
    pickle.dump(run_list, f)

with open(pathlib.Path("polynomial_db") / "polys.pickle", "rb") as f:
    tmp = pickle.load(f)
    # tmp = pd.DataFrame.from_dict(tmp)
    # tmp.index.name = "name"


# for row in df[df["total"] < pd.Timedelta(15, "s")].itertuples():
#     groebner = sympy.groebner(row.system, row.generators)
#     print(f"Constructed Gröbner basis for {row.Index}:")
#     # print(groebner)
