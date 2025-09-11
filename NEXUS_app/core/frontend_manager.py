#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🌐 Frontend Manager for Nexus Platform
Manages React/Next.js frontend services, build processes, and development servers.
"""

import asyncio
import logging
import subprocess
import time
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import signal
import threading
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FrontendManager:
    """Manages frontend services for the Nexus Platform"""
    
    def __init__(self, workspace_path: str):
        """
          Init  
        
        
        Args:
            workspace_path: Description of workspace_path
    
        Example:
            TBD: Add usage example
        """
        self.workspace_path = Path(workspace_path)
        self.frontend_path = self.workspace_path / "frontend"
        self.frontend_processes = {}
        self.build_processes = {}
        self.running = True
        self.health_check_interval = 30  # seconds
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Initialize frontend configurations
        self._initialize_frontend_configs()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down frontend manager...")
        self.running = False
        self.shutdown()
    
    def _initialize_frontend_configs(self):
        """Initialize frontend configurations"""
        self.frontend_configs = {
            "nexus-app": {
                "path": "frontend/nexus-app",
                "port": 3000,
                "script": "dev",
                "build_script": "build",
                "start_script": "start",
                "package_manager": "npm",
                "status": "stopped",
                "health": "unknown",
                "last_check": None
            },
            "admin-dashboard": {
                "path": "frontend/admin-dashboard",
                "port": 3001,
                "script": "dev",
                "build_script": "build",
                "start_script": "start",
                "package_manager": "npm",
                "status": "stopped",
                "health": "unknown",
                "last_check": None
            },
            "user-portal": {
                "path": "frontend/user-portal",
                "port": 3002,
                "script": "dev",
                "build_script": "build",
                "start_script": "start",
                "package_manager": "npm",
                "status": "stopped",
                "health": "unknown",
                "last_check": None
            }
        }
    
    async def start_frontend_services(self) -> Dict[str, Any]:
        """Start all frontend services"""
        logger.info("🚀 Starting all frontend services...")
        
        results = {}
        for service_name, config in self.frontend_configs.items():
            result = await self.start_frontend_service(service_name)
            results[service_name] = result
            
            # Wait a moment between service starts
            await asyncio.sleep(3)
        
        # Wait for all services to be ready
        await asyncio.sleep(15)
        
        # Perform health checks
        health_status = await self.check_all_frontend_health()
        
        return {
            "success": True,
            "message": "All frontend services started",
            "results": results,
            "health_status": health_status
        }
    
    async def start_frontend_service(self, service_name: str) -> Dict[str, Any]:
        if service_name not in self.frontend_configs:
            return {"success": False, "error": f"Frontend service {service_name} not found"}
        
        config = self.frontend_configs[service_name]
        service_path = self.workspace_path / config["path"]
        
        if not service_path.exists():
            return {"success": False, "error": f"Frontend service path not found: {service_path}"}
        
        try:
            logger.info(f"🚀 Starting frontend service: {service_name}")
            
            # Check if dependencies are installed
            if not (service_path / "node_modules").exists():
                logger.info(f"📦 Installing dependencies for {service_name}...")
                install_result = await self._install_dependencies(service_name)
                if not install_result["success"]:
                    return install_result
            
            # Start development server
            process = subprocess.Popen(
                [config["package_manager"], "run", config["script"]],
                cwd=str(service_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=self._prepare_environment(config)
            )
            
            # Store process reference
            self.frontend_processes[service_name] = process
            
            # Update service status
            self.frontend_configs[service_name]["status"] = "starting"
            self.frontend_configs[service_name]["last_check"] = time.time()
            
            # Start output monitoring
            threading.Thread(
                target=self._monitor_frontend_output,
                args=(process, service_name),
                daemon=True
            ).start()
            
            # Wait for service to be ready
            await asyncio.sleep(5)
            
            # Check if service is responding
            if await self._check_service_responding(service_name):
                self.frontend_configs[service_name]["status"] = "running"
                logger.info(f"✅ Frontend service {service_name} started successfully")
                
                return {
                    "success": True,
                    "message": f"Frontend service {service_name} started successfully",
                    "pid": process.pid,
                    "port": config["port"]
                }
            else:
                # Service not responding, stop it
                process.terminate()
                del self.frontend_processes[service_name]
                self.frontend_configs[service_name]["status"] = "failed"
                
                return {
                    "success": False,
                    "error": f"Frontend service {service_name} failed to start - not responding"
                }
            
        except Exception as e:
            logger.error(f"❌ Error starting frontend service {service_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def stop_frontend_services(self) -> Dict[str, Any]:
        """Stop all running frontend services"""
        logger.info("🛑 Stopping all frontend services...")
        
        results = {}
        for service_name in list(self.frontend_processes.keys()):
            result = await self.stop_frontend_service(service_name)
            results[service_name] = result
        
        return {
            "success": True,
            "message": "All frontend services stopped",
            "results": results
        }
    
    async def stop_frontend_service(self, service_name: str) -> Dict[str, Any]:
        if service_name not in self.frontend_processes:
            return {"success": False, "error": f"Frontend service {service_name} not running"}
        
        try:
            logger.info(f"🛑 Stopping frontend service: {service_name}")
            
            process = self.frontend_processes[service_name]
            
            # Send SIGTERM first
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                # Force kill if not responding
                process.kill()
                process.wait()
            
            # Remove from processes
            del self.frontend_processes[service_name]
            
            # Update service status
            self.frontend_configs[service_name]["status"] = "stopped"
            self.frontend_configs[service_name]["health"] = "unknown"
            
            logger.info(f"✅ Frontend service {service_name} stopped successfully")
            
            return {
                "success": True,
                "message": f"Frontend service {service_name} stopped successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Error stopping frontend service {service_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def build_frontend_service(self, service_name: str) -> Dict[str, Any]:
        if service_name not in self.frontend_configs:
            return {"success": False, "error": f"Frontend service {service_name} not found"}
        
        config = self.frontend_configs[service_name]
        service_path = self.workspace_path / config["path"]
        
        try:
            logger.info(f"🔨 Building frontend service: {service_name}")
            
            # Check if dependencies are installed
            if not (service_path / "node_modules").exists():
                install_result = await self._install_dependencies(service_name)
                if not install_result["success"]:
                    return install_result
            
            # Start build process
            process = subprocess.Popen(
                [config["package_manager"], "run", config["build_script"]],
                cwd=str(service_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=self._prepare_environment(config)
            )
            
            # Store build process reference
            self.build_processes[service_name] = process
            
            # Wait for build to complete
            stdout, stderr = process.communicate()
            
            # Remove from build processes
            del self.build_processes[service_name]
            
            if process.returncode == 0:
                logger.info(f"✅ Frontend service {service_name} built successfully")
                return {
                    "success": True,
                    "message": f"Frontend service {service_name} built successfully",
                    "stdout": stdout,
                    "stderr": stderr
                }
            else:
                logger.error(f"❌ Build failed for {service_name}: {stderr}")
                return {
                    "success": False,
                    "error": f"Build failed: {stderr}",
                    "stdout": stdout,
                    "stderr": stderr
                }
            
        except Exception as e:
            logger.error(f"❌ Error building frontend service {service_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def build_all_frontend_services(self) -> Dict[str, Any]:
        """Build all frontend services for production"""
        logger.info("🔨 Building all frontend services...")
        
        results = {}
        for service_name in self.frontend_configs:
            result = await self.build_frontend_service(service_name)
            results[service_name] = result
            
            # Wait a moment between builds
            await asyncio.sleep(2)
        
        return {
            "success": True,
            "message": "All frontend services built",
            "results": results
        }
    
    async def check_frontend_health(self, service_name: str) -> Dict[str, Any]:
        if service_name not in self.frontend_configs:
            return {"healthy": False, "error": f"Frontend service {service_name} not found"}
        
        config = self.frontend_configs[service_name]
        
        try:
            # Check if process is running
            if service_name not in self.frontend_processes:
                config["status"] = "stopped"
                config["health"] = "unhealthy"
                return {"healthy": False, "error": "Frontend service not running"}
            
            process = self.frontend_processes[service_name]
            
            # Check process status
            if process.poll() is not None:
                # Process has terminated
                config["status"] = "stopped"
                config["health"] = "unhealthy"
                del self.frontend_processes[service_name]
                return {"healthy": False, "error": "Frontend service process terminated"}
            
            # Check if service is responding
            if await self._check_service_responding(service_name):
                config["status"] = "running"
                config["health"] = "healthy"
                config["last_check"] = time.time()
                return {"healthy": True, "status": "running"}
            else:
                config["status"] = "unresponsive"
                config["health"] = "unhealthy"
                return {"healthy": False, "error": "Frontend service not responding"}
            
        except Exception as e:
            logger.error(f"❌ Error checking health for {service_name}: {e}")
            config["health"] = "unhealthy"
            return {"healthy": False, "error": str(e)}
    
    async def check_all_frontend_health(self) -> Dict[str, Any]:
        """Check health of all frontend services"""
        logger.info("🏥 Checking health of all frontend services...")
        
        health_results = {}
        
        for service_name in self.frontend_configs:
            health_status = await self.check_frontend_health(service_name)
            health_results[service_name] = health_status
        
        # Calculate overall health
        healthy_services = sum(1 for status in health_results.values() if status.get("healthy", False))
        total_services = len(self.frontend_configs)
        
        overall_health = {
            "total_services": total_services,
            "healthy_services": healthy_services,
            "unhealthy_services": total_services - healthy_services,
            "health_percentage": (healthy_services / total_services * 100) if total_services > 0 else 0,
            "services": health_results
        }
        
        logger.info(f"🏥 Health check complete: {healthy_services}/{total_services} frontend services healthy")
        return overall_health
    
    async def _install_dependencies(self, service_name: str) -> Dict[str, Any]:
        """Install dependencies for a frontend service"""
        config = self.frontend_configs[service_name]
        service_path = self.workspace_path / config["path"]
        
        try:
            logger.info(f"📦 Installing dependencies for {service_name}...")
            
            process = subprocess.run(
                [config["package_manager"], "install"],
                cwd=str(service_path),
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if process.returncode == 0:
                logger.info(f"✅ Dependencies installed for {service_name}")
                return {"success": True, "message": "Dependencies installed successfully"}
            else:
                logger.error(f"❌ Failed to install dependencies for {service_name}: {process.stderr}")
                return {"success": False, "error": process.stderr}
            
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Dependency installation timed out"}
        except Exception as e:
            logger.error(f"❌ Error installing dependencies for {service_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _check_service_responding(self, service_name: str) -> bool:
        """Check if a frontend service is responding"""
        config = self.frontend_configs[service_name]
        
        try:
            response = requests.get(f"http://localhost:{config['port']}", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _prepare_environment(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Prepare environment variables for frontend processes"""
        env = os.environ.copy()
        env["PORT"] = str(config["port"])
        env["NODE_ENV"] = "development"
        return env
    
    def _monitor_frontend_output(self, process: subprocess.Popen, service_name: str):
        """Monitor frontend process output"""
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
            logger.info(f"Frontend service {service_name} process terminated with code {process.returncode}")
            
        except Exception as e:
            logger.error(f"Error monitoring frontend service {service_name}: {e}")
    
    async def start_health_monitoring(self):
        """Start continuous health monitoring"""
        logger.info("🏥 Starting continuous frontend health monitoring...")
        
        while self.running:
            try:
                await self.check_all_frontend_health()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"❌ Error in frontend health monitoring: {e}")
                await asyncio.sleep(10)
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get summary of all frontend services status"""
        return {
            "total_services": len(self.frontend_configs),
            "running_services": len(self.frontend_processes),
            "stopped_services": len(self.frontend_configs) - len(self.frontend_processes),
            "services": self.frontend_configs
        }
    
    def shutdown(self):
        """Gracefully shutdown the frontend manager"""
        logger.info("🛑 Shutting down frontend manager...")
        
        # Stop all frontend services
        for service_name in list(self.frontend_processes.keys()):
            try:
                process = self.frontend_processes[service_name]
                process.terminate()
                process.wait(timeout=5)
            except:
                pass
        
        # Stop all build processes
        for service_name in list(self.build_processes.keys()):
            try:
                process = self.build_processes[service_name]
                process.terminate()
                process.wait(timeout=5)
            except:
                pass
        
        logger.info("✅ Frontend manager shutdown complete")

async def main():
    frontend_manager = FrontendManager("/Users/Arief/Desktop/Nexus")
    
    
    
    # Wait a moment
    await asyncio.sleep(5)
    

if __name__ == "__main__":
    asyncio.run(main())
