#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
⚙️ Frenly AI Configuration Management
Centralized configuration for Frenly AI service
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseSettings, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FrenlyAIConfig(BaseSettings):
    """Frenly AI service configuration"""
    
    # Service Configuration
    service_name: str = Field(default="frenly-ai", env="FRENLY_SERVICE_NAME")
    version: str = Field(default="2.0.0", env="FRENLY_VERSION")
    debug: bool = Field(default=False, env="FRENLY_DEBUG")
    log_level: str = Field(default="INFO", env="FRENLY_LOG_LEVEL")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="FRENLY_HOST")
    port: int = Field(default=8002, env="FRENLY_PORT")
    workers: int = Field(default=4, env="FRENLY_WORKERS")
    
    # Database Configuration
    database_url: str = Field(
        default="postgresql://nexus_user:nexus_password@postgres:5432/nexus_platform",
        env="DATABASE_URL"
    )
    redis_url: str = Field(
        default="redis://redis:6379/0",
        env="REDIS_URL"
    )
    
    # AI Model Configuration
    default_model: str = Field(default="gpt-3.5-turbo", env="FRENLY_DEFAULT_MODEL")
    max_tokens: int = Field(default=2048, env="FRENLY_MAX_TOKENS")
    temperature: float = Field(default=0.7, env="FRENLY_TEMPERATURE")
    
    # API Keys
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    
    # Agent Configuration
    max_concurrent_requests: int = Field(default=100, env="FRENLY_MAX_CONCURRENT")
    request_timeout: int = Field(default=30, env="FRENLY_REQUEST_TIMEOUT")
    session_timeout: int = Field(default=3600, env="FRENLY_SESSION_TIMEOUT")
    
    # Performance Configuration
    enable_caching: bool = Field(default=True, env="FRENLY_ENABLE_CACHING")
    cache_ttl: int = Field(default=300, env="FRENLY_CACHE_TTL")
    enable_metrics: bool = Field(default=True, env="FRENLY_ENABLE_METRICS")
    
    # Security Configuration
    enable_auth: bool = Field(default=True, env="FRENLY_ENABLE_AUTH")
    jwt_secret: str = Field(default="frenly-secret-key", env="FRENLY_JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", env="FRENLY_JWT_ALGORITHM")
    jwt_expiration: int = Field(default=3600, env="FRENLY_JWT_EXPIRATION")
    
    # Monitoring Configuration
    enable_health_checks: bool = Field(default=True, env="FRENLY_ENABLE_HEALTH")
    health_check_interval: int = Field(default=30, env="FRENLY_HEALTH_INTERVAL")
    enable_prometheus: bool = Field(default=True, env="FRENLY_ENABLE_PROMETHEUS")
    prometheus_port: int = Field(default=9090, env="FRENLY_PROMETHEUS_PORT")
    
    # Agent Types Configuration
    agent_types: Dict[str, Dict[str, Any]] = Field(default={
        "fraud_detection": {
            "enabled": True,
            "model": "fraud-detection-v1",
            "max_requests_per_minute": 100,
            "timeout": 30
        },
        "forensic_analysis": {
            "enabled": True,
            "model": "forensic-analysis-v1",
            "max_requests_per_minute": 50,
            "timeout": 60
        },
        "reconciliation": {
            "enabled": True,
            "model": "reconciliation-v1",
            "max_requests_per_minute": 200,
            "timeout": 45
        },
        "compliance": {
            "enabled": True,
            "model": "compliance-v1",
            "max_requests_per_minute": 75,
            "timeout": 30
        },
        "general": {
            "enabled": True,
            "model": "gpt-3.5-turbo",
            "max_requests_per_minute": 500,
            "timeout": 15
        }
    })
    
    # Workspace Configuration
    workspace_path: str = Field(default="/workspace", env="FRENLY_WORKSPACE_PATH")
    data_path: str = Field(default="/workspace/data", env="FRENLY_DATA_PATH")
    logs_path: str = Field(default="/workspace/logs", env="FRENLY_LOGS_PATH")
    
    class Config:
        """
        Config Class
        
        Config
        
        Attributes:
            TBD: Add attribute descriptions
        
        Methods:
            TBD: Add method descriptions
        
        Example:
            TBD: Add usage example
        """
        env_file = ".env"
        case_sensitive = False

