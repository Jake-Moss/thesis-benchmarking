#include "flint/flint.h"
#include "flint/fmpz_mpoly.h"
#include "flint/mpoly.h"
#include <stdio.h>

#define ITERATIONS 62 * 2
#define GENS 5

void number_of_bits(void) {
  unsigned long long cycle_start, cycle_end;
  fmpz_mpoly_t x;
  fmpz_mpoly_ctx_t ctx;

  const char *vars[] = {"x"};

  ulong ui_exps[GENS] = { 0 };
  fmpz fmpz_exps[GENS] = { 0 };

  fmpz_mpoly_ctx_init(ctx, GENS, ORD_LEX);
  fmpz_mpoly_init(x, ctx);
  fmpz_mpoly_gen(x, 0, ctx);
  ulong res[ITERATIONS] = {0};
  ulong res2[ITERATIONS] = {0};

  for (int i = 0; i < ITERATIONS; i++) {
    /* fmpz_mpoly_print_pretty(x, vars, ctx); */
    /* flint_printf("\n"); */
    if (!fmpz_mpoly_pow_ui(x, x, 2, ctx)) {
      flint_printf("unreasonably large polynomial: ");
      break;
    }

    res[i] = x->bits;
    res2[i] = x->alloc;
    /* if (i > 1 && res[i - 1] != res[i]) { */
    /*     flint_printf("bits changed\n"); */
    /* } */
  }

  printf("[%lu, ", res[0]);
  for (int i = 1; i < ITERATIONS; i++) {
    if (res[i - 1] != res[i]) {
        printf("%lu, ", res[i]);
    }
  }
  printf("]\n");

  printf("[");
  for (int i = 0; i < FLINT_BITS; i++) {
      printf("%ld, ", ctx->minfo->lut_words_per_exp[i]);
  }
  printf("%ld]\n", ctx->minfo->lut_words_per_exp[FLINT_BITS - 1]);

  printf("[");
  for (int i = 0; i < FLINT_BITS; i++) {
      printf("%u, ", ctx->minfo->lut_fix_bits[i]);
  }
  printf("%u]\n", ctx->minfo->lut_fix_bits[FLINT_BITS - 1]);
}

int main(void) {
  number_of_bits();
  return 0;
}

/* Local Variables: */
/* compile-command: "gcc number_of_bits_per_exp.c -lflint -O3 && ./a.out > number_of_bits_per_exp.txt" */
/* End: */
