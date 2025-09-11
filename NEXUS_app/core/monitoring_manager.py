#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
📊 Monitoring Manager for Nexus Platform
Manages Prometheus, Grafana, Jaeger, and other monitoring tools.
Provides comprehensive observability and alerting capabilities.
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
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MonitoringManager:
    """Manages monitoring and observability tools for the Nexus Platform"""
    
    def __init__(self, workspace_path: str):
        """
          Init  
        
        
        Args:
            workspace_path: Description of workspace_path
    
        Example:
            TBD: Add usage example
        """
        self.workspace_path = Path(workspace_path)
        self.monitoring_path = self.workspace_path / "monitoring"
        self.monitoring_processes = {}
        self.running = True
        self.health_check_interval = 30  # seconds
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Initialize monitoring configurations
        self._initialize_monitoring_configs()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down monitoring manager...")
        self.running = False
        self.shutdown()
    
    def _initialize_monitoring_configs(self):
        """Initialize monitoring tool configurations"""
        self.monitoring_configs = {
            "prometheus": {
                "path": "monitoring/prometheus",
                "port": 9090,
                "config_file": "prometheus.yml",
                "data_dir": "data",
                "retention_days": 15,
                "status": "stopped",
                "health": "unknown",
                "last_check": None
            },
            "grafana": {
                "path": "monitoring/grafana",
                "port": 3000,
                "config_file": "grafana.ini",
                "data_dir": "data",
                "admin_user": "admin",
                "admin_password": "admin",
                "status": "stopped",
                "health": "unknown",
                "last_check": None
            },
            "jaeger": {
                "path": "monitoring/jaeger",
                "port": 16686,
                "collector_port": 14268,
                "agent_port": 6831,
                "storage": "memory",
                "status": "stopped",
                "health": "unknown",
                "last_check": None
            },
            "alertmanager": {
                "path": "monitoring/alertmanager",
                "port": 9093,
                "config_file": "alertmanager.yml",
                "data_dir": "data",
                "status": "stopped",
                "health": "unknown",
                "last_check": None
            },
            "node-exporter": {
                "path": "monitoring/node-exporter",
                "port": 9100,
                "collectors": ["cpu", "memory", "disk", "network"],
                "status": "stopped",
                "health": "unknown",
                "last_check": None
            }
        }
    
    async def start_monitoring_stack(self) -> Dict[str, Any]:
        """Start all monitoring tools"""
        logger.info("🚀 Starting monitoring stack...")
        
        results = {}
        
        # Start monitoring tools in dependency order
        startup_sequence = ["prometheus", "alertmanager", "grafana", "jaeger", "node-exporter"]
        
        for tool_name in startup_sequence:
            if tool_name in self.monitoring_configs:
                result = await self.start_monitoring_tool(tool_name)
                results[tool_name] = result
                
                # Wait between tool starts
                await asyncio.sleep(3)
        
        # Wait for all tools to be ready
        await asyncio.sleep(15)
        
        # Perform health checks
        health_status = await self.check_all_monitoring_health()
        
        return {
            "success": True,
            "message": "Monitoring stack started",
            "results": results,
            "health_status": health_status
        }
    
    async def start_monitoring_tool(self, tool_name: str) -> Dict[str, Any]:
        if tool_name not in self.monitoring_configs:
            return {"success": False, "error": f"Monitoring tool {tool_name} not found"}
        
        config = self.monitoring_configs[tool_name]
        tool_path = self.workspace_path / config["path"]
        
        if not tool_path.exists():
            return {"success": False, "error": f"Monitoring tool path not found: {tool_path}"}
        
        try:
            logger.info(f"🚀 Starting monitoring tool: {tool_name}")
            
            # Start tool based on type
            if tool_name == "prometheus":
                result = await self._start_prometheus(config)
            elif tool_name == "grafana":
                result = await self._start_grafana(config)
            elif tool_name == "jaeger":
                result = await self._start_jaeger(config)
            elif tool_name == "alertmanager":
                result = await self._start_alertmanager(config)
            elif tool_name == "node-exporter":
                result = await self._start_node_exporter(config)
            else:
                return {"success": False, "error": f"Unknown monitoring tool: {tool_name}"}
            
            if result["success"]:
                # Store process reference
                self.monitoring_processes[tool_name] = result["process"]
                
                # Update tool status
                self.monitoring_configs[tool_name]["status"] = "starting"
                self.monitoring_configs[tool_name]["last_check"] = time.time()
                
                # Start output monitoring
                threading.Thread(
                    target=self._monitor_tool_output,
                    args=(result["process"], tool_name),
                    daemon=True
                ).start()
                
                # Wait for tool to be ready
                await asyncio.sleep(5)
                
                # Check if tool is responding
                if await self._check_tool_responding(tool_name):
                    self.monitoring_configs[tool_name]["status"] = "running"
                    logger.info(f"✅ Monitoring tool {tool_name} started successfully")
                    
                    return {
                        "success": True,
                        "message": f"Monitoring tool {tool_name} started successfully",
                        "pid": result["process"].pid,
                        "port": config.get("port", "N/A")
                    }
                else:
                    # Tool not responding, stop it
                    result["process"].terminate()
                    del self.monitoring_processes[tool_name]
                    self.monitoring_configs[tool_name]["status"] = "failed"
                    
                    return {
                        "success": False,
                        "error": f"Monitoring tool {tool_name} failed to start - not responding"
                    }
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error starting monitoring tool {tool_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _start_prometheus(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Start Prometheus monitoring tool"""
        try:
            # Check if Prometheus binary exists
            prometheus_bin = self.workspace_path / config["path"] / "prometheus"
            if not prometheus_bin.exists():
                # Try to download or use system Prometheus
                prometheus_bin = "prometheus"
            
            # Create data directory
            data_dir = self.workspace_path / config["path"] / config["data_dir"]
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Start Prometheus process
            process = subprocess.Popen([
                str(prometheus_bin),
                f"--config.file={config['config_file']}",
                f"--storage.tsdb.path={data_dir}",
                f"--storage.tsdb.retention.time={config['retention_days']}d",
                f"--web.listen-address=:{config['port']}"
            ], cwd=str(self.workspace_path / config["path"]))
            
            return {"success": True, "process": process}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _start_grafana(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Start Grafana monitoring tool"""
        try:
            # Check if Grafana binary exists
            grafana_bin = self.workspace_path / config["path"] / "grafana-server"
            if not grafana_bin.exists():
                # Try to use system Grafana
                grafana_bin = "grafana-server"
            
            # Create data directory
            data_dir = self.workspace_path / config["path"] / config["data_dir"]
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Start Grafana process
            process = subprocess.Popen([
                str(grafana_bin),
                f"--config={config['config_file']}",
                f"--homepath={self.workspace_path / config['path']}",
                f"--pidfile={data_dir}/grafana.pid"
            ], cwd=str(self.workspace_path / config["path"]))
            
            return {"success": True, "process": process}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _start_jaeger(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Start Jaeger tracing tool"""
        try:
            # Check if Jaeger binary exists
            jaeger_bin = self.workspace_path / config["path"] / "jaeger-all-in-one"
            if not jaeger_bin.exists():
                # Try to use system Jaeger
                jaeger_bin = "jaeger-all-in-one"
            
            # Start Jaeger process
            process = subprocess.Popen([
                str(jaeger_bin),
                f"--http-port={config['port']}",
                f"--collector.http-port={config['collector_port']}",
                f"--agent.http-port={config['agent_port']}",
                f"--storage.type={config['storage']}"
            ], cwd=str(self.workspace_path / config["path"]))
            
            return {"success": True, "process": process}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _start_alertmanager(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Start Alertmanager tool"""
        try:
            # Check if Alertmanager binary exists
            alertmanager_bin = self.workspace_path / config["path"] / "alertmanager"
            if not alertmanager_bin.exists():
                # Try to use system Alertmanager
                alertmanager_bin = "alertmanager"
            
            # Create data directory
            data_dir = self.workspace_path / config["path"] / config["data_dir"]
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Start Alertmanager process
            process = subprocess.Popen([
                str(alertmanager_bin),
                f"--config.file={config['config_file']}",
                f"--storage.path={data_dir}",
                f"--web.listen-address=:{config['port']}"
            ], cwd=str(self.workspace_path / config["path"]))
            
            return {"success": True, "process": process}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _start_node_exporter(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Start Node Exporter tool"""
        try:
            # Check if Node Exporter binary exists
            node_exporter_bin = self.workspace_path / config["path"] / "node_exporter"
            if not node_exporter_bin.exists():
                # Try to use system Node Exporter
                node_exporter_bin = "node_exporter"
            
            # Start Node Exporter process
            collectors = ",".join(config["collectors"])
            process = subprocess.Popen([
                str(node_exporter_bin),
                f"--web.listen-address=:{config['port']}",
                f"--collectors.enabled={collectors}"
            ], cwd=str(self.workspace_path / config["path"]))
            
            return {"success": True, "process": process}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def stop_monitoring_stack(self) -> Dict[str, Any]:
        """Stop all monitoring tools"""
        logger.info("🛑 Stopping monitoring stack...")
        
        results = {}
        
        # Stop tools in reverse order
        stop_sequence = ["node-exporter", "jaeger", "grafana", "alertmanager", "prometheus"]
        
        for tool_name in stop_sequence:
            if tool_name in self.monitoring_processes:
                result = await self.stop_monitoring_tool(tool_name)
                results[tool_name] = result
        
        return {
            "success": True,
            "message": "Monitoring stack stopped",
            "results": results
        }
    
    async def stop_monitoring_tool(self, tool_name: str) -> Dict[str, Any]:
        if tool_name not in self.monitoring_processes:
            return {"success": False, "error": f"Monitoring tool {tool_name} not running"}
        
        try:
            logger.info(f"🛑 Stopping monitoring tool: {tool_name}")
            
            process = self.monitoring_processes[tool_name]
            
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
            del self.monitoring_processes[tool_name]
            
            # Update tool status
            self.monitoring_configs[tool_name]["status"] = "stopped"
            self.monitoring_configs[tool_name]["health"] = "unknown"
            
            logger.info(f"✅ Monitoring tool {tool_name} stopped successfully")
            
            return {
                "success": True,
                "message": f"Monitoring tool {tool_name} stopped successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Error stopping monitoring tool {tool_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def check_monitoring_health(self, tool_name: str) -> Dict[str, Any]:
        if tool_name not in self.monitoring_configs:
            return {"healthy": False, "error": f"Monitoring tool {tool_name} not found"}
        
        config = self.monitoring_configs[tool_name]
        
        try:
            # Check if process is running
            if tool_name not in self.monitoring_processes:
                config["status"] = "stopped"
                config["health"] = "unhealthy"
                return {"healthy": False, "error": "Monitoring tool not running"}
            
            process = self.monitoring_processes[tool_name]
            
            # Check process status
            if process.poll() is not None:
                # Process has terminated
                config["status"] = "stopped"
                config["health"] = "unhealthy"
                del self.monitoring_processes[tool_name]
                return {"healthy": False, "error": "Monitoring tool process terminated"}
            
            # Check if tool is responding
            if await self._check_tool_responding(tool_name):
                config["status"] = "running"
                config["health"] = "healthy"
                config["last_check"] = time.time()
                return {"healthy": True, "status": "running"}
            else:
                config["status"] = "unresponsive"
                config["health"] = "unhealthy"
                return {"healthy": False, "error": "Monitoring tool not responding"}
            
        except Exception as e:
            logger.error(f"❌ Error checking health for {tool_name}: {e}")
            config["health"] = "unhealthy"
            return {"healthy": False, "error": str(e)}
    
    async def check_all_monitoring_health(self) -> Dict[str, Any]:
        """Check health of all monitoring tools"""
        logger.info("🏥 Checking monitoring stack health...")
        
        health_results = {}
        
        for tool_name in self.monitoring_configs:
            health_status = await self.check_monitoring_health(tool_name)
            health_results[tool_name] = health_status
        
        # Calculate overall health
        healthy_tools = sum(1 for status in health_results.values() if status.get("healthy", False))
        total_tools = len(self.monitoring_configs)
        
        overall_health = {
            "total_tools": total_tools,
            "healthy_tools": healthy_tools,
            "unhealthy_tools": total_tools - healthy_tools,
            "health_percentage": (healthy_tools / total_tools * 100) if total_tools > 0 else 0,
            "tools": health_results
        }
        
        logger.info(f"🏥 Health check complete: {healthy_tools}/{total_tools} monitoring tools healthy")
        return overall_health
    
    async def _check_tool_responding(self, tool_name: str) -> bool:
        """Check if a monitoring tool is responding"""
        config = self.monitoring_configs[tool_name]
        
        try:
            # Try to connect to the tool
            if tool_name == "prometheus":
                response = requests.get(f"http://localhost:{config['port']}/-/healthy", timeout=5)
            elif tool_name == "grafana":
                response = requests.get(f"http://localhost:{config['port']}/api/health", timeout=5)
            elif tool_name == "jaeger":
                response = requests.get(f"http://localhost:{config['port']}/", timeout=5)
            elif tool_name == "alertmanager":
                response = requests.get(f"http://localhost:{config['port']}/-/healthy", timeout=5)
            elif tool_name == "node-exporter":
                response = requests.get(f"http://localhost:{config['port']}/metrics", timeout=5)
            else:
                return False
            
            return response.status_code < 500  # Any non-server error is OK
            
        except:
            return False
    
    def _monitor_tool_output(self, process: subprocess.Popen, tool_name: str):
        """Monitor monitoring tool process output"""
        try:
            while process.poll() is None:
                # Read stdout
                if process.stdout:
                    line = process.stdout.readline()
                    if line:
                        logger.info(f"[{tool_name}] {line.strip()}")
                
                # Read stderr
                if process.stderr:
                    line = process.stderr.readline()
                    if line:
                        logger.error(f"[{tool_name}] ERROR: {line.strip()}")
                
                time.sleep(0.1)
            
            # Process has terminated
            logger.info(f"Monitoring tool {tool_name} process terminated with code {process.returncode}")
            
        except Exception as e:
            logger.error(f"Error monitoring tool {tool_name}: {e}")
    
    async def get_monitoring_metrics(self) -> Dict[str, Any]:
        """Get metrics from monitoring tools"""
        try:
            metrics = {}
            
            # Get Prometheus metrics
            if "prometheus" in self.monitoring_processes:
                try:
                    response = requests.get("http://localhost:9090/api/v1/query?query=up", timeout=5)
                    if response.status_code == 200:
                        metrics["prometheus"] = response.json()
                except:
                    metrics["prometheus"] = {"error": "Failed to fetch metrics"}
            
            # Get Node Exporter metrics
            if "node-exporter" in self.monitoring_processes:
                try:
                    response = requests.get("http://localhost:9100/metrics", timeout=5)
                    if response.status_code == 200:
                        metrics["node-exporter"] = {"status": "healthy", "metrics_count": len(response.text.split('\n'))}
                except:
                    metrics["node-exporter"] = {"error": "Failed to fetch metrics"}
            
            return {"success": True, "metrics": metrics}
            
        except Exception as e:
            logger.error(f"❌ Error getting monitoring metrics: {e}")
            return {"success": False, "error": str(e)}
    
    async def start_health_monitoring(self):
        """Start continuous health monitoring"""
        logger.info("🏥 Starting continuous monitoring health monitoring...")
        
        while self.running:
            try:
                await self.check_all_monitoring_health()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"❌ Error in monitoring health monitoring: {e}")
                await asyncio.sleep(10)
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get summary of all monitoring tools status"""
        return {
            "total_tools": len(self.monitoring_configs),
            "running_tools": len(self.monitoring_processes),
            "stopped_tools": len(self.monitoring_configs) - len(self.monitoring_processes),
            "tools": self.monitoring_configs
        }
    
    def shutdown(self):
        """Gracefully shutdown the monitoring manager"""
        logger.info("🛑 Shutting down monitoring manager...")
        
        # Stop all monitoring tools
        for tool_name in list(self.monitoring_processes.keys()):
            try:
                process = self.monitoring_processes[tool_name]
                process.terminate()
                process.wait(timeout=5)
            except:
                pass
        
        logger.info("✅ Monitoring manager shutdown complete")

async def main():
    monitoring_manager = MonitoringManager("/Users/Arief/Desktop/Nexus")
    
    
    
    # Wait a moment
    await asyncio.sleep(5)
    

if __name__ == "__main__":
    asyncio.run(main())
