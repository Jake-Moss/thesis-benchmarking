#!/usr/bin/env sh

# time python -c "from src.benchmarking.cli import *; main()" ./polynomial_db/polys.pickle ./polynomial_db/run_list.pickle ./results --libraries sagemath python-flint sympy-domains sympy-domains-gmpy sympy-domains-flint mathematica --venv .venv-312 --gc True False --cores 6 --benchmark -v --timeout 15 --repeats 1

time python -c "from src.benchmarking.cli import *; main()" ./polys.pickle ./run_list.pickle ./results --libraries sagemath python-flint sympy-domains sympy-domains-gmpy sympy-domains-flint sympy-dmp sympy-dmp-gmpy sympy-dmp-flint mathematica --venv .venv-312 --gc True False --cores 6 --benchmark -v --timeout 1 --repeats 3


# time python -c "from src.benchmarking.cli import *; main()" ./polynomial_db/polys.pickle ./polynomial_db/run_list.pickle ./results --libraries python-flint sympy-domains sympy-domains-gmpy sympy-domains-flint --venv .venv-312 --gc True --cores 6 --cpu-profiling -v --timeout 15 --repeats 1

time python -c "from src.benchmarking.cli import *; main()" ./polys.pickle ./run_list.pickle ./results --libraries python-flint sympy-domains sympy-domains-gmpy sympy-domains-flint sympy-dmp sympy-dmp-gmpy sympy-dmp-flint --venv .venv-312 --gc False --cores 6 --cpu-profiling -v --timeout 1 --repeats 1


# time python -c "from src.benchmarking.cli import *; main()" ./polynomial_db/polys.pickle ./polynomial_db/run_list.pickle ./results --libraries python-flint sympy-domains sympy-domains-gmpy sympy-domains-flint --venv .venv-312 --gc True --cores 6 --memory-profiling -v --timeout 15 --repeats 1

time python -c "from src.benchmarking.cli import *; main()" ./polys.pickle ./run_list.pickle ./results --libraries python-flint sympy-domains sympy-domains-gmpy sympy-domains-flint sympy-dmp sympy-dmp-gmpy sympy-dmp-flint --venv .venv-312 --gc False --cores 6 --memory-profiling -v --timeout 1 --repeats 1
