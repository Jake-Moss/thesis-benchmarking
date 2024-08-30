from benchmarking.harness.generic import Library
import sys


ID = {
    "python-flint": {"file": __file__, "env": {}},
}


class PythonFlint(Library):
    def parse_polys(self, polys_collection: dict):
        self.poly_dict = {}
        for k, (gens, polys) in polys_collection.items():
            ctx = flint.fmpz_mpoly_ctx.get_context(len(gens), flint.Ordering.lex, nametup=tuple(gens))
            if isinstance(polys, dict):
                res = ctx.from_dict({k: int(v) for k, v in polys.items()})
            else:
                res = flint.fmpz_mpoly_vec([ctx.from_dict({k: int(v) for k, v in p.items()}) for p in polys], ctx)

            self.poly_dict[k] = res

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
    def groebner(p):
        return p.buchberger_naive().autoreduction()


if __name__ == "__main__":
    import flint  # noqa: F401

    PythonFlint.main()
