# Nexus Platform - Python Launcher Script (PowerShell)
# This script runs Python from the nexus_env environment

# Script location
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$NEXUS_ENV_PATH = Join-Path -Path $SCRIPT_DIR -ChildPath "nexus_env"
$PYTHON_PATH = Join-Path -Path $NEXUS_ENV_PATH -ChildPath "Scripts\python.exe"

# Check if the environment exists
if (-not (Test-Path -Path $NEXUS_ENV_PATH)) {
    Write-Host "❌ Error: nexus_env not found at $NEXUS_ENV_PATH" -ForegroundColor Red
    Write-Host "Please run '.\activate_nexus_env.ps1' to create the environment first." -ForegroundColor Yellow
    exit 1
}

# Check if python executable exists
if (-not (Test-Path -Path $PYTHON_PATH)) {
    Write-Host "❌ Error: Python executable not found at $PYTHON_PATH" -ForegroundColor Red
    Write-Host "The virtual environment may be corrupted. Please recreate it with '.\activate_nexus_env.ps1'" -ForegroundColor Yellow
    exit 1
}

# Run the command
$pythonVersion = & $PYTHON_PATH --version
Write-Host "🚀 Running with Nexus Python ($pythonVersion)" -ForegroundColor Green
& $PYTHON_PATH $args
