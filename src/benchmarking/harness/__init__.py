from benchmarking.harness.python_flint import ID as python_flint_id
from benchmarking.harness.sympy import ID as sympy_id
from benchmarking.harness.dummy import ID as dummy_id


harnesses = {
    "python": (python_flint_id | sympy_id | dummy_id),
    "external": {}
}

__all__ = ["harnesses"]
