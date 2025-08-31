#!/usr/bin/env python3
"""
Frenly MCP Bridge - Connects Frenly to MCP sub-agents

This module provides the bridge between Frenly's decisions and MCP sub-agent calls.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

# Fix imports to use correct class names
from .frenly_meta_agent import AppContext, AppCommand, AppResponse


@dataclass
class MCPCall:
    """Represents an MCP call to a sub-agent."""

    agent_name: str
    method: str
    parameters: Dict[str, Any]
    timeout: float = 30.0
    priority: int = 1


@dataclass
class MCPResponse:
    """Response from an MCP call."""

    success: bool
    data: Any
    error_message: Optional[str] = None
    processing_time: float = 0.0


class FrenlyMCPBridge:
    """Bridge between Frenly and sub-agents via MCP."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # MCP configuration
        self.default_timeout = config.get("default_timeout", 30.0)
        self.max_retries = config.get("max_retries", 3)
        self.retry_delay = config.get("retry_delay", 1.0)

        # Agent registry (populated during initialization)
        self.registered_agents: Dict[str, Any] = {}

        # Performance tracking
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0

    async def start(self):
        """Start the MCP bridge."""
        self.logger.info("Starting FrenlyMCPBridge...")

        # Initialize agent connections
        await self._initialize_agent_connections()

        self.logger.info("FrenlyMCPBridge started successfully")

    async def stop(self):
        """Stop the MCP bridge."""
        self.logger.info("Stopping FrenlyMCPBridge...")
        # Cleanup connections if needed
        self.logger.info("FrenlyMCPBridge stopped successfully")

    async def invoke_sub_agent(
        self,
        agent_name: str,
        method: str,
        parameters: Dict[str, Any],
        timeout: float = None,
    ) -> MCPResponse:
        """Invoke a single sub-agent via MCP."""

        start_time = asyncio.get_event_loop().time()
        self.total_calls += 1

        try:
            if agent_name not in self.registered_agents:
                return MCPResponse(
                    success=False,
                    data=None,
                    error_message=f"Agent '{agent_name}' not registered",
                )

            agent = self.registered_agents[agent_name]
            timeout = timeout or self.default_timeout

            # Execute the agent method
            if hasattr(agent, method):
                method_obj = getattr(agent, method)

                if asyncio.iscoroutinefunction(method_obj):
                    result = await asyncio.wait_for(
                        method_obj(**parameters), timeout=timeout
                    )
                else:
                    result = method_obj(**parameters)

                processing_time = asyncio.get_event_loop().time() - start_time
                self.successful_calls += 1

                return MCPResponse(
                    success=True, data=result, processing_time=processing_time
                )
            else:
                return MCPResponse(
                    success=False,
                    data=None,
                    error_message=f"Method '{method}' not found on agent '{agent_name}'",
                )

        except asyncio.TimeoutError:
            processing_time = asyncio.get_event_loop().time() - start_time
            self.failed_calls += 1

            return MCPResponse(
                success=False,
                data=None,
                error_message=f"Agent '{agent_name}' execution timed out after {timeout}s",
                processing_time=processing_time,
            )

        except Exception as e:
            processing_time = asyncio.get_event_loop().time() - start_time
            self.failed_calls += 1

            return MCPResponse(
                success=False,
                data=None,
                error_message=f"Error executing agent '{agent_name}': {str(e)}",
                processing_time=processing_time,
            )

    async def orchestrate_multiple_agents(
        self, agent_calls: List[MCPCall]
    ) -> Dict[str, MCPResponse]:
        """Orchestrate multiple agent calls in parallel."""

        tasks = []
        for call in agent_calls:
            task = self.invoke_sub_agent(
                call.agent_name, call.method, call.parameters, call.timeout
            )
            tasks.append((call.agent_name, task))

        # Execute all calls in parallel
        results = {}
        for agent_name, task in tasks:
            try:
                result = await task
                results[agent_name] = result
            except Exception as e:
                results[agent_name] = MCPResponse(
                    success=False,
                    data=None,
                    error_message=f"Task execution failed: {str(e)}",
                )

        return results

    async def execute_workflow(
        self, workflow: List[Dict[str, Any]]
    ) -> Dict[str, MCPResponse]:
        """Execute a workflow of agent calls with dependencies."""

        results = {}
        executed_agents = set()

        for step in workflow:
            agent_name = step["agent"]
            method = step["method"]
            parameters = step.get("parameters", {})
            dependencies = step.get("dependencies", [])

            # Check if dependencies are satisfied
            if not all(dep in executed_agents for dep in dependencies):
                results[agent_name] = MCPResponse(
                    success=False,
                    data=None,
                    error_message=f"Dependencies not satisfied: {dependencies}",
                )
                continue

            # Execute the agent
            result = await self.invoke_sub_agent(agent_name, method, parameters)
            results[agent_name] = result

            if result.success:
                executed_agents.add(agent_name)

        return results

    def register_agent(self, agent_name: str, agent_instance: Any):
        """Register a sub-agent with the MCP bridge."""

        self.registered_agents[agent_name] = agent_instance
        self.logger.info(f"Registered agent: {agent_name}")

    def unregister_agent(self, agent_name: str):
        """Unregister a sub-agent."""

        if agent_name in self.registered_agents:
            del self.registered_agents[agent_name]
            self.logger.info(f"Unregistered agent: {agent_name}")

    def get_registered_agents(self) -> List[str]:
        """Get list of registered agent names."""
        return list(self.registered_agents.keys())

    def get_agent_capabilities(self, agent_name: str) -> List[str]:
        """Get capabilities of a registered agent."""

        if agent_name not in self.registered_agents:
            return []

        agent = self.registered_agents[agent_name]
        capabilities = []

        # Check for common capability attributes
        if hasattr(agent, "capabilities"):
            capabilities.extend(agent.capabilities)

        if hasattr(agent, "get_capabilities"):
            try:
                agent_caps = agent.get_capabilities()
                if isinstance(agent_caps, list):
                    capabilities.extend(agent_caps)
            except:
                pass

        # Add methods as capabilities
        methods = [
            method
            for method in dir(agent)
            if callable(getattr(agent, method)) and not method.startswith("_")
        ]
        capabilities.extend(methods)

        return list(set(capabilities))  # Remove duplicates

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all registered agents."""

        health_status = {
            "bridge_status": "healthy",
            "registered_agents": len(self.registered_agents),
            "agent_health": {},
            "performance_metrics": {
                "total_calls": self.total_calls,
                "successful_calls": self.successful_calls,
                "failed_calls": self.failed_calls,
                "success_rate": self.successful_calls / max(1, self.total_calls),
            },
        }

        # Check individual agent health
        for agent_name, agent in self.registered_agents.items():
            try:
                if hasattr(agent, "health_check"):
                    if asyncio.iscoroutinefunction(agent.health_check):
                        health = await agent.health_check()
                    else:
                        health = agent.health_check()
                    health_status["agent_health"][agent_name] = health
                else:
                    health_status["agent_health"][agent_name] = {"status": "unknown"}
            except Exception as e:
                health_status["agent_health"][agent_name] = {
                    "status": "error",
                    "error": str(e),
                }

        return health_status

    async def _initialize_agent_connections(self):
        """Initialize connections to registered agents."""

        # This will be populated when the main service initializes agents
        self.logger.info(
            "Agent connections will be established during main service initialization"
        )

    def get_bridge_status(self) -> Dict[str, Any]:
        """Get current bridge status."""

        return {
            "status": "running",
            "registered_agents": len(self.registered_agents),
            "agent_names": list(self.registered_agents.keys()),
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "success_rate": self.successful_calls / max(1, self.total_calls),
        }
