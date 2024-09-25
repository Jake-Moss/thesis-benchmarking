#include <stdio.h>

#include "gmp.h"
#include "flint/flint.h"
#include "flint/fmpz.h"
#include "flint/fmpz_vec.h"

#include "small_int_benchmark.h"

void benchmark_single(void) {
  unsigned long long cycle_start, cycle_end;
  int res[ITERATIONS] = {0};

  /* ----- FLINT ----- */
  fmpz_t x;
  fmpz_init_set_si(x, 1);

  // Warm up, get the function in cache
  for (int i = 0; i < 100; i++) {
    fmpz_mul_si(x, x, FACTOR);
  }
  fmpz_clear(x);
  fmpz_init_set_si(x, 1);
  rdtsc_serial_start();
  rdtsc_serial_end();

  // https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html
  // The processor monotonically increments the time-stamp counter MSR every
  // clock cycle and resets it to 0 whenever the processor is reset. See “Time
  // Stamp Counter” in Chapter 18 of the Intel® 64 and IA-32 Architectures
  // Software Developer’s Manual, Volume 3B, for specific details of the time
  // stamp counter behavior.
  //
  // Page 1763 Intel® 64 and IA-32 Architectures Software Developer’s Manual
  // Combined Volumes: 1, 2A, 2B, 2C, 2D, 3A, 3B, 3C, 3D, and 4
  for (int i = 0; i < ITERATIONS; i++) {
    cycle_start = rdtsc_serial_start();

    fmpz_mul_si(x, x, FACTOR);

    cycle_end = rdtsc_serial_end();

    res[i] = cycle_end - cycle_start;
  }

  printf("[");
  for (int i = 0; i < ITERATIONS - 1; i++) {
    printf("%d, ", res[i]);
  }
  printf("%d]\n", res[ITERATIONS - 1]);

  // fmpz_print(x); flint_printf("\n");
  fmpz_clear(x);

  /* ----- GMP ----- */
  mpz_t y;
  mpz_init(y);
  mpz_set_si(y, 1);

  for (int i = 0; i < 100; i++) {
    mpz_mul_si(y, y, FACTOR);
  }
  mpz_clear(y);
  mpz_init(y);
  mpz_set_si(y, 1);

  rdtsc_serial_start();
  rdtsc_serial_end();

  for (int i = 0; i < ITERATIONS; i++) {
    cycle_start = rdtsc_serial_start();

    mpz_mul_si(y, y, FACTOR);

    cycle_end = rdtsc_serial_end();

    res[i] = cycle_end - cycle_start;
  }

  printf("[");
  for (int i = 0; i < ITERATIONS - 1; i++) {
    printf("%d, ", res[i]);
  }
  printf("%d]\n", res[ITERATIONS - 1]);

  // gmp_printf("%Zd\n", y);

  mpz_clear(y);
}

void benchmark_vec(void) {
  unsigned long long cycle_start, cycle_end;
  int res[ITERATIONS] = {0};

  /* ----- FLINT ----- */
  fmpz xs[VEC_LENGTH] = {0};
  for (int i = 0; i < VEC_LENGTH; i++) {
    fmpz_init_set_si(xs + i, 1);
  }

  // Warm up, get the function in cache
  for (int i = 0; i < VEC_LENGTH; i++) {
    fmpz_mul_si(xs + i, xs + 1, 1);
  }
  rdtsc_serial_start();
  rdtsc_serial_end();

  // https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html
  // The processor monotonically increments the time-stamp counter MSR every
  // clock cycle and resets it to 0 whenever the processor is reset. See “Time
  // Stamp Counter” in Chapter 18 of the Intel® 64 and IA-32 Architectures
  // Software Developer’s Manual, Volume 3B, for specific details of the time
  // stamp counter behavior.
  //
  // Page 1763 Intel® 64 and IA-32 Architectures Software Developer’s Manual
  // Combined Volumes: 1, 2A, 2B, 2C, 2D, 3A, 3B, 3C, 3D, and 4
  for (int k = 0; k < ITERATIONS; k++) {
    cycle_start = rdtsc_serial_start();

    for (int i = 0; i < VEC_LENGTH; i++) {
      fmpz_mul_si(xs + i, xs + 1, FACTOR);
    }

    cycle_end = rdtsc_serial_end();

    res[k] = cycle_end - cycle_start;
  }

  printf("[");
  for (int i = 0; i < ITERATIONS - 1; i++) {
    printf("%d, ", res[i]);
  }
  printf("%d]\n", res[ITERATIONS - 1]);

  // fmpz_print(x); flint_printf("\n");
  for (int i = 0; i < VEC_LENGTH; i++) {
    fmpz_clear(xs + i);
  }

  /* ----- GMP ----- */
  mpz_t ys[VEC_LENGTH] = { 0 };
  for (int i = 0; i < VEC_LENGTH; i++) {
      mpz_init(ys[i]);
      mpz_set_si(ys[i], 1);
  }

  for (int i = 0; i < VEC_LENGTH; i++) {
    mpz_mul_si(ys[i], ys[i], 1);
  }
  rdtsc_serial_start();
  rdtsc_serial_end();

  for (int i = 0; i < ITERATIONS; i++) {
    cycle_start = rdtsc_serial_start();

    for (int i = 0; i < VEC_LENGTH; i++) {
        mpz_mul_si(ys[i], ys[i], FACTOR);
    }

    cycle_end = rdtsc_serial_end();

    res[i] = cycle_end - cycle_start;
  }

  printf("[");
  for (int i = 0; i < ITERATIONS - 1; i++) {
    printf("%d, ", res[i]);
  }
  printf("%d]\n", res[ITERATIONS - 1]);

  // gmp_printf("%Zd\n", y);

  for (int i = 0; i < VEC_LENGTH; i++) {
      mpz_clear(ys[i]);
  }
}

int main(void) {
    for (int i = 0; i < TRIALS; i++) {
        benchmark_single();
        benchmark_vec();
    }
  return 0;
}

/* Local Variables: */
/* compile-command: "gcc src/benchmarking/small_int/small_int_benchmark_flint_gmp.c -lflint -lgmp -march=native -O3 && ./a.out > small_int_benchmark.txt" */
/* End: */
