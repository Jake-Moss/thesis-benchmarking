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
            self.divmod = self.__divmod_dmp
        else:
            self.__parse_polys_domains(polys_collection)
            self.leading_coefficient = self.__leading_coefficient_domains
            self.groebner = self.__groebner_domains
            self.divmod = self.__divmod_domains

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
    def add(ps1, ps2):
        for p1, p2 in zip(ps1, ps2):
            p1 + p2

    @staticmethod
    def sub(ps1, ps2):
        for p1, p2 in zip(ps1, ps2):
            p1 - p2

    @staticmethod
    def mult(ps1, ps2):
        for p1, p2 in zip(ps1, ps2):
            p1 * p2

    @staticmethod
    def __divmod_dmp(ps1, ps2):
        for p1, p2 in zip(ps1, ps2):
            sympy.polys.polytools.pdiv(p1, p2)

    @staticmethod
    def __divmod_domains(ps1, ps2):
        for p1, p2 in zip(ps1, ps2):
            p1.pdiv(p2)

    @staticmethod
    def resultant(ps1, ps2):
        for p1, p2 in zip(ps1, ps2):
            p1.resultant(p2)

    @staticmethod
    def factor(p):
        for p1 in p:
            p1.factor_list()

    @staticmethod
    def gcd(ps1, ps2):
        for p1, p2 in zip(ps1, ps2):
            p1.gcd(p2)

    @staticmethod
    def lcm(ps1, ps2):
        for p1, p2 in zip(ps1, ps2):
            p1.lcm(p2)

    @staticmethod
    def __leading_coefficient_dmp(p):
        for p1 in p:
            p1.LC()

    @staticmethod
    def __leading_coefficient_domains(p):
        for p1 in p:
            p1.LC

    @staticmethod
    def __groebner_dmp(system):
        raise NotImplementedError("don't use this one")

    @staticmethod
    def __groebner_domains(system):
        return sympy.polys.groebnertools.groebner(system, system[0].ring)

    # @staticmethod
    # def groebner_f5b(system):
    #     gens, p = system
    #     return sympy.groebner(p, *gens, method="f5b")


if __name__ == "__main__":
    import multiprocessing as mp
    import sympy  # noqa: F401

    mp.set_start_method("fork")

    SymPy.main()
