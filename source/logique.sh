#!/bin/bash

# Checks if python3 binary is named python or python3
if command -v python &> /dev/null; then
    PY_CMD="python"
else
    PY_CMD="python3"
fi

# Checks the python version
PY_VERSION=$($PY_CMD -c 'import sys; print(sys.version_info[0])')

# Launches the appropriate version of python script
if [ $PY_VERSION -eq 2 ]; then
    $PY_CMD logic_v2.py
else
    $PY_CMD logic_v3.py
fi
