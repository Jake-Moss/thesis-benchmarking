from benchmarking.harness.generic import Library
import os


ID = {
    "sympy-dmp": {"file": __file__, "env": {"SYMPY_GROUND_TYPES": "python", "SYMPY_USE_DMP": "1"}},
    "sympy-dmp-gmpy": {"file": __file__, "env": {"SYMPY_GROUND_TYPES": "gmpy", "SYMPY_USE_DMP": "1"}},
    "sympy-dmp-flint": {"file": __file__, "env": {"SYMPY_GROUND_TYPES": "flint", "SYMPY_USE_DMP": "1"}},

    "sympy-domains": {"file": __file__, "env": {"SYMPY_GROUND_TYPES": "python", "SYMPY_USE_DMP": "0"}},
    "sympy-domains-gmpy": {"file": __file__, "env": {"SYMPY_GROUND_TYPES": "gmpy", "SYMPY_USE_DMP": "0"}},
    "sympy-domains-flint": {"file": __file__, "env": {"SYMPY_GROUND_TYPES": "flint", "SYMPY_USE_DMP": "0"}},
}


class SymPy(Library):
    def parse_polys(self, polys_collection: dict):
        if os.getenv("SYMPY_USE_DMP") == "1":
            self.__parse_polys_dmp(polys_collection)
        else:
            self.__parse_polys_domains(polys_collection)

    def __parse_polys_dmp(self, polys_collection: dict):
        for k, (gens, polys) in polys_collection.items():
            gens = sympy.symbols(gens)
            res = []
            for poly in polys:
                if isinstance(poly, dict):
                    poly = sympy.Poly.from_dict(poly, gens=gens)
                else:
                    poly = [sympy.Poly.from_dict(p, gens=gens) for p in poly]
                res.append(poly)
            self.poly_dict[k] = res

    def __parse_polys_domains(self, polys_collection: dict):
        for k, (gens, polys) in polys_collection.items():
            gens = sympy.symbols(gens)
            R = sympy.ZZ[*gens]

            res = []
            for poly in polys:
                if isinstance(poly, dict):
                    poly = R.from_sympy(sympy.Poly.from_dict(poly, gens=gens).as_expr())
                else:
                    poly = [R.from_sympy(sympy.Poly.from_dict(p, gens=gens).as_expr()) for p in poly]
                res.append(poly)
            self.poly_dict[k] = res

    @staticmethod
    def add(p1s, p2s):
        for p1, p2 in zip(p1s, p2s):
            p1 + p2

    @staticmethod
    def sub(p1s, p2s):
        for p1, p2 in zip(p1s, p2s):
            p1 - p2

    @staticmethod
    def mult(p1s, p2s):
        for p1, p2 in zip(p1s, p2s):
            p1 * p2

    @staticmethod
    def divmod(p1s, p2s):
        for p1, p2 in zip(p1s, p2s):
            divmod(p1, p2)

    @staticmethod
    def factor(p):
        for p1 in p:
            p1.factor()

    @staticmethod
    def gcd(p1s, p2s):
        for p1, p2 in zip(p1s, p2s):
            p1.gcd(p2)

    @staticmethod
    def lcm(p1s, p2s):
        for p1, p2 in zip(p1s, p2s):
            p1.lcm(p2)

    @staticmethod
    def leading_term(p):
        for p1 in p:
            p1.leading_term()

    @staticmethod
    def groebner(system):
        p, gens = system
        return sympy.groebner(p, *gens)

    @staticmethod
    def groebner_f5b(system):
        p, gens = system
        return sympy.groebner(p, *gens, method="f5b")


if __name__ == "__main__":
    import sympy  # noqa: F401

    SymPy.main()
