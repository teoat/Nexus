#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
Frenly Meta Agent
Central coordination hub for all agents, ensuring they follow the single source of truth.
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentTask:
    """Information about an agent's current task"""
    agent_id: str
    task_description: str
    file_path: Optional[str] = None
    start_time: str = ""
    status: str = "in_progress"
    compliance_score: float = 0.0
    recommendations: List[str] = None
    
    def __post_init__(self):
        """
          Post Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        if self.recommendations is None:
            self.recommendations = []
        if not self.start_time:
            self.start_time = datetime.now().isoformat()

class FrenlyMetaAgent:
    """Central coordination hub for all agents"""
    
    def __init__(self, workspace_path: str):
        """
          Init  
        
        
        Args:
            workspace_path: Description of workspace_path
    
        Example:
            TBD: Add usage example
        """
        self.workspace_path = Path(workspace_path)
        self.agent_tasks: Dict[str, AgentTask] = {}
        self.meta_agent_file = self.workspace_path / ".mcp" / "frenly_meta_agent.json"
        self.logs_file = self.workspace_path / ".mcp" / "frenly_meta_agent.logs"
        
        # Ensure MCP directory exists
        self.meta_agent_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Single source of truth files
        self.sot_files = {
            "file_organization": "docs/UNIFIED_FILE_ORGANIZATION.md",
            "structure_analysis": "docs/FILE_STRUCTURE_ANALYSIS.md",
            "implementation_roadmap": "docs/IMPLEMENTATION_ROADMAP.md",
            "master_todo": "docs/master_todo.md"
        }
        
        # Load existing data
        self.load_data()
    
    def load_data(self):
        """Load existing agent data"""
        try:
            if self.meta_agent_file.exists():
                with open(self.meta_agent_file, 'r') as f:
                    data = json.load(f)
                    if 'agent_tasks' in data:
                        for task_id, task_data in data['agent_tasks'].items():
                            self.agent_tasks[task_id] = AgentTask(**task_data)
                logger.info(f"Loaded {len(self.agent_tasks)} agent tasks")
        except Exception as e:
            logger.error(f"Error loading meta agent data: {e}")
    
    def save_data(self):
        """Save agent data"""
        try:
            data = {
                'agent_tasks': {tid: asdict(task) for tid, task in self.agent_tasks.items()}
            }
            with open(self.meta_agent_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving meta agent data: {e}")
    
    def register_agent_task(self, agent_id: str, task_description: str, file_path: str = None) -> str:
        """Register a new agent task"""
        task_id = f"{agent_id}_{int(time.time())}"
        
        task = AgentTask(
            agent_id=agent_id,
            task_description=task_description,
            file_path=file_path
        )
        
        self.agent_tasks[task_id] = task
        self.save_data()
        
        logger.info(f"Registered task for agent {agent_id}: {task_description}")
        return task_id
    
    def get_agent_tasks(self, agent_id: str = None) -> List[AgentTask]:
        """
        Retrieve agent tasks
        
        
        Args:
            agent_id: Description of agent_id
    
        Returns:
            Unknown: Description of return value
    
        Example:
            TBD: Add usage example
        """
        if agent_id:
            return [task for task in self.agent_tasks.values() if task.agent_id == agent_id]
        return list(self.agent_tasks.values())
    
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
    
    def log_activity(self, level: str, message: str, metadata: Dict[str, Any] = None):
        """Log meta agent activity"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "metadata": metadata or {}
        }
        
        try:
            with open(self.logs_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.error(f"Error writing to log file: {e}")

# Global meta agent instance
meta_agent = FrenlyMetaAgent(os.getenv("FRENLY_WORKSPACE_PATH", "/Users/Arief/Desktop/Nexus"))

# MCP Server setup
server = mcp.server.Server("frenly-meta-agent")

@server.list_resources()
async def list_resources() -> List[Resource]:
    """List available resources"""
    return [
        Resource(
            uri="frenly://tasks",
            name="Agent Tasks",
            description="List of all agent tasks",
            mimeType="application/json"
        ),
        Resource(
            uri="frenly://sot",
            name="Single Source of Truth",
            description="Access to unified file organization documents",
            mimeType="text/markdown"
        )
    ]

@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read resource content"""
    if uri == "frenly://tasks":
        tasks = meta_agent.get_agent_tasks()
        return json.dumps([asdict(task) for task in tasks], indent=2)
    elif uri == "frenly://sot":
        sot_content = meta_agent.get_single_source_of_truth("file_organization")
        return sot_content or "Single source of truth file not found"
    else:
        raise ValueError(f"Unknown resource: {uri}")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="register_agent_task",
            description="Register a new task for an agent",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Agent identifier"},
                    "task_description": {"type": "string", "description": "Description of the task"},
                    "file_path": {"type": "string", "description": "File being worked on"}
                },
                "required": ["agent_id", "task_description"]
            }
        ),
        Tool(
            name="get_agent_tasks",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string", "description": "Agent identifier (optional)"}
                }
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
        if name == "register_agent_task":
            task_id = meta_agent.register_agent_task(
                arguments["agent_id"],
                arguments["task_description"],
                arguments.get("file_path")
            )
            return f"Task registered successfully with ID: {task_id}"
        
        elif name == "get_agent_tasks":
            tasks = meta_agent.get_agent_tasks(arguments.get("agent_id"))
            return f"Agent tasks:\n{json.dumps([asdict(task) for task in tasks], indent=2)}"
        
        elif name == "get_sot_content":
            content = meta_agent.get_single_source_of_truth(arguments["file_type"])
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
    logger.info("Starting Frenly Meta Agent MCP Server...")
    
    # Start the server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            NotificationOptions()
        )

if __name__ == "__main__":
    asyncio.run(main())
