import itertools
import random
import logging


logger = logging.getLogger(__name__)

poly_gen_format = """\
Generating {number} polynomials with:
\tGenerators: {gens}
\tCoefficients in: {coeff_range}
\tExponents in: {exp_range}
\tSparsity: {sparsity}% ({num_terms} terms)"""


class PolynomialGenerator:
    def __init__(
        self,
        *,
        generators: list[range],
        sparsity: list[range],
        coefficients: list[range],
        exponents: list[range],
        number: int,
        seed: int,
    ):
        self.gens = generators
        self.sparity = sparsity
        self.coefficients = coefficients
        self.exponents = exponents
        self.number = number
        self.rng = random.Random(seed)

    def generate(self):
        self.results = []
        for gen_range, sparsity_range, coeff_range, exp_range in itertools.product(
            self.gens, self.sparity, self.coefficients, self.exponents
        ):
            for gens in gen_range:
                for sparsity in sparsity_range:
                    num_terms = int(gens * len(exp_range) * (100 - sparsity) / 100.0)
                    logger.info(
                        poly_gen_format.format(
                            number=self.number,
                            gens=gens,
                            sparsity=sparsity,
                            num_terms=num_terms,
                            coeff_range=coeff_range,
                            exp_range=exp_range,
                        )
                    )

                    polys = []
                    for _ in range(self.number):
                        poly = []
                        for _ in range(num_terms):
                            exp_vec = tuple(
                                self.rng.randrange(exp_range.start, exp_range.stop, exp_range.step) for _ in range(gens)
                            )
                            coeff = self.rng.randrange(coeff_range.start, coeff_range.stop, coeff_range.step)
                            poly.append((exp_vec, coeff))

                        if len(poly) != num_terms:
                            logger.warn("polynomial generated with less terms than requested")

                        polys.append(poly)

                    if len(polys) != self.number:
                        logger.warn("generated less polynomials than requested")
                    self.results.append(
                        (
                            (
                                gens,
                                sparsity,
                                (exp_range.start, exp_range.stop, exp_range.step),
                                (coeff_range.start, coeff_range.stop, coeff_range.step),
                            ),
                            polys,
                        )
                    )

    @staticmethod
    def parse(polys):
        results = {}
        for config, poly_list in polys:
            # gens, sparsity, exp_range, coeff_range
            config = (*config[:2], range(*config[2]), range(*config[3]))
            res = []
            for poly in poly_list:
                res.append({tuple(k): v for k, v in poly})

            results[config] = res

        return results

