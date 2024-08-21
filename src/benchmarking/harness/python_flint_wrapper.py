from benchmarking.harness.generic import Library


ID = {
    "python-flint": {"file": __file__, "env": {}},
}


class PythonFlint(Library):
    def parse_polys(self, polys_collection: dict):
        self.poly_dict = {}
        for k, (gens, polys) in polys_collection.items():
            ctx = flint.fmpz_mpoly_ctx.get_context(len(gens), flint.Ordering.lex, nametup=gens)
            res = []
            for poly in polys:
                if isinstance(poly, dict):
                    poly = ctx.from_dict(poly)
                else:
                    poly = flint.fmpz_mpoly_vec([ctx.from_dict(p) for p in polys], ctx)
                res.append(poly)
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
        return p.buchberger_naive()



if __name__ == "__main__":
    import flint  # noqa: F401
    PythonFlint.main()
