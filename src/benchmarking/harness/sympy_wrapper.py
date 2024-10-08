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
            self.leading_coefficient = self.__leading_coefficient_dmp
            self.groebner = self.__groebner_dmp
        else:
            self.__parse_polys_domains(polys_collection)
            self.leading_coefficient = self.__leading_coefficient_domains
            self.groebner = self.__groebner_domains

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
            self.poly_dict[k] = (gens, res)

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
            self.poly_dict[k] = (gens, res)

    @staticmethod
    def add(s1, s2):
        (_, p1s) = s1
        (_, p2s) = s2
        for p1, p2 in zip(p1s, p2s):
            p1 + p2

    @staticmethod
    def sub(s1, s2):
        (_, p1s) = s1
        (_, p2s) = s2
        for p1, p2 in zip(p1s, p2s):
            p1 - p2

    @staticmethod
    def mult(s1, s2):
        (_, p1s) = s1
        (_, p2s) = s2
        for p1, p2 in zip(p1s, p2s):
            p1 * p2

    @staticmethod
    def divmod(s1, s2):
        (gens, p1s) = s1
        (_, p2s) = s2
        for p1, p2 in zip(p1s, p2s):
            sympy.polys.polytools.pdiv(p1, p1)

    @staticmethod
    def factor(s):
        (_, p) = s
        for p1 in p:
            p1.factor_list()

    @staticmethod
    def gcd(s1, s2):
        (_, p1s) = s1
        (_, p2s) = s2
        for p1, p2 in zip(p1s, p2s):
            p1.gcd(p2)

    @staticmethod
    def lcm(s1, s2):
        (_, p1s) = s1
        (_, p2s) = s2
        for p1, p2 in zip(p1s, p2s):
            p1.lcm(p2)

    @staticmethod
    def __leading_coefficient_dmp(s):
        _, p = s
        for p1 in p:
            p1.LC()

    @staticmethod
    def __leading_coefficient_domains(s):
        _, p = s
        for p1 in p:
            p1.LC

    @staticmethod
    def __groebner_dmp(system):
        gens, p = system
        return sympy.polys.polytools.groebner(p, *gens)

    @staticmethod
    def __groebner_domains(system):
        _, p = system
        return sympy.polys.groebnertools.groebner(p, p[0].ring)

    # @staticmethod
    # def groebner_f5b(system):
    #     gens, p = system
    #     return sympy.groebner(p, *gens, method="f5b")


if __name__ == "__main__":
    import multiprocessing as mp
    import sympy  # noqa: F401

    mp.set_start_method("fork")

    SymPy.main()
