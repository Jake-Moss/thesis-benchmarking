#include <x86intrin.h> // For __rdtsc()
#include <cpuid.h>
#include <stdint.h>

#define ITERATIONS 3000
#define FACTOR 2
#define VEC_LENGTH 1000
#define TRIALS 10

#if 1
#define LFENCE "lfence\n\t"

#define CPUID "cpuid\n\t"
#else
#define LFENCE
#define CPUID
#endif

static inline uint64_t rdtsc_serial() {
  unsigned int hi, lo;
  asm volatile(CPUID LFENCE "rdtsc\n\t" LFENCE "mov %%edx, %0\n\t"
                            "mov %%eax, %1\n\t"
               : "=r"(hi), "=r"(lo)
               :
               : "%rax", "%rbx", "%rcx", "%rdx");

  return ((uint64_t)hi << 32) | lo;
}
