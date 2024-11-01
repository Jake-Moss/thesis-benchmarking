from benchmarking.harness.generic import Library, MathematicaExecutor


# We cheat in this wrapper and use the sage interface to mathematica! It works wonderfully


ID = {
    "mathematica": {"file": __file__, "env": {}},
}


class Mathematica(Library):
    @classmethod
    def main(cls):
        mathematica("myPolynomialReduce[args___] := PolynomialReduce[args, CoefficientDomain -> Integers]")
        mathematica("myGroebnerBasis[args___] := GroebnerBasis[args, CoefficientDomain -> Integers]")
        super().main(Executor_cls=MathematicaExecutor)

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
            self.poly_dict[k] = (mathematica(R.gens()), mathematica(res))

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
        (_, p1s) = s1
        (_, p2s) = s2
        for p1, p2 in zip(p1s, p2s):
            p1.myPolynomialReduce([p2])

    @staticmethod
    def resultant(s1, s2):
        (gens, p1s) = s1
        (_, p2s) = s2
        for p1, p2 in zip(p1s, p2s):
            p1.Resultant(p2, gens[1])  # Mathematica is 1-indexed

    @staticmethod
    def factor(s):
        (_, p) = s
        for p1 in p:
            p1.Factor()

    @staticmethod
    def gcd(s1, s2):
        (_, p1s) = s1
        (_, p2s) = s2
        for p1, p2 in zip(p1s, p2s):
            p1.PolynomialGCD(p2)

    @staticmethod
    def lcm(s1, s2):
        (_, p1s) = s1
        (_, p2s) = s2
        for p1, p2 in zip(p1s, p2s):
            p1.PolynomialLCM(p2)

    @staticmethod
    def leading_coefficient(s):
        gens, p = s
        for p1 in p:
            p1.CoefficientList(gens)

    @staticmethod
    def groebner(s):
        gens, p = s
        p.myGroebnerBasis()


if __name__ == "__main__":
    from sage.all import PolynomialRing, ZZ, Integer, mathematica

    Mathematica.main()
