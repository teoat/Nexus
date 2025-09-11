#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🚀 Nexus Platform Production Startup Script
Comprehensive startup script with environment management
"""

import os
import sys
import subprocess
import signal
import time
from pathlib import Path

def kill_port(port):
    """
    Kill Port
    
    
    Args:
        port: Description of port

    Example:
        TBD: Add usage example
    """
    try:
        result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    subprocess.run(['kill', '-9', pid], capture_output=True)
                    print(f"✅ Killed process {pid} on port {port}")
    except Exception as e:
        print(f"⚠️ Could not kill processes on port {port}: {e}")

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        print("✅ All dependencies are available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def start_application():
    """Start the Nexus Platform application"""
    print("🚀 Starting Nexus Platform...")
    print("=" * 50)
    
    # Set environment variables
    os.environ.update({
        "APP_ENV": "development",
        "DEBUG_MODE": "True",
        "LOG_LEVEL": "INFO",
        "DATABASE_URL": "sqlite:///./nexus_dev.db",
        "JWT_SECRET_KEY": "your-super-secret-jwt-key-change-this-in-production",
        "SECRET_KEY": "your-super-secret-key-change-this-in-production",
        "CORS_ORIGINS": "http://localhost:3000,http://localhost:8080,http://127.0.0.1:3000"
    })
    
    # Kill any existing processes on port 8000
    print("🧹 Cleaning up port 8000...")
    kill_port(8000)
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Please install dependencies first:")
        print("   pip install -r requirements_core.txt")
        return False
    
    # Start the application
    try:
        import uvicorn
        from simple_app import app
        
        print("🌐 Server: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
        print("🔍 Health Check: http://localhost:8000/health")
        print("=" * 50)
        
        uvicorn.run(
            "simple_app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Nexus Platform...")
    except Exception as e:
        print(f"❌ Error starting Nexus Platform: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = start_application()
    sys.exit(0 if success else 1)
