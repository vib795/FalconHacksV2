#!/bin/bash

# Check the operating system
if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
    # Linux or macOS
    python3 password-manager.py
fi
