#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
Agent Coordinator MCP Server
Manages inter-agent communication and ensures all agents follow the single source of truth.
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import mcp.server
import mcp.server.stdio
from mcp.server import NotificationOptions
from mcp import Resource, Tool

# Ensure log directory exists
log_dir = Path("data/logs")
log_dir.mkdir(parents=True, exist_ok=True)

# Configure logging to a shared file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename=log_dir / "mcp_combined.log",
    filemode='a'
)
logger = logging.getLogger(__name__)

@dataclass
class AgentInfo:
    """Information about a registered agent"""
    id: str
    name: str
    type: str
    status: str
    current_task: str
    current_file: Optional[str] = None
    workspace_path: str = ""
    last_seen: str = ""
    started_at: str = ""
    task_history: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.task_history is None:
            self.task_history = []
        if self.metadata is None:
            self.metadata = {}

class AgentCoordinator:
    """Manages agent coordination and communication"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.agents: Dict[str, AgentInfo] = {}
        self.agent_file = self.workspace_path / ".mcp" / "agents.json"
        self.tasks_file = self.workspace_path / ".mcp" / "tasks.json"
        
        # Ensure MCP directory exists
        self.agent_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing agents
        self.load_agents()
        
        # Single source of truth files
        self.sot_files = {
            "file_organization": "docs/UNIFIED_FILE_ORGANIZATION.md",
            "structure_analysis": "docs/FILE_STRUCTURE_ANALYSIS.md",
            "implementation_roadmap": "docs/IMPLEMENTATION_ROADMAP.md",
            "master_todo": "docs/master_todo.md"
        }
    
    def load_agents(self):
        """Load existing agents from file"""
        try:
            if self.agent_file.exists():
                with open(self.agent_file, 'r') as f:
                    data = json.load(f)
                    for agent_id, agent_data in data.items():
                        self.agents[agent_id] = AgentInfo(**agent_data)
                logger.info(f"Loaded {len(self.agents)} existing agents")
        except Exception as e:
            logger.error(f"Error loading agents: {e}")
    
    def save_agents(self):
        """Save agents to file"""
        try:
            with open(self.agent_file, 'w') as f:
                json.dump({aid: asdict(agent) for aid, agent in self.agents.items()}, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving agents: {e}")
    
    def register_agent(self, agent_id: str, name: str, agent_type: str, workspace_path: str = "") -> AgentInfo:
        """Register a new agent"""
        now = datetime.now().isoformat()
        
        if agent_id not in self.agents:
            agent = AgentInfo(
                id=agent_id,
                name=name,
                type=agent_type,
                status="running",
                current_task="Initializing",
                workspace_path=workspace_path or str(self.workspace_path),
                last_seen=now,
                started_at=now,
                task_history=[],
                metadata={}
            )
            self.agents[agent_id] = agent
            logger.info(f"Registered new agent: {agent_id} ({name})")
        else:
            # Update existing agent
            agent = self.agents[agent_id]
            agent.status = "running"
            agent.last_seen = now
            agent.workspace_path = workspace_path or str(self.workspace_path)
            logger.info(f"Updated existing agent: {agent_id}")
        
        self.save_agents()
        return agent
    
    def update_agent_status(self, agent_id: str, status: str, task: str = None, file_path: str = None):
        """Update agent status and current task"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.status = status
            agent.last_seen = datetime.now().isoformat()
            
            if task:
                agent.current_task = task
                if task not in agent.task_history:
                    agent.task_history.append(task)
                    # Keep only last 50 tasks
                    if len(agent.task_history) > 50:
                        agent.task_history = agent.task_history[-50:]
            
            if file_path:
                agent.current_file = file_path
            
            self.save_agents()
            logger.info(f"Updated agent {agent_id}: {status} - {task}")
    
    def get_agent_info(self, agent_id: str) -> Optional[AgentInfo]:
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[AgentInfo]:
        """List all registered agents"""
        return list(self.agents.values())
    
    def get_single_source_of_truth(self, file_type: str) -> Optional[str]:
        """Get content from single source of truth files"""
        if file_type in self.sot_files:
            file_path = self.workspace_path / self.sot_files[file_type]
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        return f.read()
                except Exception as e:
                    logger.error(f"Error reading SOT file {file_path}: {e}")
        return None
    
    def validate_file_structure(self, file_path: str) -> Dict[str, Any]:
        """Validate if a file follows the unified organization structure"""
        full_path = Path(file_path)
        relative_path = full_path.relative_to(self.workspace_path) if full_path.is_relative_to(self.workspace_path) else full_path
        
        # Check if file follows naming conventions
        valid_naming = all(part.islower() and (part.replace('_', '').isalnum() or part in ['-', '_']) 
                          for part in relative_path.parts)
        
        # Check if file is in appropriate directory
        valid_location = self._validate_file_location(relative_path)
        
        return {
            "file_path": str(relative_path),
            "valid_naming": valid_naming,
            "valid_location": valid_location,
            "recommendations": self._get_recommendations(relative_path, valid_naming, valid_location)
        }
    
    def _validate_file_location(self, relative_path: Path) -> bool:
        """Validate if file is in the correct directory according to unified organization"""
        # Define valid directory patterns based on UNIFIED_FILE_ORGANIZATION.md
        valid_patterns = [
            "NEXUS_app/core/ai_engine/",
            "NEXUS_app/core/business_services/",
            "NEXUS_app/interfaces/api/",
            "NEXUS_app/interfaces/frontend/",
            "nexus_docker/services/",
            "docs/",
            "monitoring/",
            "automation/"
        ]
        
        path_str = str(relative_path)
        return any(pattern in path_str for pattern in valid_patterns)
    
    def _get_recommendations(self, relative_path: Path, valid_naming: bool, valid_location: bool) -> List[str]:
        """Get recommendations for file organization improvements"""
        recommendations = []
        
        if not valid_naming:
            recommendations.append("File/directory names should use lowercase with underscores")
        
        if not valid_location:
            recommendations.append("File should be moved to appropriate directory according to unified organization")
        
        path_str = str(relative_path)
        if " " in path_str:
            recommendations.append("Remove spaces from file/directory names")
        
        if any(char in path_str for char in ['(', ')', '[', ']', '{', '}']):
        
        return recommendations
    
    def log_activity(self, agent_id: str, level: str, message: str, metadata: Dict[str, Any] = None):
        """Log agent activity using the centralized logger"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id,
            "level": level,
            "message": message,
            "metadata": metadata or {}
        }
        
        # Use the configured logger, which writes to mcp_combined.log
        if level == "info":
            logger.info(f"[AgentActivity] {json.dumps(log_entry)}")
        elif level == "warning":
            logger.warning(f"[AgentActivity] {json.dumps(log_entry)}")
        elif level == "error":
            logger.error(f"[AgentActivity] {json.dumps(log_entry)}")
        else:
            logger.debug(f"[AgentActivity] {json.dumps(log_entry)}")

# Global coordinator instance
coordinator = AgentCoordinator(os.getenv("AGENT_COORDINATOR_WORKSPACE_PATH", "/Users/Arief/Desktop/Nexus"))

# MCP Server setup
server = mcp.server.Server("agent-coordinator")

@server.list_resources()
async def list_resources() -> List[Resource]:
    """List available resources"""
    return [
        Resource(
            uri="agent://agents",
            name="Registered Agents",
            description="List of all registered agents",
            mimeType="application/json"
        ),
        Resource(
            uri="agent://sot",
            name="Single Source of Truth",
            description="Access to unified file organization documents",
            mimeType="text/markdown"
        )
    ]

@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read resource content"""
    if uri == "agent://agents":
        agents = coordinator.list_agents()
        return json.dumps([asdict(agent) for agent in agents], indent=2)
    elif uri == "agent://sot":
        sot_content = coordinator.get_single_source_of_truth("file_organization")
        return sot_content or "Single source of truth file not found"
    else:
        raise ValueError(f"Unknown resource: {uri}")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="register_agent",
            description="Register a new agent or update existing agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Unique agent identifier"},
                    "name": {"type": "string", "description": "Agent display name"},
                    "agent_type": {"type": "string", "description": "Type of agent (e.g., 'cursor', 'claude', 'gemini')"},
                    "workspace_path": {"type": "string", "description": "Agent's workspace path"}
                },
                "required": ["agent_id", "name", "agent_type"]
            }
        ),
        Tool(
            name="update_agent_status",
            description="Update agent status and current task",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Agent identifier"},
                    "status": {"type": "string", "description": "New status"},
                    "task": {"type": "string", "description": "Current task description"},
                    "file_path": {"type": "string", "description": "Current file being worked on"}
                },
                "required": ["agent_id", "status"]
            }
        ),
        Tool(
            name="list_agents",
            description="List all registered agents",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="get_agent_info",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Agent identifier"}
                },
                "required": ["agent_id"]
            }
        ),
        Tool(
            name="validate_file_structure",
            description="Validate if a file follows the unified organization structure",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Path to file to validate"}
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="get_sot_content",
            description="Get content from single source of truth files",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_type": {"type": "string", "description": "Type of SOT file (file_organization, structure_analysis, implementation_roadmap, master_todo)"}
                },
                "required": ["file_type"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> str:
    """Execute tool calls"""
    try:
        if name == "register_agent":
            agent = coordinator.register_agent(
                arguments["agent_id"],
                arguments["name"],
                arguments["agent_type"],
                arguments.get("workspace_path", "")
            )
            coordinator.log_activity(agent.id, "info", f"Agent registered: {agent.name}")
            return f"Agent {agent.name} registered successfully"
        
        elif name == "update_agent_status":
            coordinator.update_agent_status(
                arguments["agent_id"],
                arguments["status"],
                arguments.get("task"),
                arguments.get("file_path")
            )
            coordinator.log_activity(arguments["agent_id"], "info", f"Status updated: {arguments['status']}")
            return "Agent status updated successfully"
        
        elif name == "list_agents":
            agents = coordinator.list_agents()
            return f"Registered agents:\n{json.dumps([asdict(agent) for agent in agents], indent=2)}"
        
        elif name == "get_agent_info":
            agent = coordinator.get_agent_info(arguments["agent_id"])
            if agent:
                return f"Agent info:\n{json.dumps(asdict(agent), indent=2)}"
            else:
                return "Agent not found"
        
        elif name == "validate_file_structure":
            result = coordinator.validate_file_structure(arguments["file_path"])
            return f"File structure validation:\n{json.dumps(result, indent=2)}"
        
        elif name == "get_sot_content":
            content = coordinator.get_single_source_of_truth(arguments["file_type"])
            if content:
                return content
            else:
                return "Single source of truth file not found"
        
        else:
            return f"Unknown tool: {name}"
    
    except Exception as e:
        logger.error(f"Error in tool call {name}: {e}")
        return f"Error: {str(e)}"

async def main():
    """Main function to run the MCP server"""
    logger.info("Starting Agent Coordinator MCP Server...")
    
    # Register this server as an agent
    coordinator.register_agent(
        "agent-coordinator",
        "Agent Coordinator",
        "mcp-server",
        str(coordinator.workspace_path)
    )
    
    # Start the server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            NotificationOptions()
        )

if __name__ == "__main__":
    asyncio.run(main())
