from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import time
import uvicorn

from core.config import settings, CORS_CONFIG
from core.database import create_tables, check_connection
from core.middleware.security import SecurityMiddleware
from core.middleware.rate_limiting import RateLimitingMiddleware
from core.middleware.logging import LoggingMiddleware
from api import auth, users, automation, chat, health, sync, sync_simple, nexus_sync, working_sync
from core.monitoring.observability import setup_monitoring

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.
    """
    # Startup
    logger.info("Starting Nexus Platform API...")
    
    # Check database connection
    if not check_connection():
        logger.error("Database connection failed")
        raise Exception("Database connection failed")
    
    # Create database tables
    try:
        create_tables()
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise
    
    # Setup monitoring
    try:
        setup_monitoring(app)
        logger.info("Monitoring setup completed")
    except Exception as e:
        logger.warning(f"Monitoring setup failed: {e}")
    
    logger.info("Nexus Platform API started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Nexus Platform API...")

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Nexus Platform API - Enterprise-grade security and monitoring platform",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    **CORS_CONFIG
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.DEBUG else ["localhost", "127.0.0.1"]
)

# Add custom middleware
app.add_middleware(SecurityMiddleware)
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

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail} - {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": time.time()
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation exceptions."""
    logger.warning(f"Validation error: {exc.errors()} - {request.url}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "details": exc.errors(),
            "status_code": 422,
            "timestamp": time.time()
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc} - {request.url}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": time.time()
        }
    )

# Health check endpoints
@app.get("/health")
async def health_check():
    """Basic health check."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.APP_VERSION
    }

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with dependencies."""
    from core.database import get_connection_info, get_database_health
    
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": get_database_health(),
        "database_connection": get_connection_info()
    }
    
    # Check if any critical service is unhealthy
    if health_status["database"]["status"] != "healthy":
        health_status["status"] = "unhealthy"
        return JSONResponse(status_code=503, content=health_status)
    
    return health_status

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to Nexus Platform API",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs" if settings.DEBUG else "Documentation not available in production",
        "health_check": "/health"
    }

# Include API routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(automation.router, prefix=settings.API_V1_STR)
app.include_router(chat.router, prefix=settings.API_V1_STR)
app.include_router(health.router)
app.include_router(sync.router, prefix=settings.API_V1_STR)
app.include_router(sync_simple.router, prefix=settings.API_V1_STR)
app.include_router(nexus_sync.router, prefix=settings.API_V1_STR)
app.include_router(working_sync.router)

# API information endpoint
@app.get("/api/info")
async def api_info():
    """Get API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "api_version": settings.API_V1_STR,
        "features": {
            "authentication": True,
            "user_management": True,
            "automation": True,
            "chat": True,
            "monitoring": True,
            "security": True,
            "rate_limiting": True
        },
        "endpoints": {
            "auth": f"{settings.API_V1_STR}/auth",
            "users": f"{settings.API_V1_STR}/users",
            "automation": f"{settings.API_V1_STR}/automation",
            "chat": f"{settings.API_V1_STR}/chat",
            "health": "/api/v1/health",
            "docs": "/docs" if settings.DEBUG else None
        }
    }

# Development server
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )