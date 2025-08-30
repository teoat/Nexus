# Nexus Platform - Python Environment Activation Script (PowerShell)
# This script activates the nexus_env virtual environment

# Script location
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$NEXUS_ENV_PATH = Join-Path -Path $SCRIPT_DIR -ChildPath "nexus_env"

# Check if the environment exists
if (-not (Test-Path -Path $NEXUS_ENV_PATH)) {
    Write-Host "❌ Error: nexus_env not found at $NEXUS_ENV_PATH" -ForegroundColor Red
    Write-Host "Creating new environment with Python 3.12..." -ForegroundColor Yellow
    
    # Check if Python 3.12 is available
    try {
        $pythonVersion = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
        if ($pythonVersion -eq "3.12") {
            python -m venv $NEXUS_ENV_PATH
            Write-Host "✅ Created new environment at $NEXUS_ENV_PATH" -ForegroundColor Green
        } else {
            Write-Host "❌ Error: Python 3.12 not found. Current version: $pythonVersion" -ForegroundColor Red
            Write-Host "Please install Python 3.12 and try again." -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "❌ Error: Python not found or could not determine version." -ForegroundColor Red
        Write-Host "Please install Python 3.12 and try again." -ForegroundColor Red
        exit 1
    }
    
    # Install requirements
    $requirementsPath = Join-Path -Path $SCRIPT_DIR -ChildPath "requirements.txt"
    if (Test-Path -Path $requirementsPath) {
        Write-Host "Installing requirements..." -ForegroundColor Yellow
        & "$NEXUS_ENV_PATH\Scripts\pip" install -r $requirementsPath
        Write-Host "✅ Requirements installed successfully" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Warning: requirements.txt not found at $requirementsPath" -ForegroundColor Yellow
    }
}

# Activate the environment
& "$NEXUS_ENV_PATH\Scripts\Activate.ps1"

# Verify activation
if ($env:VIRTUAL_ENV -like "*nexus_env*") {
    Write-Host "✅ nexus_env activated successfully" -ForegroundColor Green
    Write-Host "Python Version: $(python --version)" -ForegroundColor Cyan
    Write-Host "Environment Path: $env:VIRTUAL_ENV" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🚀 Ready for Nexus Platform development" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to activate nexus_env" -ForegroundColor Red
    exit 1
}
