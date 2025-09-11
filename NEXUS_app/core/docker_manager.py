#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🐳 Docker Service Manager for Nexus Platform
Manages Docker service orchestration, health checks, and dependency management.
"""

import asyncio
import logging
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import docker
from docker.errors import DockerException
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DockerManager:
    """Manages Docker services for the Nexus Platform"""
    
    def __init__(self, workspace_path: str):
        """
          Init  
        
        
        Args:
            workspace_path: Description of workspace_path
    
        Example:
            TBD: Add usage example
        """
        self.workspace_path = Path(workspace_path)
        self.docker_client = None
        self.compose_file = self.workspace_path / "nexus_docker" / "docker-compose.yml"
        self.services_status = {}
        self.health_check_interval = 30  # seconds
        
        try:
            self.docker_client = docker.from_env()
            logger.info("✅ Docker client initialized successfully")
        except DockerException as e:
            logger.error(f"❌ Failed to initialize Docker client: {e}")
            self.docker_client = None
    
    async def start_services(self) -> Dict[str, Any]:
        """Start all Docker services using docker-compose"""
        if not self.compose_file.exists():
            logger.error(f"❌ Docker Compose file not found: {self.compose_file}")
            return {"success": False, "error": "Compose file not found"}
        
        try:
            logger.info("🚀 Starting Docker services...")
            
            # Start services using docker-compose
            result = subprocess.run(
                ["docker-compose", "-f", str(self.compose_file), "up", "-d"],
                cwd=self.workspace_path / "nexus_docker",
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("✅ Docker services started successfully")
                
                # Wait for services to be ready
                await asyncio.sleep(10)
                
                # Perform health checks
                health_status = await self.check_all_services_health()
                
                return {
                    "success": True,
                    "message": "Services started successfully",
                    "health_status": health_status
                }
            else:
                logger.error(f"❌ Failed to start services: {result.stderr}")
                return {
                    "success": False,
                    "error": result.stderr
                }
                
        except Exception as e:
            logger.error(f"❌ Error starting services: {e}")
            return {"success": False, "error": str(e)}
    
    async def stop_services(self) -> Dict[str, Any]:
        """Stop all Docker services"""
        try:
            logger.info("🛑 Stopping Docker services...")
            
            result = subprocess.run(
                ["docker-compose", "-f", str(self.compose_file), "down"],
                cwd=self.workspace_path / "nexus_docker",
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("✅ Docker services stopped successfully")
                return {"success": True, "message": "Services stopped successfully"}
            else:
                logger.error(f"❌ Failed to stop services: {result.stderr}")
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            logger.error(f"❌ Error stopping services: {e}")
            return {"success": False, "error": str(e)}
    
    async def check_service_health(self, service_name: str) -> Dict[str, Any]:
        try:
            if not self.docker_client:
                return {"healthy": False, "error": "Docker client not available"}
            
            # Get service container
            containers = self.docker_client.containers.list(
                filters={"label": f"com.docker.compose.service={service_name}"}
            )
            
            if not containers:
                return {"healthy": False, "error": "Service container not found"}
            
            container = containers[0]
            
            # Check container status
            container.reload()
            status = container.status
            
            if status != "running":
                return {
                    "healthy": False,
                    "status": status,
                    "error": f"Container status: {status}"
                }
            
            # Check health status if available
            health = container.attrs.get("State", {}).get("Health", {})
            if health:
                health_status = health.get("Status", "unknown")
                if health_status == "healthy":
                    return {"healthy": True, "status": status, "health": health_status}
                else:
                    return {
                        "healthy": False,
                        "status": status,
                        "health": health_status,
                        "error": "Health check failed"
                    }
            
            # If no health check, assume running container is healthy
            return {"healthy": True, "status": status}
            
        except Exception as e:
            logger.error(f"❌ Error checking health for {service_name}: {e}")
            return {"healthy": False, "error": str(e)}
    
    async def check_all_services_health(self) -> Dict[str, Any]:
        """Check health of all services"""
        logger.info("🏥 Checking health of all services...")
        
        # Read docker-compose file to get service names
        services = await self._get_service_names()
        health_results = {}
        
        for service_name in services:
            health_status = await self.check_service_health(service_name)
            health_results[service_name] = health_status
            
            # Update service status
            self.services_status[service_name] = health_status
        
        # Calculate overall health
        healthy_services = sum(1 for status in health_results.values() if status.get("healthy", False))
        total_services = len(services)
        
        overall_health = {
            "total_services": total_services,
            "healthy_services": healthy_services,
            "unhealthy_services": total_services - healthy_services,
            "health_percentage": (healthy_services / total_services * 100) if total_services > 0 else 0,
            "services": health_results
        }
        
        logger.info(f"🏥 Health check complete: {healthy_services}/{total_services} services healthy")
        return overall_health
    
    async def _get_service_names(self) -> List[str]:
        """Extract service names from docker-compose file"""
        try:
            with open(self.compose_file, 'r') as f:
                compose_data = yaml.safe_load(f)
            
            services = compose_data.get("services", {})
            return list(services.keys())
            
        except Exception as e:
            logger.error(f"❌ Error reading compose file: {e}")
            return []
    
    async def restart_services(self) -> Dict[str, Any]:
        """Restart all Docker services"""
        logger.info("🔄 Restarting Docker services...")
        
        # Stop services first
        stop_result = await self.stop_services()
        if not stop_result["success"]:
            return stop_result
        
        # Wait a moment
        await asyncio.sleep(5)
        
        # Start services again
        start_result = await self.start_services()
        return start_result
    
    async def restart_service(self, service_name: str) -> Dict[str, Any]:
        try:
            logger.info(f"🔄 Restarting service: {service_name}")
            
            result = subprocess.run(
                ["docker-compose", "-f", str(self.compose_file), "restart", service_name],
                cwd=self.workspace_path / "nexus_docker",
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Service {service_name} restarted successfully")
                
                # Wait for service to be ready
                await asyncio.sleep(10)
                
                # Check health after restart
                health_status = await self.check_service_health(service_name)
                
                return {
                    "success": True,
                    "message": f"Service {service_name} restarted successfully",
                    "health_status": health_status
                }
            else:
                logger.error(f"❌ Failed to restart {service_name}: {result.stderr}")
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            logger.error(f"❌ Error restarting {service_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_service_logs(self, service_name: str, lines: int = 50) -> Dict[str, Any]:
        try:
            if not self.docker_client:
                return {"success": False, "error": "Docker client not available"}
            
            containers = self.docker_client.containers.list(
                filters={"label": f"com.docker.compose.service={service_name}"}
            )
            
            if not containers:
                return {"success": False, "error": "Service container not found"}
            
            container = containers[0]
            logs = container.logs(tail=lines).decode('utf-8')
            
            return {
                "success": True,
                "service": service_name,
                "logs": logs,
                "lines": lines
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting logs for {service_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_service_metrics(self) -> Dict[str, Any]:
        """Get resource usage metrics for all services"""
        try:
            if not self.docker_client:
                return {"success": False, "error": "Docker client not available"}
            
            metrics = {}
            services = await self._get_service_names()
            
            for service_name in services:
                containers = self.docker_client.containers.list(
                    filters={"label": f"com.docker.compose.service={service_name}"}
                )
                
                if containers:
                    container = containers[0]
                    stats = container.stats(stream=False)
                    
                    # Extract relevant metrics
                    cpu_stats = stats.get("cpu_stats", {})
                    memory_stats = stats.get("memory_stats", {})
                    
                    metrics[service_name] = {
                        "cpu_usage": cpu_stats.get("cpu_usage", {}).get("total_usage", 0),
                        "memory_usage": memory_stats.get("usage", 0),
                        "memory_limit": memory_stats.get("limit", 0),
                        "network_rx": stats.get("networks", {}).get("eth0", {}).get("rx_bytes", 0),
                        "network_tx": stats.get("networks", {}).get("eth0", {}).get("tx_bytes", 0)
                    }
            
            return {"success": True, "metrics": metrics}
            
        except Exception as e:
            logger.error(f"❌ Error getting service metrics: {e}")
            return {"success": False, "error": str(e)}
    
    async def start_health_monitoring(self):
        """Start continuous health monitoring"""
        logger.info("🏥 Starting continuous health monitoring...")
        
        while True:
            try:
                await self.check_all_services_health()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"❌ Error in health monitoring: {e}")
                await asyncio.sleep(10)
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get summary of all services status"""
        return {
            "total_services": len(self.services_status),
            "healthy_services": sum(1 for status in self.services_status.values() if status.get("healthy", False)),
            "unhealthy_services": sum(1 for status in self.services_status.values() if not status.get("healthy", False)),
            "services": self.services_status
        }

async def main():
    docker_manager = DockerManager("/Users/Arief/Desktop/Nexus")
    
    

if __name__ == "__main__":
    asyncio.run(main())
