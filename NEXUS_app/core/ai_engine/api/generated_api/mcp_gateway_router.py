from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any, Optional
import json
import asyncio
import os
import sys

# Add the parent directory to the Python path to allow imports of mcp.server
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

# Import MCP server components (assuming mcp is installed and accessible)
try:
    import mcp.server
    import mcp.server.stdio
    from mcp import Resource, Tool
except ImportError:
    # Fallback for environments where mcp is not directly installed in the API's venv
    # This might require a more robust solution in a production environment (e.g., separate service)
    print("WARNING: MCP library not found directly. MCP gateway functionality will be limited.")
    mcp = None

mcp_router = APIRouter(prefix="/mcp", tags=["MCP Gateway"])

# In a real scenario, these would communicate with the running MCP servers
# via their stdio interfaces or a more robust inter-process communication mechanism.

async def call_mcp_tool(server_script: str, tool_name: str, args: Dict[str, Any]) -> str:
    """
    In a real system, this would involve inter-process communication (e.g., sending
    a message to the running MCP server via its stdin and reading from its stdout).
    """
    # 1. Spawning a client process that connects to the MCP server's stdio or a socket.
    # 2. Sending MCP messages (e.g., ToolCallRequest).
    # 3. Parsing MCP responses (e.g., ToolCallResponse).
    
    # and communicate with them. For now, we'll just indicate a successful call.
    print(f"Simulating MCP tool call to {server_script}: {tool_name} with args {args}")
    
    # Attempt to dynamically import the MCP server script and call its function

async def read_mcp_resource(server_script: str, resource_uri: str) -> str:
    """
    Similar to call_mcp_tool, this would involve inter-process communication.
    """
    print(f"Simulating MCP resource read from {server_script}: {resource_uri}")
    try:
        if "agent_coordinator" in server_script:
            from NEXUS_app.core.agent_coordinator import coordinator as agent_coordinator_instance
            if resource_uri == "agent://agents":
                agents = agent_coordinator_instance.list_agents()
                return json.dumps([asdict(agent) for agent in agents], indent=2)
            elif resource_uri == "agent://sot":
                sot_content = agent_coordinator_instance.get_single_source_of_truth("file_organization")
                return sot_content if sot_content else "Single source of truth file not found."
            else:
                raise HTTPException(status_code=400, detail=f"Unknown agent coordinator resource: {resource_uri}")
        elif "process_monitor" in server_script:
            from NEXUS_app.core.process_monitor import monitor as process_monitor_instance
            if resource_uri == "process://processes":
                processes = process_monitor_instance.list_processes()
                return json.dumps([asdict(process) for process in processes], indent=2)
            elif resource_uri == "process://health":
                health = process_monitor_instance.get_system_health()
                return json.dumps(health, indent=2)
            else:
                raise HTTPException(status_code=400, detail=f"Unknown process monitor resource: {resource_uri}")
        else:
            raise HTTPException(status_code=400, detail=f"Unknown MCP server script: {server_script}")
    except ImportError as e:
        raise HTTPException(status_code=500, detail=f"MCP backend not directly available for resource read: {e}")
    except Exception as e:

# --- MCP Gateway API Endpoints ---

@mcp_router.get("/agents", summary="List all registered agents")
async def get_registered_agents():
    """
    Retrieves a list of all agents currently registered with the Agent Coordinator MCP server.
    """
    try:
        result = await read_mcp_resource("agent_coordinator.py", "agent://agents")
        return json.loads(result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve agents: {str(e)}")

@mcp_router.post("/agents/register", summary="Register a new agent or update an existing one")
async def register_agent(
    agent_id: str,
    name: str,
    agent_type: str,
    workspace_path: Optional[str] = None
):
    """
    Registers a new agent with the Agent Coordinator MCP server or updates an existing one.
    """
    try:
        args = {"agent_id": agent_id, "name": name, "agent_type": agent_type}
        if workspace_path:
            args["workspace_path"] = workspace_path
        result = await call_mcp_tool("agent_coordinator.py", "register_agent", args)
        return {"message": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to register agent: {str(e)}")

@mcp_router.post("/agents/{agent_id}/status", summary="Update an agent's status and current task")
async def update_agent_status(
    agent_id: str,
    status: str,
    task: Optional[str] = None,
    file_path: Optional[str] = None
):
    """
    Updates the status and current task of a registered agent on the Agent Coordinator MCP server.
    """
    try:
        args = {"agent_id": agent_id, "status": status}
        if task:
            args["task"] = task
        if file_path:
            args["file_path"] = file_path
        result = await call_mcp_tool("agent_coordinator.py", "update_agent_status", args)
        return {"message": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update agent status: {str(e)}")

@mcp_router.get("/processes", summary="List all monitored processes")
async def get_monitored_processes():
    """
    Retrieves a list of all processes currently monitored by the Process Monitor MCP server.
    """
    try:
        result = await read_mcp_resource("process_monitor.py", "process://processes")
        return json.loads(result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve processes: {str(e)}")

@mcp_router.post("/processes/scan", summary="Trigger a scan of running processes")
async def scan_running_processes():
    """
    Triggers the Process Monitor MCP server to rescan all running processes on the system.
    """
    try:
        result = await call_mcp_tool("process_monitor.py", "scan_processes", {})
        return {"message": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to scan processes: {str(e)}")

@mcp_router.get("/system-health", summary="Get overall system health metrics")
async def get_system_health():
    """
    Retrieves overall system health metrics from the Process Monitor MCP server,
    including process statistics and file organization compliance.
    """
    try:
        result = await read_mcp_resource("process_monitor.py", "process://health")
        return json.loads(result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve system health: {str(e)}")

@mcp_router.post("/files/validate", summary="Validate file organization structure")
async def validate_file_organization(file_path: str):
    """
    Validates if a given file path adheres to the unified file organization structure
    using the Process Monitor MCP server's validation tool.
    """
    try:
        args = {"file_path": file_path}
        result = await call_mcp_tool("process_monitor.py", "validate_file_organization", args)
        return json.loads(result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate file organization: {str(e)}")

@mcp_router.get("/sot/{file_type}", summary="Get content from Single Source of Truth files")
async def get_sot_content(file_type: str):
    """
    managed by the Agent Coordinator MCP server.
    
    Args:
        file_type (str): The type of SOT file (e.g., 'file_organization', 'structure_analysis', 'implementation_roadmap', 'master_todo').
    """
    valid_file_types = ["file_organization", "structure_analysis", "implementation_roadmap", "master_todo"]
    if file_type not in valid_file_types:
        raise HTTPException(status_code=400, detail=f"Invalid file_type. Must be one of: {', '.join(valid_file_types)}")

    try:
        args = {"file_type": file_type}
        result = await call_mcp_tool("agent_coordinator.py", "get_sot_content", args)
        if "not found" in result.lower():
            raise HTTPException(status_code=404, detail=f"SOT file '{file_type}' not found or content is empty.")
        return {"content": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve SOT content: {str(e)}")