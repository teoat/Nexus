#!/bin/bash

# Nexus Platform - Setup Script
# This script sets up the Nexus Platform environment

# Script location
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "🚀 Nexus Platform - Setup Script"
echo "================================="
echo "Project root: $PROJECT_ROOT"
echo

# Check prerequisites
echo "🔍 Checking prerequisites..."
echo

# Check Python version
if command -v python3.12 &> /dev/null; then
    PYTHON_VERSION=$(python3.12 --version)
    echo "✅ Python 3.12 found: $PYTHON_VERSION"
else
    echo "❌ Python 3.12 not found"
    echo "Please install Python 3.12 and try again"
    exit 1
fi

# Check Docker
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo "✅ Docker found: $DOCKER_VERSION"
else
    echo "❌ Docker not found"
    echo "Please install Docker and try again"
    exit 1
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    echo "✅ Docker Compose found: $COMPOSE_VERSION"
else
    echo "❌ Docker Compose not found"
    echo "Please install Docker Compose and try again"
    exit 1
fi

echo
echo "🌱 Creating Python virtual environment..."
echo

# Create Python virtual environment
cd "$PROJECT_ROOT"
if [ ! -d "nexus_env" ]; then
    python3.12 -m venv nexus_env
    echo "✅ Virtual environment created at $PROJECT_ROOT/nexus_env"
else
    echo "ℹ️ Virtual environment already exists at $PROJECT_ROOT/nexus_env"
fi

# Make activation scripts executable
chmod +x "$PROJECT_ROOT/activate_nexus_env.sh"
chmod +x "$PROJECT_ROOT/nexus_python.sh"
echo "✅ Made activation scripts executable"

# Install requirements
echo
echo "📦 Installing Python dependencies..."
echo
"$PROJECT_ROOT/nexus_env/bin/pip" install -r "$PROJECT_ROOT/requirements.txt"
echo "✅ Python dependencies installed"

# Create required directories
echo
echo "📂 Creating required directories..."
echo
mkdir -p "$PROJECT_ROOT/config/prometheus" \
         "$PROJECT_ROOT/config/grafana/provisioning" \
         "$PROJECT_ROOT/config/alertmanager" \
         "$PROJECT_ROOT/docker/data/postgres/init" \
         "$PROJECT_ROOT/docker/data/neo4j/import"
echo "✅ Required directories created"

# Set up Docker environments
echo
echo "🐳 Setting up Docker environments..."
echo
# Create empty Dockerfiles for services
for service in api-gateway ai-engine fraud-detection forensic-analysis frenly-ai; do
    touch "$PROJECT_ROOT/docker/services/$service/Dockerfile"
    echo "# Nexus Platform - $service Dockerfile" > "$PROJECT_ROOT/docker/services/$service/Dockerfile"
    echo "FROM python:3.12-slim" >> "$PROJECT_ROOT/docker/services/$service/Dockerfile"
    echo "✅ Created placeholder Dockerfile for $service"
done

echo
echo "🎉 Setup completed successfully!"
echo
echo "Next steps:"
echo "1. Activate the Python environment: ./activate_nexus_env.sh"
echo "2. Start the Docker services: docker-compose up -d"
echo "3. Open http://localhost:8000 in your browser"
echo
echo "For more information, see the README.md file."
