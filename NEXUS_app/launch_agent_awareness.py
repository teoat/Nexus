#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
Agent Awareness Launcher
Launches all MCP servers for agent coordination and process monitoring.
"""

import asyncio
import logging
import os
import signal
import sys
import time
from pathlib import Path
from typing import List, Dict, Any
import subprocess
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AgentAwarenessLauncher:
    """Launches and manages all agent awareness MCP servers"""
    
    def __init__(self, workspace_path: str):
        """
          Init  
        
        
        Args:
            workspace_path: Description of workspace_path
    
        Example:
            TBD: Add usage example
        """
        self.workspace_path = Path(workspace_path)
        self.processes: List[subprocess.Popen] = []
        self.running = True
        
        # MCP server configurations
        self.mcp_servers = {
            "agent-coordinator": {
                "script": "core/agent_coordinator.py",
                "env": {
                    "AGENT_COORDINATOR_WORKSPACE_PATH": str(self.workspace_path),
                    "AGENT_COORDINATOR_ENABLED": "true",
                    "AGENT_COORDINATOR_INTER_AGENT_COMMUNICATION": "true"
                }
            },
            "process-monitor": {
                "script": "core/process_monitor.py",
                "env": {
                    "PROCESS_MONITOR_WORKSPACE_PATH": str(self.workspace_path),
                    "PROCESS_MONITORING_ENABLED": "true"
                }
            },
            "frenly-meta-agent": {
                "script": "core/frenly_meta_agent.py",
                "env": {
                    "FRENLY_WORKSPACE_PATH": str(self.workspace_path),
                    "FRENLY_AGENT_COORDINATION_ENABLED": "true",
                    "FRENLY_INTER_AGENT_COMMUNICATION": "true"
                }
            }
        }
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        self.shutdown()
    
    def launch_server(self, server_name: str, config: Dict[str, Any]) -> subprocess.Popen:
        """Launch a single MCP server"""
        script_path = self.workspace_path / config["script"]
        
        if not script_path.exists():
            logger.error(f"Server script not found: {script_path}")
            return None
        
        # Prepare environment
        env = os.environ.copy()
        env.update(config["env"])
        env["PYTHONPATH"] = str(self.workspace_path)
        
        # Launch server
        try:
            logger.info(f"Launching {server_name}...")
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                env=env,
                cwd=str(self.workspace_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Start output monitoring in separate threads
            threading.Thread(
                target=self._monitor_output,
                args=(process, server_name, "stdout"),
                daemon=True
            ).start()
            
            threading.Thread(
                target=self._monitor_output,
                args=(process, server_name, "stderr"),
                daemon=True
            ).start()
            
            logger.info(f"✅ {server_name} launched with PID {process.pid}")
            return process
            
        except Exception as e:
            logger.error(f"Failed to launch {server_name}: {e}")
            return None
    
    def _monitor_output(self, process: subprocess.Popen, server_name: str, output_type: str):
        """Monitor server output"""
        stream = process.stdout if output_type == "stdout" else process.stderr
        
        while self.running and process.poll() is None:
            try:
                line = stream.readline()
                if line:
                    logger.info(f"[{server_name}] {line.strip()}")
            except Exception as e:
                logger.error(f"Error monitoring {server_name} {output_type}: {e}")
                break
    
    def launch_all_servers(self):
        """Launch all MCP servers"""
        logger.info("🚀 Launching Agent Awareness System...")
        
        for server_name, config in self.mcp_servers.items():
            process = self.launch_server(server_name, config)
            if process:
                self.processes.append(process)
                time.sleep(1)  # Small delay between launches
        
        logger.info(f"✅ Launched {len(self.processes)} MCP servers")
    
    def check_server_health(self) -> Dict[str, bool]:
        """Check health of all running servers"""
        health_status = {}
        
        for i, process in enumerate(self.processes):
            server_name = list(self.mcp_servers.keys())[i]
            
            if process.poll() is None:
                health_status[server_name] = True
                logger.info(f"✅ {server_name} is running (PID: {process.pid})")
            else:
                health_status[server_name] = False
                logger.error(f"❌ {server_name} has stopped (Exit code: {process.returncode})")
        
        return health_status
    
    def restart_failed_servers(self):
        """Restart any servers that have failed"""
        health_status = self.check_server_health()
        
        for server_name, is_healthy in health_status.items():
            if not is_healthy:
                logger.warning(f"🔄 Restarting failed server: {server_name}")
                
                # Find and remove the failed process
                for i, process in enumerate(self.processes):
                    if list(self.mcp_servers.keys())[i] == server_name:
                        self.processes.pop(i)
                        break
                
                # Relaunch the server
                config = self.mcp_servers[server_name]
                process = self.launch_server(server_name, config)
                if process:
                    self.processes.append(process)
                    time.sleep(1)
    
    def run(self):
        """Main run loop"""
        try:
            # Launch all servers
            self.launch_all_servers()
            
            # Main monitoring loop
            while self.running:
                time.sleep(10)  # Check every 10 seconds
                
                # Check server health
                health_status = self.check_server_health()
                
                # Restart failed servers
                if not all(health_status.values()):
                    self.restart_failed_servers()
                
                # Log status
                healthy_count = sum(health_status.values())
                total_count = len(health_status)
                logger.info(f"📊 Server Health: {healthy_count}/{total_count} healthy")
                
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Shutdown all servers gracefully"""
        logger.info("🛑 Shutting down Agent Awareness System...")
        
        for process in self.processes:
            try:
                logger.info(f"Terminating process {process.pid}")
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning(f"Force killing process {process.pid}")
                    process.kill()
                    
            except Exception as e:
                logger.error(f"Error terminating process {process.pid}: {e}")
        
        logger.info("✅ Agent Awareness System shutdown complete")

def main():
    """Main entry point"""
    # Get workspace path from environment or use current directory
    workspace_path = os.getenv("AGENT_COORDINATOR_WORKSPACE_PATH", "/Users/Arief/Desktop/Nexus")
    
    # Create and run launcher
    launcher = AgentAwarenessLauncher(workspace_path)
    launcher.run()

if __name__ == "__main__":
    main()
