from benchmarking.harness.generic import Library
import sys


ID = {
    "python-flint": {"file": __file__, "env": {}},
}


class PythonFlint(Library):
    def parse_polys(self, polys_collection: dict):
        self.poly_dict = {}
        for k, (gens, polys) in polys_collection.items():
            ctx = flint.fmpz_mpoly_ctx.get(gens, flint.Ordering.lex)
            if isinstance(polys, dict):
                res = ctx.from_dict({k: int(v) for k, v in polys.items()})
            else:
                res = flint.fmpz_mpoly_vec([ctx.from_dict({k: int(v) for k, v in p.items()}) for p in polys], ctx)

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
            p1 * (p2 / (p1.gcd(p2)))

    @staticmethod
    def leading_term(p):
        for p1 in p:
            p1.leading_term()

    @staticmethod
    @staticmethod
    def groebner(p):
        return p.buchberger_naive().autoreduction()


if __name__ == "__main__":
    import flint  # noqa: F401

    PythonFlint.main()