# Global configuration instance
config = FrenlyAIConfig()

def get_config() -> FrenlyAIConfig:
    """Get configuration instance"""
    return config

def update_config(**kwargs) -> None:
    """Update configuration values"""
    global config
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)

def get_agent_config(agent_type: str) -> Dict[str, Any]:
    """
    Retrieve agent config
    
    
    Args:
        agent_type: Description of agent_type

    Returns:
        Unknown: Description of return value

    Example:
        TBD: Add usage example
    """
    return config.agent_types.get(agent_type, config.agent_types["general"])

def is_agent_enabled(agent_type: str) -> bool:
    """Check if agent type is enabled"""
    agent_config = get_agent_config(agent_type)
    return agent_config.get("enabled", False)

def get_agent_model(agent_type: str) -> str:
    """
    Retrieve agent model
    
    
    Args:
        agent_type: Description of agent_type

    Returns:
        str: Description of return value

    Example:
        TBD: Add usage example
    """
    agent_config = get_agent_config(agent_type)
    return agent_config.get("model", config.default_model)

def get_agent_timeout(agent_type: str) -> int:
    """
    Retrieve agent timeout
    
    
    Args:
        agent_type: Description of agent_type

    Returns:
        int: Description of return value

    Example:
        TBD: Add usage example
    """
    agent_config = get_agent_config(agent_type)
    return agent_config.get("timeout", config.request_timeout)

def get_agent_rate_limit(agent_type: str) -> int:
    """
    Retrieve agent rate limit
    
    
    Args:
        agent_type: Description of agent_type

    Returns:
        int: Description of return value

    Example:
        TBD: Add usage example
    """
    agent_config = get_agent_config(agent_type)
    return agent_config.get("max_requests_per_minute", 100)

def get_development_config() -> FrenlyAIConfig:
    """Get development configuration"""
    return FrenlyAIConfig(
        debug=True,
        log_level="DEBUG",
        workers=1,
        enable_auth=False,
        enable_metrics=False
    )

def get_production_config() -> FrenlyAIConfig:
    """Get production configuration"""
    return FrenlyAIConfig(
        debug=False,
        log_level="WARNING",
        workers=8,
        enable_auth=True,
        enable_metrics=True,
        enable_prometheus=True
    )

    return FrenlyAIConfig(
        debug=True,
        log_level="DEBUG",
        workers=1,
        enable_auth=False,
        enable_metrics=False,
        redis_url="redis://localhost:6379/1"
    )

# Configuration validation
def validate_config() -> bool:
    """Validate configuration settings"""
    try:
        # Check required fields
        assert config.service_name, "Service name is required"
        assert config.host, "Host is required"
        assert config.port > 0, "Port must be positive"
        assert config.database_url, "Database URL is required"
        assert config.redis_url, "Redis URL is required"
        
        # Check agent configurations
        for agent_type, agent_config in config.agent_types.items():
            assert "enabled" in agent_config, f"Agent {agent_type} missing enabled field"
            assert "model" in agent_config, f"Agent {agent_type} missing model field"
            assert "timeout" in agent_config, f"Agent {agent_type} missing timeout field"
        
        # Check workspace paths exist
        workspace_path = Path(config.workspace_path)
        assert workspace_path.exists(), f"Workspace path {config.workspace_path} does not exist"
        
        return True
        
    except AssertionError as e:
        print(f"❌ Configuration validation failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Configuration validation error: {e}")
        return False

if __name__ == "__main__":
    
    if validate_config():
        print("✅ Configuration validation passed")
    else:
        print("❌ Configuration validation failed")
