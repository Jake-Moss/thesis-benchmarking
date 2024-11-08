cdef extern from "small_int_benchmark.h" nogil:
    int ITERATIONS
    int FACTOR
    int VEC_LENGTH
    int TRIALS
    unsigned long long rdtsc_serial_start()
    unsigned long long rdtsc_serial_end()


def benchmark_single():
    cdef:
        object x = int()
        object two = int(2)
        unsigned long long cycle_start, cycle_end

    res = [0] * ITERATIONS

    for i in range(100):
        x *= two
    x = 1
    rdtsc_serial_start();
    rdtsc_serial_end()

    for i in range(ITERATIONS):
        cycle_start = rdtsc_serial_start();

        x *= two

        cycle_end = rdtsc_serial_end();
        res[i] = cycle_end - cycle_start

    print(res)

def benchmark_vector():
    cdef:
        object xs = [int(1)] * VEC_LENGTH
        object two = int(2)
        unsigned long long cycle_start, cycle_end

    res = [0] * ITERATIONS

    for i in range(100):
        xs[i] *= two

    for i in range(VEC_LENGTH):
        xs[i] = int(1)

    rdtsc_serial_start();
    rdtsc_serial_end()

    for k in range(ITERATIONS):
        cycle_start = rdtsc_serial_start();

        for i in range(VEC_LENGTH):
            xs[i] *= two

        cycle_end = rdtsc_serial_end();
        res[k] = cycle_end - cycle_start

    print(res)

def main():
    for i in range(TRIALS):
        benchmark_single()
        benchmark_vector()

# Local Variables:
# compile-command: "cd src/benchmarking/small_int/ && python setup.py build_ext --inplace"
# End:
