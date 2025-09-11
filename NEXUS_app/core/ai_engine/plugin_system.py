#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🔌 Frenly AI Plugin System
Plugin architecture for custom agents and extensions
"""

import asyncio
import logging
import time
import json
import importlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Callable, Type
from dataclasses import dataclass, field
from enum import Enum
import redis
from pathlib import Path
from backend.config import get_config

logger = logging.getLogger(__name__)

class PluginType(Enum):
    """Plugin type enumeration"""
    AGENT = "agent"
    PROCESSOR = "processor"
    VALIDATOR = "validator"
    NOTIFIER = "notifier"
    ANALYZER = "analyzer"
    CUSTOM = "custom"

class PluginStatus(Enum):
    """Plugin status enumeration"""
    INSTALLED = "installed"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"
    UPDATING = "updating"

class PluginCapability(Enum):
    """Plugin capability enumeration"""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    NETWORK = "network"
    FILE_SYSTEM = "file_system"
    DATABASE = "database"

@dataclass
class PluginManifest:
    """Plugin manifest definition"""
    id: str
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    capabilities: List[PluginCapability]
    dependencies: List[str] = field(default_factory=list)
    config_schema: Dict[str, Any] = field(default_factory=dict)
    api_version: str = "1.0.0"
    min_frenly_version: str = "2.0.0"

@dataclass
class Plugin:
    """Plugin definition"""
    manifest: PluginManifest
    status: PluginStatus
    installed_at: str
    enabled_at: Optional[str] = None
    last_updated: Optional[str] = None
    error_message: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)
    instance: Optional[Any] = None

@dataclass
class PluginHook:
    """Plugin hook definition"""
    name: str
    plugin_id: str
    function: Callable
    priority: int = 0
    enabled: bool = True

class PluginSystem:
    """Plugin system for Frenly AI"""
    
    def __init__(self):
        """
          Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        self.config = get_config()
        self.redis_client = redis.Redis.from_url(self.config.redis_url)
        self.running = False
        
        # Plugin storage
        self.plugins: Dict[str, Plugin] = {}
        self.hooks: Dict[str, List[PluginHook]] = {}
        self.plugin_directory = Path("plugins")
        
        # Plugin configuration
        self.sandbox_enabled = True
        self.auto_update = False
        self.max_plugins = 100
        
        # Create plugin directory
        self.plugin_directory.mkdir(exist_ok=True)
        
        logger.info("✅ Plugin System initialized")
    
    async def start(self):
        """Start the plugin system"""
        self.running = True
        logger.info("🚀 Starting Plugin System...")
        
        # Load existing plugins
        await self._load_plugins()
        
        # Start background tasks
        asyncio.create_task(self._monitor_plugins())
        asyncio.create_task(self._check_updates())
        
        logger.info("✅ Plugin System started")
    
    async def stop(self):
        """Stop the plugin system"""
        self.running = False
        logger.info("🛑 Stopping Plugin System...")
        
        # Disable all plugins
        for plugin in self.plugins.values():
            if plugin.status == PluginStatus.ENABLED:
                await self.disable_plugin(plugin.manifest.id)
        
        # Save plugin state
        await self._save_plugins()
        
        logger.info("✅ Plugin System stopped")
    
    async def install_plugin(self, plugin_path: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """Install a plugin from file or URL"""
        try:
            # Load plugin manifest
            manifest = await self._load_plugin_manifest(plugin_path)
            if not manifest:
                return False
            
            # Check if plugin already exists
            if manifest.id in self.plugins:
                logger.warning(f"Plugin {manifest.id} already installed")
                return False
            
            # Validate plugin
            if not await self._validate_plugin(manifest):
                return False
            
            # Create plugin instance
            plugin = Plugin(
                manifest=manifest,
                status=PluginStatus.INSTALLED,
                installed_at=datetime.now().isoformat(),
                config=config or {}
            )
            
            # Load plugin code
            plugin.instance = await self._load_plugin_instance(plugin)
            if not plugin.instance:
                plugin.status = PluginStatus.ERROR
                plugin.error_message = "Failed to load plugin instance"
                return False
            
            # Register plugin
            self.plugins[manifest.id] = plugin
            
            # Register hooks
            await self._register_plugin_hooks(plugin)
            
            logger.info(f"Plugin installed: {manifest.id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error installing plugin: {e}")
            return False
    
    async def enable_plugin(self, plugin_id: str) -> bool:
        """Enable a plugin"""
        try:
            if plugin_id not in self.plugins:
                logger.warning(f"Plugin not found: {plugin_id}")
                return False
            
            plugin = self.plugins[plugin_id]
            
            if plugin.status == PluginStatus.ENABLED:
                logger.warning(f"Plugin already enabled: {plugin_id}")
                return True
            
            # Check dependencies
            if not await self._check_dependencies(plugin):
                return False
            
            # Initialize plugin
            if hasattr(plugin.instance, 'initialize'):
                await plugin.instance.initialize(plugin.config)
            
            # Enable plugin
            plugin.status = PluginStatus.ENABLED
            plugin.enabled_at = datetime.now().isoformat()
            plugin.error_message = None
            
            logger.info(f"Plugin enabled: {plugin_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error enabling plugin {plugin_id}: {e}")
            plugin.status = PluginStatus.ERROR
            plugin.error_message = str(e)
            return False
    
    async def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin"""
        try:
            if plugin_id not in self.plugins:
                logger.warning(f"Plugin not found: {plugin_id}")
                return False
            
            plugin = self.plugins[plugin_id]
            
            if plugin.status != PluginStatus.ENABLED:
                logger.warning(f"Plugin not enabled: {plugin_id}")
                return True
            
            # Cleanup plugin
            if hasattr(plugin.instance, 'cleanup'):
                await plugin.instance.cleanup()
            
            # Unregister hooks
            await self._unregister_plugin_hooks(plugin_id)
            
            # Disable plugin
            plugin.status = PluginStatus.DISABLED
            plugin.enabled_at = None
            
            logger.info(f"Plugin disabled: {plugin_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error disabling plugin {plugin_id}: {e}")
            return False
    
    async def uninstall_plugin(self, plugin_id: str) -> bool:
        """Uninstall a plugin"""
        try:
            if plugin_id not in self.plugins:
                logger.warning(f"Plugin not found: {plugin_id}")
                return False
            
            plugin = self.plugins[plugin_id]
            
            # Disable if enabled
            if plugin.status == PluginStatus.ENABLED:
                await self.disable_plugin(plugin_id)
            
            # Remove plugin
            del self.plugins[plugin_id]
            
            logger.info(f"Plugin uninstalled: {plugin_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error uninstalling plugin {plugin_id}: {e}")
            return False
    
    async def get_plugin(self, plugin_id: str) -> Optional[Plugin]:
        """Get plugin information"""
        return self.plugins.get(plugin_id)
    
    async def list_plugins(self, status: Optional[PluginStatus] = None) -> List[Plugin]:
        """List all plugins with optional status filter"""
        plugins = list(self.plugins.values())
        
        if status:
            plugins = [p for p in plugins if p.status == status]
        
        return plugins
    
    async def register_hook(self, hook_name: str, plugin_id: str, function: Callable, priority: int = 0):
        """Register a plugin hook"""
        try:
            if hook_name not in self.hooks:
                self.hooks[hook_name] = []
            
            hook = PluginHook(
                name=hook_name,
                plugin_id=plugin_id,
                function=function,
                priority=priority
            )
            
            self.hooks[hook_name].append(hook)
            
            # Sort by priority
            self.hooks[hook_name].sort(key=lambda h: h.priority, reverse=True)
            
            logger.debug(f"Hook registered: {hook_name} from {plugin_id}")
            
        except Exception as e:
            logger.error(f"❌ Error registering hook: {e}")
    
    async def unregister_hook(self, hook_name: str, plugin_id: str):
        """Unregister a plugin hook"""
        try:
            if hook_name in self.hooks:
                self.hooks[hook_name] = [
                    h for h in self.hooks[hook_name] 
                    if h.plugin_id != plugin_id
                ]
                
                logger.debug(f"Hook unregistered: {hook_name} from {plugin_id}")
            
        except Exception as e:
            logger.error(f"❌ Error unregistering hook: {e}")
    
    async def call_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Call all registered hooks for a given name"""
        try:
            if hook_name not in self.hooks:
                return []
            
            results = []
            
            for hook in self.hooks[hook_name]:
                if hook.enabled:
                    try:
                        result = await hook.function(*args, **kwargs)
                        results.append(result)
                    except Exception as e:
                        logger.error(f"❌ Error in hook {hook_name} from {hook.plugin_id}: {e}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error calling hook {hook_name}: {e}")
            return []
    
    async def get_plugin_analytics(self) -> Dict[str, Any]:
        """Get plugin system analytics"""
        try:
            total_plugins = len(self.plugins)
            enabled_plugins = len([p for p in self.plugins.values() if p.status == PluginStatus.ENABLED])
            disabled_plugins = len([p for p in self.plugins.values() if p.status == PluginStatus.DISABLED])
            error_plugins = len([p for p in self.plugins.values() if p.status == PluginStatus.ERROR])
            
            # Plugin type distribution
            type_distribution = {}
            for plugin in self.plugins.values():
                plugin_type = plugin.manifest.plugin_type.value
                type_distribution[plugin_type] = type_distribution.get(plugin_type, 0) + 1
            
            # Hook statistics
            total_hooks = sum(len(hooks) for hooks in self.hooks.values())
            
            return {
                "total_plugins": total_plugins,
                "enabled_plugins": enabled_plugins,
                "disabled_plugins": disabled_plugins,
                "error_plugins": error_plugins,
                "type_distribution": type_distribution,
                "total_hooks": total_hooks,
                "hook_categories": list(self.hooks.keys()),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting plugin analytics: {e}")
            return {"error": str(e)}
    
    async def _load_plugin_manifest(self, plugin_path: str) -> Optional[PluginManifest]:
        """Load plugin manifest from file"""
        try:
            # This would load from actual plugin file
            
            manifest_data = {
                "id": f"plugin_{int(time.time())}",
                "version": "1.0.0",
                "author": "Frenly AI Team",
                "plugin_type": "agent",
                "capabilities": ["read", "write"],
                "dependencies": [],
                "config_schema": {},
                "api_version": "1.0.0",
                "min_frenly_version": "2.0.0"
            }
            
            return PluginManifest(**manifest_data)
            
        except Exception as e:
            logger.error(f"❌ Error loading plugin manifest: {e}")
            return None
    
    async def _validate_plugin(self, manifest: PluginManifest) -> bool:
        """Validate plugin before installation"""
        try:
            # Check API version compatibility
            if manifest.api_version != "1.0.0":
                logger.warning(f"Unsupported API version: {manifest.api_version}")
                return False
            
            # Check minimum Frenly version
            if manifest.min_frenly_version > self.config.version:
                logger.warning(f"Plugin requires Frenly version {manifest.min_frenly_version}")
                return False
            
            # Check capabilities
            if not manifest.capabilities:
                logger.warning("Plugin has no capabilities defined")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error validating plugin: {e}")
            return False
    
    async def _load_plugin_instance(self, plugin: Plugin) -> Optional[Any]:
        """Load plugin instance"""
        try:
            # This would load the actual plugin code
            
                def __init__(self, manifest, config):
                    """
                      Init  
                    
                    
                    Args:
                        manifest: Description of manifest
                        config: Description of config
                
                    Example:
                        TBD: Add usage example
                    """
                    self.manifest = manifest
                    self.config = config
                
                async def initialize(self, config):
                    logger.info(f"Plugin {self.manifest.id} initialized")
                
                async def cleanup(self):
                    logger.info(f"Plugin {self.manifest.id} cleaned up")
                
                async def process(self, data):
                    return f"Processed by {self.manifest.id}: {data}"
            
            
        except Exception as e:
            logger.error(f"❌ Error loading plugin instance: {e}")
            return None
    
    async def _register_plugin_hooks(self, plugin: Plugin):
        """Register hooks for a plugin"""
        try:
            if not plugin.instance:
                return
            
            # Look for hook methods in the plugin instance
            for method_name in dir(plugin.instance):
                method = getattr(plugin.instance, method_name)
                
                if callable(method) and method_name.startswith('hook_'):
                    hook_name = method_name[5:]  # Remove 'hook_' prefix
                    await self.register_hook(hook_name, plugin.manifest.id, method)
            
        except Exception as e:
            logger.error(f"❌ Error registering plugin hooks: {e}")
    
    async def _unregister_plugin_hooks(self, plugin_id: str):
        """Unregister hooks for a plugin"""
        try:
            for hook_name in list(self.hooks.keys()):
                await self.unregister_hook(hook_name, plugin_id)
            
        except Exception as e:
            logger.error(f"❌ Error unregistering plugin hooks: {e}")
    
    async def _check_dependencies(self, plugin: Plugin) -> bool:
        """Check plugin dependencies"""
        try:
            for dependency in plugin.manifest.dependencies:
                if dependency not in self.plugins:
                    logger.warning(f"Missing dependency: {dependency}")
                    return False
                
                dep_plugin = self.plugins[dependency]
                if dep_plugin.status != PluginStatus.ENABLED:
                    logger.warning(f"Dependency not enabled: {dependency}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error checking dependencies: {e}")
            return False
    
    async def _monitor_plugins(self):
        """Monitor plugin health"""
        while self.running:
            try:
                for plugin in self.plugins.values():
                    if plugin.status == PluginStatus.ENABLED:
                        # Check plugin health
                        if hasattr(plugin.instance, 'health_check'):
                            try:
                                health = await plugin.instance.health_check()
                                if not health:
                                    plugin.status = PluginStatus.ERROR
                                    plugin.error_message = "Health check failed"
                            except Exception as e:
                                plugin.status = PluginStatus.ERROR
                                plugin.error_message = f"Health check error: {e}"
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"❌ Error monitoring plugins: {e}")
                await asyncio.sleep(60)
    
    async def _check_updates(self):
        """Check for plugin updates"""
        while self.running:
            try:
                if self.auto_update:
                    # This would check for plugin updates
                    # For now, we'll just log that we're checking
                    logger.debug("Checking for plugin updates...")
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"❌ Error checking updates: {e}")
                await asyncio.sleep(60)
    
    async def _load_plugins(self):
        """Load plugins from storage"""
        try:
            if self.redis_client:
                data = self.redis_client.get("frenly_plugins")
                if data:
                    plugins_data = json.loads(data)
                    
                    for plugin_id, plugin_data in plugins_data.items():
                        manifest_data = plugin_data["manifest"]
                        manifest = PluginManifest(**manifest_data)
                        
                        plugin = Plugin(
                            manifest=manifest,
                            status=PluginStatus(plugin_data["status"]),
                            installed_at=plugin_data["installed_at"],
                            enabled_at=plugin_data.get("enabled_at"),
                            last_updated=plugin_data.get("last_updated"),
                            error_message=plugin_data.get("error_message"),
                            config=plugin_data.get("config", {})
                        )
                        
                        self.plugins[plugin_id] = plugin
                    
                    logger.info(f"Loaded {len(self.plugins)} plugins")
            
        except Exception as e:
            logger.error(f"❌ Error loading plugins: {e}")
    
    async def _save_plugins(self):
        """Save plugins to storage"""
        try:
            if self.redis_client:
                plugins_data = {
                    plugin_id: {
                        "manifest": {
                            "id": plugin.manifest.id,
                            "name": plugin.manifest.name,
                            "version": plugin.manifest.version,
                            "description": plugin.manifest.description,
                            "author": plugin.manifest.author,
                            "plugin_type": plugin.manifest.plugin_type.value,
                            "capabilities": [c.value for c in plugin.manifest.capabilities],
                            "dependencies": plugin.manifest.dependencies,
                            "config_schema": plugin.manifest.config_schema,
                            "api_version": plugin.manifest.api_version,
                            "min_frenly_version": plugin.manifest.min_frenly_version
                        },
                        "status": plugin.status.value,
                        "installed_at": plugin.installed_at,
                        "enabled_at": plugin.enabled_at,
                        "last_updated": plugin.last_updated,
                        "error_message": plugin.error_message,
                        "config": plugin.config
                    }
                    for plugin_id, plugin in self.plugins.items()
                }
                
                self.redis_client.setex(
                    "frenly_plugins",
                    86400,  # 24 hours TTL
                    json.dumps(plugins_data, default=str)
                )
            
        except Exception as e:
            logger.error(f"❌ Error saving plugins: {e}")

# Global plugin system instance
plugin_system = PluginSystem()
