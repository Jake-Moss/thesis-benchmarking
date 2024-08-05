#/bin/env bash

export PYTHON311_VENV=$(readlink -f .venv-311)
export PYTHON313_VENV=$(readlink -f .venv-313)

if test ! -d $PYTHON311_VENV; then
    python3.11 -m venv $PYTHON311_VENV
    . $PYTHON311_VENV/bin/activate $PYTHON311_VENV/
    pip install ./python-flint/
    pip install ./sympy/
    pip install gmpy2==2.2.1
    deactivate
fi

if test ! -d $PYTHON313_VENV; then
    python3.13 -m venv $PYTHON313_VENV
    . $PYTHON313_VENV/bin/activate $PYTHON313_VENV/
    pip install ./python-flint/
    pip install ./sympy/
    pip install gmpy2==2.2.1
    deactivate
fi
