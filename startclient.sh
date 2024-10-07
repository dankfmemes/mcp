#!/bin/bash

if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    if [ ! -d "./env" ]; then
        echo "Virtual environment not found!"
        exit 1
    fi
    source ./env/bin/activate
else
    echo "Already in a virtual environment: $VIRTUAL_ENV"
fi

if [ ! -f "runtime/startclient.py" ]; then
    echo "Python script not found!"
    deactivate
    exit 1
fi

python runtime/startclient.py "$@"
