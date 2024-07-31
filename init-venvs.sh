#/bin/env bash

export HOST_VENV=.venv-host

if test ! -d HOST_VENV; then
    python3.11 -m venv $HOST_VENV
    . $HOST_VENV/bin/activate $HOST_VENV/
    pip install -r requirements.txt
    deactivate
fi

export PYTHON311_VENV=.venv-311
export PYTHON313_VENV=.venv-313

if test ! -d $PYTHON311_VENV; then
    python3.11 -m venv $PYTHON311_VENV
    . $PYTHON311_VENV/bin/activate $PYTHON311_VENV/
    pip install ./python-flint/
    deactivate
fi

if test ! -d $PYTHON313_VENV; then
    python3.13 -m venv $PYTHON313_VENV
    . $PYTHON313_VENV/bin/activate $PYTHON313_VENV/
    pip install ./python-flint/
    deactivate
fi
