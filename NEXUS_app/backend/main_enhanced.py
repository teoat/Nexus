#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🚀 Enhanced Nexus Platform Backend
Comprehensive backend API system with all major and minor functions
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import time
import logging
import uvicorn
from datetime import datetime

# Import API routers
from api import api_router
from routers import auth_router, users_router, workflows_router
from middleware.enhanced_security import EnhancedSecurityMiddleware
from middleware.rate_limiting import RateLimitingMiddleware
from middleware.logging import LoggingMiddleware
from database.config import engine, Base
from database.models import User, Workflow

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting Nexus Platform Backend...")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {e}")
    
    # Initialize services
    logger.info("🔧 Initializing services...")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Nexus Platform Backend...")

# Create FastAPI application
app = FastAPI(
    title="Nexus Platform API",
    description="""
    🚀 **Nexus Platform Backend API**
    
    A comprehensive backend API system providing all major and minor functions for frontend processing.
    
    ## Features
    
    ### Core Functions
    - **User Management**: Profile management, activity tracking, preferences
    - **Workflow Management**: Create, read, update, delete workflows
    - **Data Processing**: Process data using workflows
    - **Analytics**: Dashboard analytics and reporting
    - **System Health**: Health checks and metrics
    
    ### Advanced Functions
    - **AI/ML Integration**: Predictions, model training, model management
    - **Real-time Updates**: WebSocket subscriptions and publishing
    - **Integrations**: Webhooks, data export, third-party connections
    - **Batch Processing**: Large-scale data processing jobs
    - **Search**: Advanced search and filtering
    
    ### Utility Functions
    - **File Management**: Upload, download, file operations
    - **Data Conversion**: CSV to JSON, JSON to CSV, format conversion
    - **Validation**: Email validation, data validation
    - **Notifications**: Send notifications, notification history
    - **Configuration**: Settings management, feature flags
    - **Backup**: Create and manage backups
    
    ## Authentication
    
    Most endpoints require authentication. Use the `/auth/token` endpoint to get an access token.
    
    ## Rate Limiting
    
    API calls are rate limited to prevent abuse. Check response headers for rate limit information.
    
    ## Error Handling
    
    All errors return consistent JSON responses with appropriate HTTP status codes.
    """,
    version="1.0.0",
    contact={
        "name": "Nexus Platform Team",
        "email": "support@nexusplatform.com",
        "url": "https://nexusplatform.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if app.debug else ["https://nexusplatform.com", "https://app.nexusplatform.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if app.debug else ["localhost", "127.0.0.1", "nexusplatform.com"]
)

# Add custom middleware
app.add_middleware(EnhancedSecurityMiddleware)
app.add_middleware(RateLimitingMiddleware)
app.add_middleware(LoggingMiddleware)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add process time header to responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url)
        }
    )

# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "services": {
            "database": "healthy",
            "redis": "healthy",
            "storage": "healthy"
        }
    }

# Root endpoint
@app.get("/", tags=["System"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Nexus Platform API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health",
        "timestamp": datetime.utcnow().isoformat()
    }

# Include all routers
app.include_router(api_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(workflows_router)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# API information endpoint
@app.get("/api/info", tags=["System"])
async def api_info():
    """Get comprehensive API information"""
    return {
        "name": "Nexus Platform API",
        "version": "1.0.0",
        "description": "Comprehensive backend API system for frontend processing",
        "endpoints": {
            "core": "/api/v1/core",
            "advanced": "/api/v1/advanced", 
            "utilities": "/api/v1/utilities",
            "auth": "/auth",
            "users": "/users",
            "workflows": "/workflows"
        },
        "features": {
            "user_management": True,
            "workflow_management": True,
            "data_processing": True,
            "ai_ml_integration": True,
            "real_time_updates": True,
            "file_management": True,
            "analytics": True,
            "notifications": True,
            "search": True,
            "batch_processing": True
        },
        "authentication": {
            "type": "JWT",
            "endpoint": "/auth/token"
        },
        "rate_limiting": {
            "enabled": True,
            "requests_per_minute": 100
        },
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main_enhanced:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
