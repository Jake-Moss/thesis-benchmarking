import pickle
import sympy

# with open("/tmp/polys.pickle", "rb") as f:
#     polys = pickle.load(f)

# with open("/tmp/run_list.pickle", "rb") as f:
#     run_list = pickle.load(f)

# with open("./polys.pickle", "rb") as f:
#     polys = pickle.load(f)

# with open("./run_list.pickle", "rb") as f:
#     run_list = pickle.load(f)

# with open("./polynomial_db/polys_df.pickle", "rb") as f:
#     df = pickle.load(f)


# 100-500:100,100-500:100,500-1000:100,500-1000:100,1000-2000:200,1000-2000:200




gens = sympy.symbols(("x", "y"))
p1 = sympy.Poly({(0, 1): 1, (1, 0): 2}, *gens)
p2 = sympy.Poly({(0, 1): 1, (1, 1): 3}, *gens)


R = sympy.ZZ[*gens]

p3 = R({(0, 1): 1, (1, 0): 2})
p4 = R({(0, 1): 1, (1, 1): 3})
