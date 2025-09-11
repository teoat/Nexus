#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🚀 Nexus Platform API Package
Comprehensive backend API system for frontend integration
"""

from fastapi import APIRouter
from .core import core_router
from .advanced import advanced_router
from .utilities import utility_router

# Main API Router
api_router = APIRouter()

# Include all API routers
api_router.include_router(core_router)
api_router.include_router(advanced_router)
api_router.include_router(utility_router)

__version__ = "1.0.0"
__author__ = "Nexus Platform Team"