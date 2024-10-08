from benchmarking.harness.generic import Library


ID = {
    "sagemath": {"file": __file__, "env": {}},
}


class SageMath(Library):
    def parse_polys(self, polys_collection: dict):
        for k, (gens, polys) in polys_collection.items():
            R = PolynomialRing(ZZ, Integer(len(gens)), gens)

            res = []
            for poly in polys:
                if isinstance(poly, dict):
                    poly = R(poly)
                else:
                    poly = [R(p) for p in poly]
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
    def leading_coefficient(p):
        for p1 in p:
            p1.lc()

    @staticmethod
    def groebner(p):
        I = ideal(p)
        I.groebner_basis()


if __name__ == "__main__":
    import multiprocessing as mp
    from sage.all import PolynomialRing, ZZ, Integer, ideal

    mp.set_start_method("fork")

    SageMath.main()
