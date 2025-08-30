#!/bin/bash

# Nexus Platform - Python Launcher Script
# This script runs Python from the nexus_env environment

# Script location
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
NEXUS_ENV_PATH="$SCRIPT_DIR/nexus_env"
PYTHON_PATH="$NEXUS_ENV_PATH/bin/python"

# Check if the environment exists
if [ ! -d "$NEXUS_ENV_PATH" ]; then
    echo "❌ Error: nexus_env not found at $NEXUS_ENV_PATH"
    echo "Please run './activate_nexus_env.sh' to create the environment first."
    exit 1
fi

# Check if python executable exists
if [ ! -f "$PYTHON_PATH" ]; then
    echo "❌ Error: Python executable not found at $PYTHON_PATH"
    echo "The virtual environment may be corrupted. Please recreate it with './activate_nexus_env.sh'"
    exit 1
fi

# Run the command
echo "🚀 Running with Nexus Python ($("$PYTHON_PATH" --version))"
"$PYTHON_PATH" "$@"
