from benchmarking.harness.python_flint_wrapper import ID as python_flint_id
from benchmarking.harness.sympy_wrapper import ID as sympy_id
from benchmarking.harness.sagemath_wrapper import ID as sagemath_id
from benchmarking.harness.mathematica_wrapper import ID as mathematica_id
from benchmarking.harness.dummy import ID as dummy_id


harnesses = {
    "python": (python_flint_id | sympy_id | dummy_id),
    "sagemath": sagemath_id,
    "mathematica": mathematica_id,
}

__all__ = ["harnesses"]
