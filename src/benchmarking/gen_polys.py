import itertools
import random
import logging
from collections import defaultdict
import pandas as pd


logger = logging.getLogger(__name__)

poly_gen_format = """\
Generating {number} polynomials with:
\tGenerators: {gens}
\tCoefficients in: {coeff_range}
\tExponents in: {exp_range}
\tTerms: {num_terms}"""


class PolynomialGenerator:
    def __init__(
        self,
        *,
        generators: list[range],
        terms: list[range],
        coefficients: list[range],
        exponents: list[range],
        groupby: list[str],
        number: int,
        seed: int,
    ):
        self.gens = generators
        self.terms = terms
        self.coefficients = coefficients
        self.exponents = exponents
        self.number = number
        self.rng = random.Random(seed)

        keys = ["gens", "terms", "exp_range", "coeff_range"]
        self.groupby = tuple(keys.index(x) for x in groupby)

    def generate(self):
        self.results = {}
        self.singles = []
        self.combos = []
        for gen_range, num_terms_range, coeff_range, exp_range in itertools.product(
                self.gens, self.terms, self.coefficients, self.exponents,
        ):
            res = {}
            for gens in gen_range:
                for num_terms in num_terms_range:
                    logger.info(
                        poly_gen_format.format(
                            number=self.number,
                            gens=gens,
                            num_terms=num_terms,
                            coeff_range=coeff_range,
                            exp_range=exp_range,
                        )
                    )

                    polys = []
                    for _ in range(self.number):
                        poly = {}
                        for _ in range(num_terms):
                            exp_vec = tuple(
                                self.rng.randrange(exp_range.start, exp_range.stop, exp_range.step) for _ in range(gens)
                            )
                            coeff = self.rng.randrange(coeff_range.start, coeff_range.stop, coeff_range.step)
                            poly[exp_vec] = coeff

                        if len(poly) != num_terms:
                            logger.warning("polynomial generated with less terms than requested")

                        polys.append(poly)

                    res[gens, num_terms, exp_range, coeff_range] \
                        = (["x" + str(gen) for gen in range(gens)], polys)


            groups = defaultdict(list)
            for key in res.keys():
                groups[tuple(key[i] for i in self.groupby)].append(key)

            self.singles.extend((x,) for x in res.keys())
            self.combos.extend(
                itertools.chain.from_iterable(
                    itertools.combinations_with_replacement(v, r=2)
                    for v in groups.values()
                )
            )

            self.results.update(res)

        self.run_list = {
            "add": self.combos,
            # "sub": self.combos,
            "mult": self.combos,
            "divmod": self.combos,
            "resultant": self.combos,
            # "factor": self.singles,
            "gcd": self.combos,
            # "lcm": self.combos,
            "leading_coefficient": self.singles,
        }


    @staticmethod
    def parse_to_df(results):
        flattened_data = [(*k, values[0], v) for k, values in results.items() for v in values[1:]]
        df = pd.DataFrame(flattened_data, columns=["generators", "terms", "exp_range", "coeff_range", "gens", "poly"])
        df["exp_range"] = df["exp_range"].apply(lambda x: (x.start, x.stop, x.step)).astype("category")
        df["coeff_range"] = df["coeff_range"].apply(lambda x: (x.start, x.stop, x.step)).astype("category")
        return df.explode("poly").reset_index(drop=True)
