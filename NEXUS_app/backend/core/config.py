from pydantic_settings import BaseSettings
from typing import Optional, List
import os
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings."""
    
    model_config = {"extra": "ignore", "env_file": ".env", "case_sensitive": True}
    
    # Application
    APP_NAME: str = "Nexus Platform"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    log_level: str = "INFO"
    
    # API
    API_V1_STR: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    
    # Database
    DATABASE_URL: str = "postgresql://nexus_user:nexus_password@localhost:5432/nexus_platform"
    DATABASE_ECHO: bool = False
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: Optional[str] = None
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # File Upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: List[str] = ["image/jpeg", "image/png", "image/gif", "application/pdf"]
    UPLOAD_DIR: str = "uploads"
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Cache
    CACHE_TTL: int = 3600  # 1 hour
    CACHE_ENABLED: bool = True
    
    # External Services
    SENTRY_DSN: Optional[str] = None
    NEW_RELIC_LICENSE_KEY: Optional[str] = None
    

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

# Global settings instance
settings = get_settings()

class DevelopmentSettings(Settings):
    """Development environment settings."""
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    DATABASE_ECHO: bool = True
    LOG_LEVEL: str = "DEBUG"

class ProductionSettings(Settings):
    """Production environment settings."""
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    DATABASE_ECHO: bool = False
    LOG_LEVEL: str = "WARNING"

    DEBUG: bool = True
    DATABASE_ECHO: bool = False

def get_environment_settings() -> Settings:
    """Get settings based on environment."""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    else:
        return DevelopmentSettings()

# Database configuration
DATABASE_CONFIG = {
    "pool_size": 20,
    "max_overflow": 30,
    "pool_pre_ping": True,
    "pool_recycle": 3600,
    "echo": settings.DATABASE_ECHO
}

# Redis configuration
REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "db": 0,
    "password": settings.REDIS_PASSWORD,
    "decode_responses": True,
    "socket_connect_timeout": 5,
    "socket_timeout": 5,
    "retry_on_timeout": True
}

# CORS configuration
CORS_CONFIG = {
    "allow_origins": settings.BACKEND_CORS_ORIGINS,
    "allow_credentials": True,
    "allow_methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    "allow_headers": ["*"],
}

# Security configuration
SECURITY_CONFIG = {
    "secret_key": settings.SECRET_KEY,
    "algorithm": settings.ALGORITHM,
    "access_token_expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    "refresh_token_expire_days": settings.REFRESH_TOKEN_EXPIRE_DAYS,
}

# Rate limiting configuration
RATE_LIMIT_CONFIG = {
    "enabled": settings.RATE_LIMIT_ENABLED,
    "requests": settings.RATE_LIMIT_REQUESTS,
    "window": settings.RATE_LIMIT_WINDOW,
}

# Cache configuration
CACHE_CONFIG = {
    "enabled": settings.CACHE_ENABLED,
    "ttl": settings.CACHE_TTL,
    "redis_url": settings.REDIS_URL,
}

# File upload configuration
UPLOAD_CONFIG = {
    "max_file_size": settings.MAX_FILE_SIZE,
    "allowed_types": settings.ALLOWED_FILE_TYPES,
    "upload_dir": settings.UPLOAD_DIR,
}

# Monitoring configuration
MONITORING_CONFIG = {
    "enabled": settings.ENABLE_METRICS,
    "port": settings.METRICS_PORT,
    "sentry_dsn": settings.SENTRY_DSN,
    "new_relic_key": settings.NEW_RELIC_LICENSE_KEY,
}

# Email configuration
EMAIL_CONFIG = {
    "smtp_tls": settings.SMTP_TLS,
    "smtp_port": settings.SMTP_PORT,
    "smtp_host": settings.SMTP_HOST,
    "smtp_user": settings.SMTP_USER,
    "smtp_password": settings.SMTP_PASSWORD,
    "emails_from_email": settings.EMAILS_FROM_EMAIL,
    "emails_from_name": settings.EMAILS_FROM_NAME,
}

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": settings.LOG_FORMAT,
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": settings.LOG_LEVEL,
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": settings.LOG_LEVEL,
            "formatter": "detailed",
            "filename": "logs/nexus_platform.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
    },
    "loggers": {
        "": {
            "level": settings.LOG_LEVEL,
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "sqlalchemy": {
            "level": "WARNING",
            "handlers": ["console"],
            "propagate": False,
        },
    },
}

# Feature flags
FEATURE_FLAGS = {
    "enable_mfa": True,
    "enable_social_login": False,
    "enable_api_keys": True,
    "enable_audit_logging": True,
    "enable_rate_limiting": True,
    "enable_caching": True,
    "enable_metrics": True,
    "enable_tracing": True,
}

# API versioning
API_VERSIONS = {
    "v1": {
        "version": "1.0.0",
        "status": "stable",
        "deprecated": False,
    },
    "v2": {
        "version": "2.0.0",
        "status": "beta",
        "deprecated": False,
    },
}

# Health check configuration
HEALTH_CHECK_CONFIG = {
    "database": True,
    "redis": True,
    "external_services": True,
    "timeout": 5,  # seconds
}

# Backup configuration
BACKUP_CONFIG = {
    "enabled": True,
    "schedule": "0 2 * * *",  # Daily at 2 AM
    "retention_days": 30,
    "backup_dir": "backups",
    "compress": True,
}

# Notification configuration
NOTIFICATION_CONFIG = {
    "email": {
        "enabled": True,
        "templates_dir": "templates/email",
    },
    "sms": {
        "enabled": False,
        "provider": "twilio",
    },
    "push": {
        "enabled": False,
        "provider": "firebase",
    },
}
