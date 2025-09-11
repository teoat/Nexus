"""
🤖 AI Service Manager
Manages and coordinates all AI services in the Nexus Platform.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
from datetime import datetime

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from interfaces.ai_service import (
    AIServiceInterface, AIServiceManager, AIRequest, AIResponse,
    AIProviderType, AIModelType, AIModelInfo
)
from models.ai_models import (
    AIServiceRegistry, AIServiceInstance, AIServiceConfig,
    AIServiceStatus, AIServicePriority, AIServiceMetrics
)

logger = logging.getLogger(__name__)

class NexusAIServiceManager(AIServiceManager):
    """Main AI service manager for the Nexus Platform"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
          Init  
        
        
        Args:
            config_path: Description of config_path
    
        Example:
            TBD: Add usage example
        """
        self.registry = AIServiceRegistry()
        self.services: Dict[str, AIServiceInterface] = {}
        self.config_path = Path(config_path) if config_path else Path("config/ai_services.json")
        self.running = True
        
        # Load configuration
        self.config = self._load_config()
        
        logger.info("🤖 AI Service Manager initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load AI service configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                # Create default configuration
                default_config = {
                    "services": {
                        "openai": {
                            "provider": "openai",
                            "enabled": True,
                            "priority": "high",
                            "max_concurrent_requests": 20,
                            "timeout_seconds": 30
                        },
                        "anthropic": {
                            "provider": "anthropic",
                            "enabled": True,
                            "priority": "high",
                            "max_concurrent_requests": 15,
                            "timeout_seconds": 30
                        },
                        "local": {
                            "provider": "local",
                            "enabled": False,
                            "priority": "medium",
                            "max_concurrent_requests": 5,
                            "timeout_seconds": 60
                        }
                    },
                    "workflows": {},
                    "default_provider": "openai"
                }
                
                # Ensure config directory exists
                self.config_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(self.config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                
                return default_config
                
        except Exception as e:
            logger.error(f"❌ Failed to load AI service config: {e}")
            return {"services": {}, "workflows": {}, "default_provider": "openai"}
    
    async def register_service(self, service: AIServiceInterface, name: str) -> bool:
        """Register an AI service"""
        try:
            if name in self.services:
                logger.warning(f"⚠️ Service {name} already registered")
                return False
            
            # Create service instance
            service_config = self.config.get("services", {}).get(name, {})
            config = AIServiceConfig(
                name=name,
                provider=service_config.get("provider", "custom"),
                max_concurrent_requests=service_config.get("max_concurrent_requests", 10),
                timeout_seconds=service_config.get("timeout_seconds", 30),
                priority=AIServicePriority(service_config.get("priority", "medium")),
                enabled=service_config.get("enabled", True)
            )
            
            instance = AIServiceInstance(config=config)
            
            # Register in both places
            self.services[name] = service
            self.registry.register_service(instance)
            
            # Initialize the service
            if await service.initialize():
                instance.status = AIServiceStatus.RUNNING
                instance.health_score = 100.0
                logger.info(f"✅ AI service {name} registered and initialized")
                return True
            else:
                instance.status = AIServiceStatus.ERROR
                logger.error(f"❌ Failed to initialize AI service {name}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error registering AI service {name}: {e}")
            return False
    
    async def get_service(self, name: str) -> Optional[AIServiceInterface]:
        """Get a registered service by name"""
        return self.services.get(name)
    
    async def list_services(self) -> List[str]:
        """List all registered services"""
        return list(self.services.keys())
    
    async def route_request(self, request: AIRequest) -> AIResponse:
        """Route request to appropriate service"""
        try:
            # Determine which service to use
            service_name = self._select_service_for_request(request)
            
            if not service_name:
                return AIResponse(
                    content="",
                    model=request.model,
                    provider=request.provider,
                    usage={},
                    metadata={},
                    error="No suitable AI service available"
                )
            
            service = self.services.get(service_name)
            if not service:
                return AIResponse(
                    content="",
                    model=request.model,
                    provider=request.provider,
                    usage={},
                    metadata={},
                    error=f"Service {service_name} not found"
                )
            
            # Execute the request
            start_time = time.time()
            response = await service.generate_text(request)
            execution_time = time.time() - start_time
            
            # Update metrics
            self._update_service_metrics(service_name, response, execution_time)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error routing AI request: {e}")
            return AIResponse(
                content="",
                model=request.model,
                provider=request.provider,
                usage={},
                metadata={},
                error=f"Request routing failed: {str(e)}"
            )
    
    def _select_service_for_request(self, request: AIRequest) -> Optional[str]:
        """Select the best service for a request"""
        available_services = []
        
        for name, service in self.services.items():
            instance = self.registry.get_service(name)
            if not instance or instance.status != AIServiceStatus.RUNNING:
                continue
            
            # Check if service supports the requested provider
            if request.provider.value == instance.config.provider:
                available_services.append((name, instance))
        
        if not available_services:
            return None
        
        # Sort by priority and health score
        available_services.sort(
            key=lambda x: (
                self._priority_score(x[1].config.priority),
                x[1].health_score
            ),
            reverse=True
        )
        
        return available_services[0][0]
    
    def _priority_score(self, priority: AIServicePriority) -> int:
        """Convert priority to numeric score"""
        priority_scores = {
            AIServicePriority.CRITICAL: 4,
            AIServicePriority.HIGH: 3,
            AIServicePriority.MEDIUM: 2,
            AIServicePriority.LOW: 1
        }
        return priority_scores.get(priority, 2)
    
    def _update_service_metrics(self, service_name: str, response: AIResponse, execution_time: float):
        """Update service metrics"""
        instance = self.registry.get_service(service_name)
        if not instance:
            return
        
        metrics = instance.metrics
        metrics.total_requests += 1
        
        if response.error:
            metrics.failed_requests += 1
        else:
            metrics.successful_requests += 1
        
        # Update response time
        if metrics.average_response_time == 0:
            metrics.average_response_time = execution_time
        else:
            metrics.average_response_time = (
                (metrics.average_response_time + execution_time) / 2
            )
        
        metrics.last_request_time = datetime.now().isoformat()
        
        # Update health score
        if metrics.total_requests > 0:
            success_rate = metrics.successful_requests / metrics.total_requests
            instance.health_score = min(100.0, success_rate * 100.0)
    
    async def get_service_health(self) -> Dict[str, Any]:
        """Get health status of all services"""
        health_status = {
            "overall_health": 0.0,
            "services": {},
            "total_services": len(self.services),
            "healthy_services": 0,
            "timestamp": datetime.now().isoformat()
        }
        
        total_health = 0.0
        
        for name, service in self.services.items():
            try:
                service_health = await service.health_check()
                instance = self.registry.get_service(name)
                
                if instance:
                    instance.last_health_check = datetime.now().isoformat()
                    instance.health_score = service_health.get("health_score", 0.0)
                
                health_status["services"][name] = {
                    "status": service_health.get("status", "unknown"),
                    "health_score": service_health.get("health_score", 0.0),
                    "last_check": datetime.now().isoformat(),
                    "error": service_health.get("error")
                }
                
                if service_health.get("status") == "healthy":
                    health_status["healthy_services"] += 1
                
                total_health += service_health.get("health_score", 0.0)
                
            except Exception as e:
                health_status["services"][name] = {
                    "status": "error",
                    "health_score": 0.0,
                    "last_check": datetime.now().isoformat(),
                    "error": str(e)
                }
        
        if self.services:
            health_status["overall_health"] = total_health / len(self.services)
        
        return health_status
    
    async def start_health_monitoring(self):
        """Start health monitoring loop"""
        logger.info("🔍 Starting AI service health monitoring...")
        
        while self.running:
            try:
                await self.get_service_health()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"❌ Health monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def shutdown(self):
        """Shutdown all services gracefully"""
        logger.info("🛑 Shutting down AI Service Manager...")
        
        self.running = False
        
        for name, service in self.services.items():
            try:
                await service.shutdown()
                logger.info(f"✅ Service {name} shut down")
            except Exception as e:
                logger.error(f"❌ Error shutting down service {name}: {e}")
        
        logger.info("✅ AI Service Manager shutdown complete")

async def main():
    manager = NexusAIServiceManager()
    
    
    # Shutdown
    await manager.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
