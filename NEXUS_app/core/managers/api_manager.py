"""
api_manager Module

Api Manager

This module provides functionality for api manager.

Classes:
    TBD: Add class descriptions

Functions:
    TBD: Add function descriptions

Example:
    TBD: Add usage example

Author: NEXUS Platform
Created: 2025-09-11
Version: 1.0.0
"""

import logging
import httpx # Import httpx for making async HTTP requests
import asyncio # Import asyncio for running async operations
from pathlib import Path # Import Path

logger = logging.getLogger(__name__)

class APIManager:
    """
    APIManager Class
    
    Apimanager
    
    Attributes:
        TBD: Add attribute descriptions
    
    Methods:
        TBD: Add method descriptions
    
    Example:
        TBD: Add usage example
    """
    def __init__(self, workspace_path):
        """
          Init  
        
        
        Args:
            workspace_path: Description of workspace_path
    
        Example:
            TBD: Add usage example
        """
        logger.info("Initializing API Manager...")
        self.workspace_path = Path(workspace_path) # Convert to Path object
        self.apis = self._discover_apis()
        logger.info(f"Discovered {len(self.apis)} APIs.")
        
        logger.info("API Manager initialized.")

    async def register_mcp_agent(self):
        """Public method to register this API Manager as an agent with the MCP Gateway API."""
        await self._register_as_mcp_agent()

    def _discover_apis(self):
        """Dynamically discovers API files in the NEXUS_app/api directory."""
        apis = {}
        api_path = self.workspace_path / "NEXUS_app" / "api"
        if not api_path.exists():
            logger.warning(f"API path not found: {api_path}")
            return apis

        for file_path in api_path.glob("**/*.py"):
            if file_path.name not in ["__init__.py"]:
                api_name = file_path.stem
                apis[api_name] = {"path": file_path, "status": "discovered"}
        return apis

    def get_status_summary(self):
        """Returns a summary of discovered APIs and their status."""
        if not self.apis:
            return {"status": "no_apis_found"}

        api_statuses = {name: data["status"] for name, data in self.apis.items()}
        return {
            "status": "operational",
            "api_count": len(self.apis),
            "apis": api_statuses,
        }

    async def _register_as_mcp_agent(self):
        """Internal method to handle the actual registration with the MCP Gateway API."""
        mcp_gateway_url = "http://localhost:8000/api/v1/mcp/agents/register" # Assuming API runs on 8000
        agent_id = "api-manager"
        agent_name = "API Manager"
        agent_type = "api-service"
        
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
                logger.info(f"Successfully registered API Manager as MCP agent: {response.json()}")
        except httpx.RequestError as exc:
            logger.error(f"Error registering API Manager as MCP agent: {exc}")
        except httpx.HTTPStatusError as exc:
            logger.error(f"HTTP error registering API Manager as MCP agent: {exc.response.status_code} - {exc.response.text}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during MCP agent registration: {e}")
