#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🚪 API Gateway Manager for Nexus Platform
Manages FastAPI services, routing, authentication, and API health monitoring.
"""

import asyncio
import logging
import subprocess
import time
import os
from pathlib import Path # Import Path
from typing import Dict, List, Optional, Any
import json
import signal
import threading
import requests
import yaml
import httpx # Import httpx for making async HTTP requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIGatewayManager:
    """Manages API Gateway and FastAPI services for the Nexus Platform"""
    
    def __init__(self, workspace_path: str):
        """
          Init  
        
        
        Args:
            workspace_path: Description of workspace_path
    
        Example:
            TBD: Add usage example
        """
        self.workspace_path = Path(workspace_path) # Convert to Path object
        self.api_processes = {}
        self.gateway_process = None
        self.running = True
        self.health_check_interval = 30  # seconds
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Initialize API configurations
        self._initialize_api_configs()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down API Gateway manager...")
        self.running = False
        self.shutdown()
    
    def _initialize_api_configs(self):
        """Initialize API service configurations"""
        self.api_configs = {
            "main-api": {
                "path": "API&AI/generated_api",
                "port": 8000,
                "script": "main.py",
                "env": {
                    "API_ENV": "development",
                    "DATABASE_URL": "sqlite:///./nexus.db",
                    "DEBUG": "true"
                },
                "status": "stopped",
                "health": "unknown",
                "last_check": None
            },
            "auth-service": {
                "path": "API&AI/generated_api/auth",
                "port": 8001,
                "script": "auth_service.py",
                "env": {
                    "AUTH_SERVICE_ENV": "development",
                    "JWT_SECRET": "your-secret-key",
                    "DEBUG": "true"
                },
                "status": "stopped",
                "health": "unknown",
                "last_check": None
            },
            "ai-service": {
                "path": "API&AI/generated_api",
                "port": 8002,
                "script": "ai_service.py",
                "env": {
                    "AI_SERVICE_ENV": "development",
                    "OPENAI_API_KEY": "your-api-key",
                    "DEBUG": "true"
                },
                "status": "stopped",
                "health": "unknown",
                "last_check": None
            },
            "gateway": {
                "path": "core",
                "port": 8080,
                "script": "api_gateway.py",
                "env": {
                    "GATEWAY_ENV": "development",
                    "DEBUG": "true",
                    "CORS_ORIGINS": "*"
                },
                "status": "stopped",
                "health": "unknown",
                "last_check": None
            }
        }
    
    async def start_api_services(self) -> Dict[str, Any]:
        """Start all API services"""
        logger.info("🚀 Starting all API services...")
        
        results = {}
        
        # Start individual API services first
        for service_name, config in self.api_configs.items():
            if service_name != "gateway":
                result = await self.start_api_service(service_name)
                results[service_name] = result
                
                # Wait a moment between service starts
                await asyncio.sleep(3)
        
        # Wait for API services to be ready
        await asyncio.sleep(10)
        
        # Start the gateway last
        gateway_result = await self.start_api_service("gateway")
        results["gateway"] = gateway_result
        
        # Wait for gateway to be ready
        await asyncio.sleep(5)
        
        # Perform health checks
        health_status = await self.check_all_api_health()
        
        return {
            "success": True,
            "message": "All API services started",
            "results": results,
            "health_status": health_status
        }
    
    async def start_api_service(self, service_name: str) -> Dict[str, Any]:
        if service_name not in self.api_configs:
            return {"success": False, "error": f"API service {service_name} not found"}
        
        config = self.api_configs[service_name]
        service_path = self.workspace_path / config["path"]
        script_path = service_path / config["script"]
        
        if not script_path.exists():
            return {"success": False, "error": f"API script not found: {script_path}"}
        
        try:
            logger.info(f"🚀 Starting API service: {service_name}")
            
            # Check if virtual environment exists
            venv_path = self.workspace_path / "frenly_env"
            python_exec = str(venv_path / "bin" / "python") if venv_path.exists() else "python"
            
            # Start API service process
            process = subprocess.Popen(
                [python_exec, str(script_path)],
                cwd=str(service_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=self._prepare_environment(config)
            )
            
            # Store process reference
            if service_name == "gateway":
                self.gateway_process = process
            else:
                self.api_processes[service_name] = process
            
            # Update service status
            self.api_configs[service_name]["status"] = "starting"
            self.api_configs[service_name]["last_check"] = time.time()
            
            # Start output monitoring
            threading.Thread(
                target=self._monitor_api_output,
                args=(process, service_name),
                daemon=True
            ).start()
            
            # Wait for service to be ready
            await asyncio.sleep(5)
            
            # Check if service is responding
            if await self._check_service_responding(service_name):
                self.api_configs[service_name]["status"] = "running"
                logger.info(f"✅ API service {service_name} started successfully")
                
                return {
                    "success": True,
                    "message": f"API service {service_name} started successfully",
                    "pid": process.pid,
                    "port": config["port"]
                }
            else:
                # Service not responding, stop it
                process.terminate()
                if service_name == "gateway":
                    self.gateway_process = None
                else:
                    del self.api_processes[service_name]
                self.api_configs[service_name]["status"] = "failed"
                
                return {
                    "success": False,
                    "error": f"API service {service_name} failed to start - not responding"
                }
            
        except Exception as e:
            logger.error(f"❌ Error starting API service {service_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def stop_api_services(self) -> Dict[str, Any]:
        """Stop all running API services"""
        logger.info("🛑 Stopping all API services...")
        
        results = {}
        
        # Stop gateway first
        if self.gateway_process:
            result = await self.stop_api_service("gateway")
            results["gateway"] = result
        
        # Stop individual API services
        for service_name in list(self.api_processes.keys()):
            result = await self.stop_api_service(service_name)
            results[service_name] = result
        
        return {
            "success": True,
            "message": "All API services stopped",
            "results": results
        }
    
    async def stop_api_service(self, service_name: str) -> Dict[str, Any]:
        if service_name not in self.api_configs:
            return {"success": False, "error": f"API service {service_name} not found"}
        
        try:
            logger.info(f"🛑 Stopping API service: {service_name}")
            
            if service_name == "gateway":
                process = self.gateway_process
                self.gateway_process = None
            else:
                if service_name not in self.api_processes:
                    return {"success": False, "error": f"API service {service_name} not running"}
                process = self.api_processes[service_name]
                del self.api_processes[service_name]
            
            if not process:
                return {"success": False, "error": f"API service {service_name} process not found"}
            
            # Send SIGTERM first
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                # Force kill if not responding
                process.kill()
                process.wait()
            
            # Update service status
            self.api_configs[service_name]["status"] = "stopped"
            self.api_configs[service_name]["health"] = "unknown"
            
            logger.info(f"✅ API service {service_name} stopped successfully")
            
            return {
                "success": True,
                "message": f"API service {service_name} stopped successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Error stopping API service {service_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def restart_api_services(self) -> Dict[str, Any]:
        """Restart all API services"""
        logger.info("🔄 Restarting all API services...")
        
        # Stop all services
        stop_result = await self.stop_api_services()
        if not stop_result["success"]:
            return stop_result
        
        # Wait a moment
        await asyncio.sleep(5)
        
        # Start all services again
        start_result = await self.start_api_services()
        return start_result
    
    async def check_api_health(self, service_name: str) -> Dict[str, Any]:
        if service_name not in self.api_configs:
            return {"healthy": False, "error": f"API service {service_name} not found"}
        
        config = self.api_configs[service_name]
        
        try:
            # Check if process is running
            if service_name == "gateway":
                process = self.gateway_process
            else:
                if service_name not in self.api_processes:
                    config["status"] = "stopped"
                    config["health"] = "unhealthy"
                    return {"healthy": False, "error": "API service not running"}
                process = self.api_processes[service_name]
            
            if not process:
                config["status"] = "stopped"
                config["health"] = "unhealthy"
                return {"healthy": False, "error": "API service process not found"}
            
            # Check process status
            if process.poll() is not None:
                # Process has terminated
                config["status"] = "stopped"
                config["health"] = "unhealthy"
                if service_name == "gateway":
                    self.gateway_process = None
                else:
                    del self.api_processes[service_name]
                return {"healthy": False, "error": "API service process terminated"}
            
            # Check if service is responding
            if await self._check_service_responding(service_name):
                config["status"] = "running"
                config["health"] = "healthy"
                config["last_check"] = time.time()
                return {"healthy": True, "status": "running"}
            else:
                config["status"] = "unresponsive"
                config["health"] = "unhealthy"
                return {"healthy": False, "error": "API service not responding"}
            
        except Exception as e:
            logger.error(f"❌ Error checking health for {service_name}: {e}")
            config["health"] = "unhealthy"
            return {"healthy": False, "error": str(e)}
    
    async def check_all_api_health(self) -> Dict[str, Any]:
        """Check health of all API services"""
        logger.info("🏥 Checking health of all API services...")
        
        health_results = {}
        
        for service_name in self.api_configs:
            health_status = await self.check_api_health(service_name)
            health_results[service_name] = health_status
        
        # Calculate overall health
        healthy_services = sum(1 for status in health_results.values() if status.get("healthy", False))
        total_services = len(self.api_configs)
        
        overall_health = {
            "total_services": total_services,
            "healthy_services": healthy_services,
            "unhealthy_services": total_services - healthy_services,
            "health_percentage": (healthy_services / total_services * 100) if total_services > 0 else 0,
            "services": health_results
        }
        
        logger.info(f"🏥 Health check complete: {healthy_services}/{total_services} API services healthy")
        return overall_health
    
    async def _check_service_responding(self, service_name: str) -> bool:
        """Check if an API service is responding"""
        config = self.api_configs[service_name]
        
        try:
            # Try to connect to the service
            response = requests.get(f"http://localhost:{config['port']}/health", timeout=5)
            return response.status_code == 200
        except:
            try:
                # Try root endpoint if health endpoint doesn't exist
                response = requests.get(f"http://localhost:{config['port']}/", timeout=5)
                return response.status_code < 500  # Any non-server error is OK
            except:
                return False
    
    def _prepare_environment(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Prepare environment variables for API processes"""
        env = os.environ.copy()
        env.update(config["env"])
        env["PYTHONPATH"] = str(self.workspace_path)
        env["PORT"] = str(config["port"])
        return env
    
    def _monitor_api_output(self, process: subprocess.Popen, service_name: str):
        """Monitor API process output"""
        try:
            while process.poll() is None:
                # Read stdout
                if process.stdout:
                    line = process.stdout.readline()
                    if line:
                        logger.info(f"[{service_name}] {line.strip()}")
                
                # Read stderr
                if process.stderr:
                    line = process.stderr.readline()
                    if line:
                        logger.error(f"[{service_name}] ERROR: {line.strip()}")
                
                time.sleep(0.1)
            
            # Process has terminated
            logger.info(f"API service {service_name} process terminated with code {process.returncode}")
            
        except Exception as e:
            logger.error(f"Error monitoring API service {service_name}: {e}")
    
    async def get_api_logs(self, service_name: str, lines: int = 50) -> Dict[str, Any]:
        if service_name == "gateway":
            process = self.gateway_process
        else:
            if service_name not in self.api_processes:
                return {"success": False, "error": f"API service {service_name} not running"}
            process = self.api_processes[service_name]
        
        try:
            return {
                "success": True,
                "service": service_name,
                "pid": process.pid,
                "status": "running" if process.poll() is None else "terminated",
                "return_code": process.returncode if process.poll() is not None else None
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting logs for {service_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def start_health_monitoring(self):
        """Start continuous health monitoring"""
        logger.info("🏥 Starting continuous API health monitoring...")
        
        while self.running:
            try:
                await self.check_all_api_health()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"❌ Error in API health monitoring: {e}")
                await asyncio.sleep(10)
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get summary of all API services status"""
        return {
            "total_services": len(self.api_configs),
            "running_services": len(self.api_processes) + (1 if self.gateway_process else 0),
            "stopped_services": len(self.api_configs) - len(self.api_processes) - (1 if self.gateway_process else 0),
            "services": self.api_configs
        }
    
    def shutdown(self):
        """Gracefully shutdown the API Gateway manager"""
        logger.info("🛑 Shutting down API Gateway manager...")
        
        # Stop all API services
        for service_name in list(self.api_processes.keys()):
            try:
                process = self.api_processes[service_name]
                process.terminate()
                process.wait(timeout=5)
            except:
                pass
        
        # Stop gateway
        if self.gateway_process:
            try:
                self.gateway_process.terminate()
                self.gateway_process.wait(timeout=5)
            except:
                pass
        
        logger.info("✅ API Gateway manager shutdown complete")

    async def register_mcp_agent(self):
        """Public method to register this API Gateway Manager as an agent with the MCP Gateway API."""
        await self._register_as_mcp_agent()

    async def _register_as_mcp_agent(self):
        """Internal method to handle the actual registration with the MCP Gateway API."""
        mcp_gateway_url = "http://localhost:8000/api/v1/mcp/agents/register" # Assuming API runs on 8000
        agent_id = "api-gateway-manager"
        agent_name = "API Gateway Manager"
        agent_type = "api-gateway"
        
        payload = {
            "agent_id": agent_id,
            "name": agent_name,
            "agent_type": agent_type,
            "workspace_path": str(self.workspace_path)
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(mcp_gateway_url, json=payload)
                response.raise_for_status()
                logger.info(f"Successfully registered API Gateway Manager as MCP agent: {response.json()}")
        except httpx.RequestError as exc:
            logger.error(f"Error registering API Gateway Manager as MCP agent: {exc}")
        except httpx.HTTPStatusError as exc:
            logger.error(f"HTTP error registering API Gateway Manager as MCP agent: {exc.response.status_code} - {exc.response.text}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during MCP agent registration: {e}")

async def main():
    api_manager = APIGatewayManager("/Users/Arief/Desktop/Nexus")
    
    
    
    # Wait a moment
    await asyncio.sleep(5)
    

if __name__ == "__main__":
    asyncio.run(main())
