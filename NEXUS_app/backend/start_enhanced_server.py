#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🚀 Enhanced Nexus Platform Server Startup
Start the enhanced backend server with all API functions
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

def start_enhanced_server():
    """Start the enhanced Nexus Platform server"""
    
    # Check if enhanced main exists
    enhanced_main_path = backend_dir / "main_enhanced.py"
    if not enhanced_main_path.exists():
        print("❌ Enhanced main file not found. Please ensure main_enhanced.py exists.")
        return
    
    print("🚀 Starting Enhanced Nexus Platform Backend Server...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔧 ReDoc Documentation: http://localhost:8000/redoc")
    print("📊 API Info: http://localhost:8000/api/info")
    print("❤️ Health Check: http://localhost:8000/health")
    print("\n" + "="*60)
    
    # Start the server
    uvicorn.run(
        "main_enhanced:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    start_enhanced_server()
