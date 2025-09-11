#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
Centralized Configuration Manager for Nexus Platform
Manages all configuration settings across components with validation and hot-reload.
"""

import json
import logging
import os
import threading
import time
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import jsonschema
from jsonschema import validate, ValidationError

logger = logging.getLogger(__name__)

class ConfigType(Enum):
    """Types of configuration"""
    SYSTEM = "system"
    DATABASE = "database"
    API = "api"
    AI = "ai"
    MONITORING = "monitoring"
    SECURITY = "security"
    FRONTEND = "frontend"
    AUTOMATION = "automation"
    PERFORMANCE = "performance"

@dataclass
class ConfigSchema:
    """Configuration schema definition"""
    type: ConfigType
    schema: Dict[str, Any]
    required_fields: List[str]
    default_values: Dict[str, Any]

class CentralizedConfigManager:
    """Centralized configuration management system"""
    
    def __init__(self, workspace_path: str):
        """
          Init  
        
        
        Args:
            workspace_path: Description of workspace_path
    
        Example:
            TBD: Add usage example
        """
        self.workspace_path = Path(workspace_path)
        self.config_dir = self.workspace_path / ".nexus" / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration storage
        self.configs: Dict[ConfigType, Dict[str, Any]] = {}
        self.schemas: Dict[ConfigType, ConfigSchema] = {}
        self.config_locks: Dict[ConfigType, threading.Lock] = {}
        
        # Hot reload
        self.watch_thread = None
        self.running = True
        self.last_modified = {}
        
        # Initialize configuration types
        for config_type in ConfigType:
            self.configs[config_type] = {}
            self.config_locks[config_type] = threading.Lock()
        
        # Define configuration schemas
        self._define_schemas()
        
        # Load all configurations
        self.load_all_configs()
        
        # Start hot reload thread
        self.start_watch_thread()
    
    def _define_schemas(self):
        """Define configuration schemas for validation"""
        
        # System configuration schema
        self.schemas[ConfigType.SYSTEM] = ConfigSchema(
            type=ConfigType.SYSTEM,
            schema={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string"},
                    "app_version": {"type": "string"},
                    "environment": {"type": "string", "enum": ["development", "staging", "production"]},
                    "debug": {"type": "boolean"},
                    "log_level": {"type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]},
                    "workspace_path": {"type": "string"}
                },
                "required": ["app_name", "app_version", "environment"]
            },
            required_fields=["app_name", "app_version", "environment"],
            default_values={
                "app_name": "Nexus Platform",
                "app_version": "1.0.0",
                "environment": "development",
                "debug": True,
                "log_level": "INFO"
            }
        )
        
        # Database configuration schema
        self.schemas[ConfigType.DATABASE] = ConfigSchema(
            type=ConfigType.DATABASE,
            schema={
                "type": "object",
                "properties": {
                    "host": {"type": "string"},
                    "port": {"type": "integer", "minimum": 1, "maximum": 65535},
                    "database": {"type": "string"},
                    "username": {"type": "string"},
                    "password": {"type": "string"},
                    "pool_size": {"type": "integer", "minimum": 1},
                    "max_overflow": {"type": "integer", "minimum": 0}
                },
                "required": ["host", "port", "database", "username", "password"]
            },
            required_fields=["host", "port", "database", "username", "password"],
            default_values={
                "host": "localhost",
                "port": 5432,
                "database": "nexus_platform",
                "username": "nexus_user",
                "password": "nexus_password",
                "pool_size": 10,
                "max_overflow": 20
            }
        )
        
        # API configuration schema
        self.schemas[ConfigType.API] = ConfigSchema(
            type=ConfigType.API,
            schema={
                "type": "object",
                "properties": {
                    "host": {"type": "string"},
                    "port": {"type": "integer", "minimum": 1, "maximum": 65535},
                    "api_prefix": {"type": "string"},
                    "cors_origins": {"type": "array", "items": {"type": "string"}},
                    "rate_limit": {"type": "integer", "minimum": 1},
                    "timeout": {"type": "integer", "minimum": 1}
                },
                "required": ["host", "port", "api_prefix"]
            },
            required_fields=["host", "port", "api_prefix"],
            default_values={
                "host": "0.0.0.0",
                "port": 8000,
                "api_prefix": "/api/v1",
                "cors_origins": ["*"],
                "rate_limit": 100,
                "timeout": 30
            }
        )
        
        # AI configuration schema
        self.schemas[ConfigType.AI] = ConfigSchema(
            type=ConfigType.AI,
            schema={
                "type": "object",
                "properties": {
                    "providers": {"type": "array", "items": {"type": "string"}},
                    "default_provider": {"type": "string"},
                    "max_tokens": {"type": "integer", "minimum": 1},
                    "temperature": {"type": "number", "minimum": 0, "maximum": 2},
                    "timeout": {"type": "integer", "minimum": 1}
                },
                "required": ["providers", "default_provider"]
            },
            required_fields=["providers", "default_provider"],
            default_values={
                "providers": ["openai", "anthropic", "google"],
                "default_provider": "openai",
                "max_tokens": 4000,
                "temperature": 0.7,
                "timeout": 30
            }
        )
        
        # Monitoring configuration schema
        self.schemas[ConfigType.MONITORING] = ConfigSchema(
            type=ConfigType.MONITORING,
            schema={
                "type": "object",
                "properties": {
                    "enabled": {"type": "boolean"},
                    "metrics_interval": {"type": "integer", "minimum": 1},
                    "log_level": {"type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR"]},
                    "retention_days": {"type": "integer", "minimum": 1}
                },
                "required": ["enabled"]
            },
            required_fields=["enabled"],
            default_values={
                "enabled": True,
                "metrics_interval": 60,
                "log_level": "INFO",
                "retention_days": 30
            }
        )
        
        # Security configuration schema
        self.schemas[ConfigType.SECURITY] = ConfigSchema(
            type=ConfigType.SECURITY,
            schema={
                "type": "object",
                "properties": {
                    "encryption_key": {"type": "string"},
                    "session_timeout": {"type": "integer", "minimum": 1},
                    "max_login_attempts": {"type": "integer", "minimum": 1},
                    "password_min_length": {"type": "integer", "minimum": 8}
                },
                "required": ["encryption_key"]
            },
            required_fields=["encryption_key"],
            default_values={
                "encryption_key": "default_key_change_in_production",
                "session_timeout": 3600,
                "max_login_attempts": 5,
                "password_min_length": 8
            }
        )
        
        # Frontend configuration schema
        self.schemas[ConfigType.FRONTEND] = ConfigSchema(
            type=ConfigType.FRONTEND,
            schema={
                "type": "object",
                "properties": {
                    "port": {"type": "integer", "minimum": 1, "maximum": 65535},
                    "host": {"type": "string"},
                    "debug": {"type": "boolean"},
                    "api_url": {"type": "string"}
                },
                "required": ["port", "host"]
            },
            required_fields=["port", "host"],
            default_values={
                "port": 3000,
                "host": "localhost",
                "debug": True,
                "api_url": "http://localhost:8000"
            }
        )
        
        # Automation configuration schema
        self.schemas[ConfigType.AUTOMATION] = ConfigSchema(
            type=ConfigType.AUTOMATION,
            schema={
                "type": "object",
                "properties": {
                    "enabled": {"type": "boolean"},
                    "max_workers": {"type": "integer", "minimum": 1},
                    "task_timeout": {"type": "integer", "minimum": 1},
                    "retry_attempts": {"type": "integer", "minimum": 0}
                },
                "required": ["enabled"]
            },
            required_fields=["enabled"],
            default_values={
                "enabled": True,
                "max_workers": 4,
                "task_timeout": 300,
                "retry_attempts": 3
            }
        )
        
        # Performance configuration schema
        self.schemas[ConfigType.PERFORMANCE] = ConfigSchema(
            type=ConfigType.PERFORMANCE,
            schema={
                "type": "object",
                "properties": {
                    "cache_enabled": {"type": "boolean"},
                    "cache_ttl": {"type": "integer", "minimum": 1},
                    "max_memory_usage": {"type": "integer", "minimum": 100},
                    "gc_interval": {"type": "integer", "minimum": 1}
                },
                "required": ["cache_enabled"]
            },
            required_fields=["cache_enabled"],
            default_values={
                "cache_enabled": True,
                "cache_ttl": 3600,
                "max_memory_usage": 1024,
                "gc_interval": 300
            }
        )
    
    def load_all_configs(self):
        """Load all configuration files"""
        for config_type in ConfigType:
            self.load_config(config_type)
    
    def load_config(self, config_type: ConfigType):
        """Load configuration from file"""
        try:
            config_file = self.config_dir / f"{config_type.value}.json"
            
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                
                # Validate configuration
                if self.validate_config(config_type, config_data):
                    with self.config_locks[config_type]:
                        self.configs[config_type] = config_data
                    logger.info(f"Loaded {config_type.value} configuration")
                else:
                    logger.warning(f"Invalid {config_type.value} configuration, using defaults")
                    self._apply_defaults(config_type)
            else:
                logger.info(f"No {config_type.value} configuration found, using defaults")
                self._apply_defaults(config_type)
                
        except Exception as e:
            logger.error(f"Error loading {config_type.value} configuration: {e}")
            self._apply_defaults(config_type)
    
    def _apply_defaults(self, config_type: ConfigType):
        """Apply default configuration values"""
        with self.config_locks[config_type]:
            self.configs[config_type] = self.schemas[config_type].default_values.copy()
    
    def save_config(self, config_type: ConfigType):
        """Save configuration to file"""
        try:
            config_file = self.config_dir / f"{config_type.value}.json"
            
            with self.config_locks[config_type]:
                config_data = self.configs[config_type].copy()
            
            # Validate before saving
            if self.validate_config(config_type, config_data):
                with open(config_file, 'w') as f:
                    json.dump(config_data, f, indent=2)
                logger.info(f"Saved {config_type.value} configuration")
            else:
                logger.error(f"Cannot save invalid {config_type.value} configuration")
                
        except Exception as e:
            logger.error(f"Error saving {config_type.value} configuration: {e}")
    
    def get_config(self, config_type: ConfigType, key: str = None) -> Any:
        """Get configuration value"""
        with self.config_locks[config_type]:
            if key is None:
                return self.configs[config_type].copy()
            else:
                return self.configs[config_type].get(key)
    
    def set_config(self, config_type: ConfigType, key: str, value: Any) -> bool:
        """Set configuration value"""
        try:
            # Create temporary config for validation
            temp_config = self.configs[config_type].copy()
            temp_config[key] = value
            
            if self.validate_config(config_type, temp_config):
                with self.config_locks[config_type]:
                    self.configs[config_type][key] = value
                
                # Save to file
                self.save_config(config_type)
                logger.info(f"Set {config_type.value}.{key} = {value}")
                return True
            else:
                logger.error(f"Invalid value for {config_type.value}.{key}: {value}")
                return False
                
        except Exception as e:
            logger.error(f"Error setting {config_type.value}.{key}: {e}")
            return False
    
    def update_config(self, config_type: ConfigType, updates: Dict[str, Any]) -> bool:
        """Update multiple configuration values"""
        try:
            # Create temporary config for validation
            temp_config = self.configs[config_type].copy()
            temp_config.update(updates)
            
            if self.validate_config(config_type, temp_config):
                with self.config_locks[config_type]:
                    self.configs[config_type].update(updates)
                
                # Save to file
                self.save_config(config_type)
                logger.info(f"Updated {config_type.value} configuration")
                return True
            else:
                logger.error(f"Invalid updates for {config_type.value} configuration")
                return False
                
        except Exception as e:
            logger.error(f"Error updating {config_type.value} configuration: {e}")
            return False
    
    def validate_config(self, config_type: ConfigType, config_data: Dict[str, Any]) -> bool:
        """Validate configuration against schema"""
        try:
            schema = self.schemas[config_type]
            validate(instance=config_data, schema=schema.schema)
            
            # Check required fields
            for field in schema.required_fields:
                if field not in config_data:
                    logger.error(f"Missing required field: {field}")
                    return False
            
            return True
            
        except ValidationError as e:
            logger.error(f"Configuration validation error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error validating configuration: {e}")
            return False
    
    def get_all_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get all configurations"""
        all_configs = {}
        for config_type in ConfigType:
            with self.config_locks[config_type]:
                all_configs[config_type.value] = self.configs[config_type].copy()
        return all_configs
    
    def start_watch_thread(self):
        """Start the configuration watch thread for hot reload"""
        self.watch_thread = threading.Thread(target=self._watch_configs, daemon=True)
        self.watch_thread.start()
    
    def _watch_configs(self):
        """Watch configuration files for changes"""
        while self.running:
            try:
                for config_type in ConfigType:
                    config_file = self.config_dir / f"{config_type.value}.json"
                    
                    if config_file.exists():
                        current_modified = config_file.stat().st_mtime
                        last_modified = self.last_modified.get(config_type, 0)
                        
                        if current_modified > last_modified:
                            self.last_modified[config_type] = current_modified
                            logger.info(f"Configuration file changed: {config_type.value}")
                            self.load_config(config_type)
                
                time.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"Error in config watch thread: {e}")
                time.sleep(5)
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary"""
        summary = {
            "total_configs": len(ConfigType),
            "loaded_configs": 0,
            "config_types": []
        }
        
        for config_type in ConfigType:
            with self.config_locks[config_type]:
                config_count = len(self.configs[config_type])
                summary["loaded_configs"] += config_count
                summary["config_types"].append({
                    "type": config_type.value,
                    "keys": list(self.configs[config_type].keys()),
                    "count": config_count
                })
        
        return summary
    
    def export_config(self, config_type: ConfigType, format: str = "json") -> str:
        """
        Export Config
        
        
        Args:
            config_type: Description of config_type
            format: Description of format
    
        Returns:
            str: Description of return value
    
        Example:
            TBD: Add usage example
        """
        with self.config_locks[config_type]:
            config_data = self.configs[config_type].copy()
        
        if format.lower() == "yaml":
            return yaml.dump(config_data, default_flow_style=False)
        else:
            return json.dumps(config_data, indent=2)
    
    def import_config(self, config_type: ConfigType, config_data: str, format: str = "json") -> bool:
        """Import configuration from string"""
        try:
            if format.lower() == "yaml":
                parsed_config = yaml.safe_load(config_data)
            else:
                parsed_config = json.loads(config_data)
            
            if self.validate_config(config_type, parsed_config):
                with self.config_locks[config_type]:
                    self.configs[config_type] = parsed_config
                
                self.save_config(config_type)
                logger.info(f"Imported {config_type.value} configuration")
                return True
            else:
                logger.error(f"Invalid {config_type.value} configuration import")
                return False
                
        except Exception as e:
            logger.error(f"Error importing {config_type.value} configuration: {e}")
            return False
    
    def shutdown(self):
        """Shutdown the configuration manager"""
        self.running = False
        if self.watch_thread:
            self.watch_thread.join(timeout=5)
        
        # Save all configurations
        for config_type in ConfigType:
            self.save_config(config_type)
        
        logger.info("Configuration manager shutdown complete")
