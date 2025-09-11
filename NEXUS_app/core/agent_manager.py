#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🤖 Agent System Manager for Nexus Platform
Manages agent coordination, MCP server integration, and agent health monitoring.
"""

import asyncio
import logging
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import signal
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentManager:
    """Manages agent coordination and MCP servers for the Nexus Platform"""
    
    def __init__(self, workspace_path: str):
        """
          Init  
        
        
        Args:
            workspace_path: Description of workspace_path
    
        Example:
            TBD: Add usage example
        """
        self.workspace_path = Path(workspace_path)
        self.agents = {}
        self.mcp_servers = {}
        self.agent_processes = {}
        self.health_check_interval = 30  # seconds
        self.running = True
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Initialize agent configurations
        self._initialize_agent_configs()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down agent manager...")
        self.running = False
        self.shutdown()
    
    def _initialize_agent_configs(self):
        """Initialize agent configurations"""
        self.agents = {
            "agent-coordinator": {
                "script": "core/agent_coordinator.py",
                "env": {
                    "AGENT_COORDINATOR_WORKSPACE_PATH": str(self.workspace_path),
                    "AGENT_COORDINATOR_ENABLED": "true",
                    "AGENT_COORDINATOR_INTER_AGENT_COMMUNICATION": "true"
                },
                "status": "stopped",
                "health": "unknown",
                "last_check": None
            },
            "process-monitor": {
                "script": "core/process_monitor.py",
                "env": {
                    "PROCESS_MONITOR_WORKSPACE_PATH": str(self.workspace_path),
                    "PROCESS_MONITORING_ENABLED": "true"
                },
                "status": "stopped",
                "health": "unknown",
                "last_check": None
            },
            "frenly-meta-agent": {
                "script": "core/frenly_meta_agent.py",
                "env": {
                    "FRENLY_WORKSPACE_PATH": str(self.workspace_path),
                    "FRENLY_AGENT_COORDINATION_ENABLED": "true",
                    "FRENLY_INTER_AGENT_COMMUNICATION": "true"
                },
                "status": "stopped",
                "health": "unknown",
                "last_check": None
            },
            "agent-compliance-checker": {
                "script": "core/agent_compliance_checker.py",
                "env": {
                    "COMPLIANCE_CHECKER_WORKSPACE_PATH": str(self.workspace_path),
                    "COMPLIANCE_CHECKING_ENABLED": "true"
                },
                "status": "stopped",
                "health": "unknown",
                "last_check": None
            }
        }
    
    async def start_agents(self) -> Dict[str, Any]:
        """Start all configured agents"""
        logger.info("🚀 Starting all agents...")
        
        results = {}
        for agent_name, config in self.agents.items():
            result = await self.start_agent(agent_name)
            results[agent_name] = result
            
            # Wait a moment between agent starts
            await asyncio.sleep(2)
        
        # Wait for all agents to be ready
        await asyncio.sleep(10)
        
        # Perform health checks
        health_status = await self.check_all_agents_health()
        
        return {
            "success": True,
            "message": "All agents started",
            "results": results,
            "health_status": health_status
        }
    
    async def start_agent(self, agent_name: str) -> Dict[str, Any]:
        if agent_name not in self.agents:
            return {"success": False, "error": f"Agent {agent_name} not found"}
        
        config = self.agents[agent_name]
        script_path = self.workspace_path / config["script"]
        
        if not script_path.exists():
            return {"success": False, "error": f"Agent script not found: {script_path}"}
        
        try:
            logger.info(f"🚀 Starting agent: {agent_name}")
            
            # Prepare environment
            env = self._prepare_environment(config["env"])
            
            # Start agent process
            process = subprocess.Popen(
                ["python", str(script_path)],
                env=env,
                cwd=str(self.workspace_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Store process reference
            self.agent_processes[agent_name] = process
            
            # Update agent status
            self.agents[agent_name]["status"] = "starting"
            self.agents[agent_name]["last_check"] = time.time()
            
            # Start output monitoring
            threading.Thread(
                target=self._monitor_agent_output,
                args=(process, agent_name),
                daemon=True
            ).start()
            
            logger.info(f"✅ Agent {agent_name} started successfully")
            
            return {
                "success": True,
                "message": f"Agent {agent_name} started successfully",
                "pid": process.pid
            }
            
        except Exception as e:
            logger.error(f"❌ Error starting agent {agent_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def stop_agents(self) -> Dict[str, Any]:
        """Stop all running agents"""
        logger.info("🛑 Stopping all agents...")
        
        results = {}
        for agent_name in list(self.agent_processes.keys()):
            result = await self.stop_agent(agent_name)
            results[agent_name] = result
        
        return {
            "success": True,
            "message": "All agents stopped",
            "results": results
        }
    
    async def stop_agent(self, agent_name: str) -> Dict[str, Any]:
        if agent_name not in self.agent_processes:
            return {"success": False, "error": f"Agent {agent_name} not running"}
        
        try:
            logger.info(f"🛑 Stopping agent: {agent_name}")
            
            process = self.agent_processes[agent_name]
            
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
            del self.agent_processes[agent_name]
            
            # Update agent status
            self.agents[agent_name]["status"] = "stopped"
            self.agents[agent_name]["health"] = "unknown"
            
            logger.info(f"✅ Agent {agent_name} stopped successfully")
            
            return {
                "success": True,
                "message": f"Agent {agent_name} stopped successfully"
            }
            
        except Exception as e:
            logger.error(f"❌ Error stopping agent {agent_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def restart_agents(self) -> Dict[str, Any]:
        """Restart all agents"""
        logger.info("🔄 Restarting all agents...")
        
        # Stop all agents
        stop_result = await self.stop_agents()
        if not stop_result["success"]:
            return stop_result
        
        # Wait a moment
        await asyncio.sleep(5)
        
        # Start all agents again
        start_result = await self.start_agents()
        return start_result
    
    async def check_agent_health(self, agent_name: str) -> Dict[str, Any]:
        if agent_name not in self.agents:
            return {"healthy": False, "error": f"Agent {agent_name} not found"}
        
        config = self.agents[agent_name]
        
        try:
            # Check if process is running
            if agent_name not in self.agent_processes:
                config["status"] = "stopped"
                config["health"] = "unhealthy"
                return {"healthy": False, "error": "Agent process not running"}
            
            process = self.agent_processes[agent_name]
            
            # Check process status
            if process.poll() is not None:
                # Process has terminated
                config["status"] = "stopped"
                config["health"] = "unhealthy"
                del self.agent_processes[agent_name]
                return {"healthy": False, "error": "Agent process terminated"}
            
            # Process is running
            config["status"] = "running"
            config["health"] = "healthy"
            config["last_check"] = time.time()
            
            return {"healthy": True, "status": "running"}
            
        except Exception as e:
            logger.error(f"❌ Error checking health for {agent_name}: {e}")
            config["health"] = "unhealthy"
            return {"healthy": False, "error": str(e)}
    
    async def check_all_agents_health(self) -> Dict[str, Any]:
        """Check health of all agents"""
        logger.info("🏥 Checking health of all agents...")
        
        health_results = {}
        
        for agent_name in self.agents:
            health_status = await self.check_agent_health(agent_name)
            health_results[agent_name] = health_status
        
        # Calculate overall health
        healthy_agents = sum(1 for status in health_results.values() if status.get("healthy", False))
        total_agents = len(self.agents)
        
        overall_health = {
            "total_agents": total_agents,
            "healthy_agents": healthy_agents,
            "unhealthy_agents": total_agents - healthy_agents,
            "health_percentage": (healthy_agents / total_agents * 100) if total_agents > 0 else 0,
            "agents": health_results
        }
        
        logger.info(f"🏥 Health check complete: {healthy_agents}/{total_agents} agents healthy")
        return overall_health
    
    def _prepare_environment(self, env_vars: Dict[str, str]) -> Dict[str, str]:
        """Prepare environment variables for agent processes"""
        env = os.environ.copy()
        env.update(env_vars)
        env["PYTHONPATH"] = str(self.workspace_path)
        return env
    
    def _monitor_agent_output(self, process: subprocess.Popen, agent_name: str):
        """Monitor agent process output"""
        try:
            while process.poll() is None:
                # Read stdout
                if process.stdout:
                    line = process.stdout.readline()
                    if line:
                        logger.info(f"[{agent_name}] {line.strip()}")
                
                # Read stderr
                if process.stderr:
                    line = process.stderr.readline()
                    if line:
                        logger.error(f"[{agent_name}] ERROR: {line.strip()}")
                
                time.sleep(0.1)
            
            # Process has terminated
            logger.info(f"Agent {agent_name} process terminated with code {process.returncode}")
            
        except Exception as e:
            logger.error(f"Error monitoring agent {agent_name}: {e}")
    
    async def get_agent_logs(self, agent_name: str, lines: int = 50) -> Dict[str, Any]:
        if agent_name not in self.agent_processes:
            return {"success": False, "error": f"Agent {agent_name} not running"}
        
        try:
            # For now, return basic process info
            process = self.agent_processes[agent_name]
            
            return {
                "success": True,
                "agent": agent_name,
                "pid": process.pid,
                "status": "running" if process.poll() is None else "terminated",
                "return_code": process.returncode if process.poll() is not None else None
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting logs for {agent_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def start_health_monitoring(self):
        """Start continuous health monitoring"""
        logger.info("🏥 Starting continuous agent health monitoring...")
        
        while self.running:
            try:
                await self.check_all_agents_health()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"❌ Error in agent health monitoring: {e}")
                await asyncio.sleep(10)
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get summary of all agents status"""
        return {
            "total_agents": len(self.agents),
            "running_agents": len(self.agent_processes),
            "stopped_agents": len(self.agents) - len(self.agent_processes),
            "agents": self.agents
        }
    
    def shutdown(self):
        """Gracefully shutdown the agent manager"""
        logger.info("🛑 Shutting down agent manager...")
        
        # Stop all agents
        for agent_name in list(self.agent_processes.keys()):
            try:
                process = self.agent_processes[agent_name]
                process.terminate()
                process.wait(timeout=5)
            except:
                pass
        
        logger.info("✅ Agent manager shutdown complete")

async def main():
    agent_manager = AgentManager("/Users/Arief/Desktop/Nexus")
    
    
    
    # Wait a moment
    await asyncio.sleep(5)
    

if __name__ == "__main__":
    import os
    asyncio.run(main())

