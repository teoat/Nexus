#!/bin/bash
# ===============================================================================
# NEXUS PLATFORM - SHELL PROFILE CONFIGURATION
# Add this to your .bashrc, .zshrc, or .profile for automatic nexus_env usage
# ===============================================================================

# NEXUS Environment Auto-Activation
export NEXUS_PROJECT_ROOT="/Users/Arief/Desktop/Nexus"
export NEXUS_ENV_PATH="$NEXUS_PROJECT_ROOT/nexus_env"

# Auto-activate nexus_env when entering the project directory
if [[ "$PWD" == "$NEXUS_PROJECT_ROOT"* ]] && [ -d "$NEXUS_ENV_PATH" ]; then
    if [[ "$VIRTUAL_ENV" != "$NEXUS_ENV_PATH" ]]; then
        echo "🚀 Auto-activating NEXUS environment..."
        source "$NEXUS_ENV_PATH/bin/activate"
    fi
fi

# NEXUS-specific aliases
alias nexus-python="$NEXUS_ENV_PATH/bin/python"
alias nexus-pip="$NEXUS_ENV_PATH/bin/pip"
alias nexus-activate="source $NEXUS_ENV_PATH/bin/activate"
alias nexus-deactivate="deactivate"

# NEXUS project navigation
alias nexus-cd="cd $NEXUS_PROJECT_ROOT"
alias nexus-app="cd $NEXUS_PROJECT_ROOT/NEXUS_app"
alias nexus-auto="cd $NEXUS_PROJECT_ROOT/automation"

# NEXUS development shortcuts
alias nexus-run="cd $NEXUS_PROJECT_ROOT && python -m uvicorn NEXUS_app.backend.main:app --reload"
alias nexus-test="cd $NEXUS_PROJECT_ROOT && python -m pytest"
alias nexus-install="cd $NEXUS_PROJECT_ROOT && pip install -r requirements.txt"
