#!/bin/bash

# Nexus Platform - Python Environment Activation Script
# This script activates the nexus_env virtual environment

# Script location
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
NEXUS_ENV_PATH="$SCRIPT_DIR/nexus_env"

# Check if the environment exists
if [ ! -d "$NEXUS_ENV_PATH" ]; then
    echo "❌ Error: nexus_env not found at $NEXUS_ENV_PATH"
    echo "Creating new environment with Python 3.12..."
    
    # Check if Python 3.12 is available
    if command -v python3.12 &> /dev/null; then
        python3.12 -m venv "$NEXUS_ENV_PATH"
        echo "✅ Created new environment at $NEXUS_ENV_PATH"
    else
        echo "❌ Error: Python 3.12 not found. Please install Python 3.12 and try again."
        exit 1
    fi
    
    # Install requirements
    if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
        echo "Installing requirements..."
        "$NEXUS_ENV_PATH/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"
        echo "✅ Requirements installed successfully"
    else
        echo "⚠️ Warning: requirements.txt not found at $SCRIPT_DIR/requirements.txt"
    fi
fi

# Activate the environment
source "$NEXUS_ENV_PATH/bin/activate"

# Verify activation
if [[ "$VIRTUAL_ENV" == *"nexus_env"* ]]; then
    echo "✅ nexus_env activated successfully"
    echo "Python Version: $(python --version)"
    echo "Environment Path: $VIRTUAL_ENV"
    echo ""
    echo "🚀 Ready for Nexus Platform development"
else
    echo "❌ Failed to activate nexus_env"
    exit 1
fi
