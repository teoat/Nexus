"""
cors Module

Cors

This module provides functionality for cors.

Classes:
    TBD: Add class descriptions

Functions:
    TBD: Add function descriptions

Example:
    TBD: Add usage example

Author: NEXUS Platform
Created: 2025-09-11
Version: 1.0.0
"""
from fastapi.middleware.cors import CORSMiddleware
import os
from typing import List

def get_cors_config() -> dict:
    """Get CORS configuration based on environment"""
    
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "production":
        # Production CORS - restrictive
        return {
            "allow_origins": [
                "https://nexusplatform.com",
                "https://www.nexusplatform.com",
                "https://app.nexusplatform.com",
            ],
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": [
                "Authorization",
                "Content-Type",
                "X-Requested-With",
                "X-API-Key",
            ],
            "expose_headers": ["X-Process-Time", "X-Rate-Limit-Remaining"],
            "max_age": 3600,
        }
    else:
        # Development CORS - permissive
        return {
            "allow_origins": [
                "http://localhost:3000",
                "http://localhost:3001",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:3001",
            ],
            "allow_credentials": True,
            "allow_methods": ["*"],
            "allow_headers": ["*"],
            "expose_headers": ["*"],
            "max_age": 3600,
        }

def setup_cors_middleware(app):
    """
    Setup Cors Middleware
    
    
    Args:
        app: Description of app

    Example:
        TBD: Add usage example
    """
    cors_config = get_cors_config()
    
    app.add_middleware(
        CORSMiddleware,
        **cors_config
    )
