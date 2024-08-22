;;; Directory Local Variables            -*- no-byte-compile: t -*-
;;; For more information see (info "(emacs) Directory Variables")

((nil . ((compile-command . "python -c \"from src.benchmarking.cli import *; main()\" ./polynomial_db/polys.pickle ./polynomial_db/run_list.pickle /tmp/output.pickle --libraries python-flint --venvs .venv-312 --cpu-profiling -vv "))))
