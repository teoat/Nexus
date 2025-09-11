#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
Core Configuration Module for Nexus Platform
Provides basic configuration settings and utilities.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

class Settings:
    """Basic settings for the Nexus Platform"""
    
    def __init__(self):
        """
          Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        self.workspace_path = os.getenv("NEXUS_WORKSPACE_PATH", "/tmp/nexus")
        self.debug = os.getenv("NEXUS_DEBUG", "true").lower() == "true"
        self.log_level = os.getenv("NEXUS_LOG_LEVEL", "INFO")
        self.app_name = "Nexus Platform"
        self.app_version = "1.0.0"
        self.environment = os.getenv("NEXUS_ENVIRONMENT", "development")
        
        # Additional attributes for main.py compatibility
        self.APP_NAME = self.app_name
        self.APP_VERSION = self.app_version
        self.DEBUG = self.debug
        self.ENVIRONMENT = self.environment
        self.API_V1_STR = "/api/v1"
        self.HOST = "0.0.0.0"
        self.PORT = 8000
        self.LOG_LEVEL = self.log_level

# Global settings instance
settings = Settings()

def get_config() -> Dict[str, Any]:
    """Get basic configuration"""
    return {
        "workspace_path": settings.workspace_path,
        "debug": settings.debug,
        "log_level": settings.log_level,
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "environment": settings.environment
    }

def get_workspace_path() -> str:
    """Get workspace path"""
    return settings.workspace_path

def is_debug() -> bool:
    """Check if debug mode is enabled"""
    return settings.debug

def get_log_level() -> str:
    """Get log level"""
    return settings.log_level

# CORS Configuration
CORS_CONFIG = {
    "allow_origins": ["*"],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}
