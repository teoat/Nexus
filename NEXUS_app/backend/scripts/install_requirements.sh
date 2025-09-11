#!/bin/bash
# NEXUS Requirements Installation Script

echo "🚀 Activating NEXUS environment and installing requirements..."

# Activate the environment
source ./activate_nexus_env.sh

# Check if activation was successful
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Failed to activate environment"
    exit 1
fi

echo "✅ Environment activated: $VIRTUAL_ENV"
echo "🐍 Python: $(python --version)"
echo "📦 Pip: $(pip --version)"

# Upgrade pip first
echo "�� Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing requirements from requirements.txt..."
pip install -r requirements.txt

# Verify installation
echo "✅ Installation complete!"
echo "🔍 Verifying key packages..."

python -c "
try:
    import fastapi
    print('✅ FastAPI installed')
except ImportError:
    print('❌ FastAPI not found')

try:
    import sqlalchemy
    print('✅ SQLAlchemy installed')
except ImportError:
    print('❌ SQLAlchemy not found')

try:
    import pydantic
    print('✅ Pydantic installed')
except ImportError:
    print('❌ Pydantic not found')

try:
    import requests
    print('✅ Requests installed')
except ImportError:
    print('❌ Requests not found')
"

echo "🎉 NEXUS environment setup complete!"
