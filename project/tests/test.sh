#!/bin/bash
set +e

if [ ! -d "/workspace" ]; then
    echo "Error: /workspace directory not found."
    exit 1
fi

cd /workspace
python -m pytest /tests/ -rA

if [ $? -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi
