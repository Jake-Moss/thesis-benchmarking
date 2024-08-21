from benchmarking.harness.generic import Library
import sys

ID = {
    "sympy": {"file": __file__, "env": {"SYMPY_GROUND_TYPES": "python"}},
    "sympy-gmpy": {"file": __file__, "env": {"SYMPY_GROUND_TYPES": "gmpy"}},
    "sympy-flint": {"file": __file__, "env": {"SYMPY_GROUND_TYPES": "flint"}},
}


class SymPy(Library):
    def parse_polys(self, polys_collection: dict):
        for k, (gens, polys) in polys_collection.items():
            gens = sympy.symbols(gens)
            res = []
            for poly in polys:
                if isinstance(poly, dict):
                    poly = sympy.Poly.from_dict(poly, gens=gens)
                else:
                    poly = [sympy.Poly.from_dict(p, gens=gens) for p in poly]
                res.append(poly)
            self.poly_dict[k] = (res, gens)

    @staticmethod
    def add(p1, p2):
        return p1 + p2

    @staticmethod
    def sub(p1, p2):
        return p1 - p2

    @staticmethod
    def mult(p1, p2):
        return p1 * p2

    @staticmethod
    def divmod(p1, p2):
        return divmod(p1, p2)

    @staticmethod
    def factor(p):
        return p.factor()

    @staticmethod
    def groebner(system):
        p, gens = system
        return sympy.groebner(p, *gens, method='f5b')


if __name__ == "__main__":
    import sympy  # noqa: F401
    SymPy.main()
