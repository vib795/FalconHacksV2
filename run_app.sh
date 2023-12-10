#!/bin/bash

# Check the operating system
if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
    # Linux or macOS
    python3 password-manager.py
elif [[ "$OSTYPE" == "msys"* ]]; then
    # Windows using Git Bash
    python3 password-manager.py
else
    # Windows using PowerShell
    powershell.exe -Command "& {python3 password-manager.py}"
    # cmd.exe /c "python3 password-manager.py"
fi
