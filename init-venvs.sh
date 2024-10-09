#/bin/env bash

export PYTHON312_VENV=$(readlink -f .venv-312)
export PYTHON313_VENV=$(readlink -f .venv-313)
export PYTHON313_JIT_VENV=$(readlink -f .venv-313-jit)

if test ! -d $PYTHON312_VENV; then
    python3.12 -m venv $PYTHON312_VENV
    . $PYTHON312_VENV/bin/activate $PYTHON312_VENV/
    pip install --config-settings=setup-args="-Dflint_version_check=false" ./libs/python-flint/
    pip install ./libs/sympy/
    pip install gmpy2==2.2.1 memray
    pip install -e .
    deactivate
    fix-python --venv $PYTHON312_VENV
fi

if test ! -d $PYTHON313_VENV; then
    python3.13 -m venv $PYTHON313_VENV
    . $PYTHON313_VENV/bin/activate $PYTHON313_VENV/
    pip install --config-settings=setup-args="-Dflint_version_check=false" ./libs/python-flint/
    pip install ./libs/sympy/
    pip install gmpy2==2.2.1
    pip install memray
    pip install -e .
    deactivate
    fix-python --venv $PYTHON313_VENV
fi

# if test ! -d $PYTHON313_JIT_VENV; then
#     python3.13 -m venv $PYTHON313_JIT_VENV
#     . $PYTHON313_JIT_VENV/bin/activate $PYTHON313_JIT_VENV/
#     pip install ./libs/python-flint/
#     pip install ./libs/sympy/
#     pip install gmpy2==2.2.1
#     pip install ./libs/memray-1.13.4-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
#     pip install -e .
#     deactivate
#     fix-python --venv $PYTHON313_JIT_VENV
# fi
