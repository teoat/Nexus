#!/bin/bash
# ===============================================================================
# NEXUS PLATFORM - UNIFIED PYTHON LAUNCHER (Unix/Mac)
# Single Source of Truth for Python Execution
# ===============================================================================

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_PATH="$SCRIPT_DIR/nexus_env"
PYTHON_EXE="$ENV_PATH/bin/python"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -f "$PYTHON_EXE" ]; then
    echo -e "${RED}❌ Nexus Python environment not found${NC}"
    echo -e "Run ./activate_nexus_env.sh first to set up the environment"
    exit 1
fi

# Execute Python with all passed arguments
exec "$PYTHON_EXE" "$@"
