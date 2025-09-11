#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🚀 Nexus Platform Startup Script
Simple startup script for the Nexus Platform
"""

import sys
import os
import uvicorn
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment variables
os.environ.setdefault("APP_ENV", "development")
os.environ.setdefault("DEBUG_MODE", "True")
os.environ.setdefault("LOG_LEVEL", "INFO")
os.environ.setdefault("DATABASE_URL", "sqlite:///./nexus_dev.db")
os.environ.setdefault("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-this-in-production")
os.environ.setdefault("SECRET_KEY", "your-super-secret-key-change-this-in-production")

if __name__ == "__main__":
    print("🚀 Starting Nexus Platform...")
    print("📍 Environment: Development")
    print("🌐 Server: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "main_enhanced:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Nexus Platform...")
    except Exception as e:
        print(f"❌ Error starting Nexus Platform: {e}")
        sys.exit(1)
