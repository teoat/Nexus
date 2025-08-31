#!/usr/bin/env python3
"""
Frenly API - FastAPI endpoints for Frenly Meta Agent

This module provides REST API endpoints for interacting with Frenly,
the central app manager and AI secretary.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging
import time

# Fix imports to use absolute paths
from agents.frenly_meta_agent import (
    FrenlyMetaAgent,
    AppContext,
    AppCommand,
    AppResponse,
)
from agents.frenly_mcp_bridge import FrenlyMCPBridge

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/frenly", tags=["frenly"])

# Global instances (would be injected in production)
frenly_agent: Optional[FrenlyMetaAgent] = None
mcp_bridge: Optional[FrenlyMCPBridge] = None


# Pydantic models for API requests/responses
class FrenlyQueryRequest(BaseModel):
    query: str = Field(..., description="User query to process")
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional context"
    )


class FrenlyQueryResponse(BaseModel):
    success: bool = Field(..., description="Whether the query was successful")
    response: Optional[AppResponse] = Field(None, description="Frenly's response")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    processing_time: float = Field(..., description="Total processing time in seconds")


class FrenlyStatusResponse(BaseModel):
    status: str = Field(..., description="Frenly's current status")
    app_mode: str = Field(..., description="Current application mode")
    ai_mode: str = Field(..., description="Current AI processing mode")
    current_view: str = Field(..., description="Current dashboard view")
    user_role: str = Field(..., description="Current user role")
    mode_intersection: Optional[Dict[str, Any]] = Field(
        None, description="Current mode intersection details"
    )


class FrenlyContextRequest(BaseModel):
    app_mode: Optional[str] = Field(None, description="Application mode to set")
    ai_mode: Optional[str] = Field(None, description="AI processing mode to set")
    user_role: Optional[str] = Field(None, description="User role to set")
    view: Optional[str] = Field(None, description="Dashboard view to set")


class FrenlyContextResponse(BaseModel):
    success: bool = Field(..., description="Whether the context update was successful")
    message: str = Field(..., description="Response message")
    updated_context: Dict[str, Any] = Field(
        ..., description="Updated context information"
    )


class FrenlyWorkflowRequest(BaseModel):
    workflow: Dict[str, Any] = Field(..., description="Workflow definition to execute")
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Workflow context"
    )


class FrenlyWorkflowResponse(BaseModel):
    success: bool = Field(
        ..., description="Whether the workflow execution was successful"
    )
    message: str = Field(..., description="Response message")
    workflow_results: Optional[Dict[str, Any]] = Field(
        None, description="Workflow execution results"
    )


class FrenlyModeSwitchRequest(BaseModel):
    mode_type: str = Field(
        ..., description="Type of mode to switch: 'app_mode' or 'ai_mode'"
    )
    new_mode: str = Field(..., description="New mode value to set")


class FrenlyModeSwitchResponse(BaseModel):
    success: bool = Field(..., description="Whether the mode switch was successful")
    message: str = Field(..., description="Response message")
    old_mode: str = Field(..., description="Previous mode value")
    new_mode: str = Field(..., description="New mode value")
    mode_intersection: Optional[Dict[str, Any]] = Field(
        None, description="Updated mode intersection details"
    )


# Dependency functions
def get_frenly_agent() -> FrenlyMetaAgent:
    if frenly_agent is None:
        raise HTTPException(status_code=503, detail="Frenly agent not initialized")
    return frenly_agent


def get_mcp_bridge() -> FrenlyMCPBridge:
    if mcp_bridge is None:
        raise HTTPException(status_code=503, detail="MCP bridge not initialized")
    return mcp_bridge


# API endpoints
@router.post("/query", response_model=FrenlyQueryResponse)
async def process_query(request: FrenlyQueryRequest):
    """Process a user query through Frenly."""
    start_time = time.time()

    try:
        agent = get_frenly_agent()

        # Create command for user query
        command = AppCommand(
            command_type="user_query",
            parameters={"query": request.query, "context": request.context or {}},
        )

        # Process through Frenly
        response = await agent.manage_app(command)

        processing_time = time.time() - start_time

        return FrenlyQueryResponse(
            success=response.success, response=response, processing_time=processing_time
        )

    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Query processing error: {e}")

        return FrenlyQueryResponse(
            success=False, error_message=str(e), processing_time=processing_time
        )


@router.get("/status", response_model=FrenlyStatusResponse)
async def get_frenly_status():
    """Get Frenly's current status and context."""
    try:
        agent = get_frenly_agent()
        status = agent.get_app_status()

        # Get current mode intersection if available
        mode_intersection = None
        if agent.app_context.current_intersection:
            mode_intersection = {
                "description": agent.app_context.current_intersection.description,
                "features": agent.app_context.current_intersection.features,
                "limitations": agent.app_context.current_intersection.limitations,
                "recommended_views": [
                    view.value
                    for view in agent.app_context.current_intersection.recommended_views
                ],
                "agent_priorities": agent.app_context.current_intersection.agent_priorities,
            }

        return FrenlyStatusResponse(
            status=status["frenly_status"],
            app_mode=status["app_mode"],
            ai_mode=status["ai_mode"],
            current_view=status["current_view"],
            user_role=status["user_role"],
            mode_intersection=mode_intersection,
        )

    except Exception as e:
        logger.error(f"Status retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/context", response_model=FrenlyContextResponse)
async def update_context(request: FrenlyContextRequest):
    """Update Frenly's context (app mode, AI mode, user role, view)."""
    try:
        agent = get_frenly_agent()
        actions_taken = []

        # Update app mode if provided
        if request.app_mode:
            command = AppCommand(
                command_type="switch_mode", parameters={"mode": request.app_mode}
            )
            response = await agent.manage_app(command)
            if response.success:
                actions_taken.append(f"Switched app mode to {request.app_mode}")

        # Update AI mode if provided
        if request.ai_mode:
            command = AppCommand(
                command_type="change_ai_mode", parameters={"ai_mode": request.ai_mode}
            )
            response = await agent.manage_app(command)
            if response.success:
                actions_taken.append(f"Switched AI mode to {request.ai_mode}")

        # Update view if provided
        if request.view:
            command = AppCommand(
                command_type="change_view", parameters={"view": request.view}
            )
            response = await agent.manage_app(command)
            if response.success:
                actions_taken.append(f"Switched view to {request.view}")

        # Get updated context
        status = agent.get_app_status()

        return FrenlyContextResponse(
            success=True,
            message=f"Context updated successfully. Actions: {', '.join(actions_taken)}",
            updated_context={
                "app_mode": status["app_mode"],
                "ai_mode": status["ai_mode"],
                "current_view": status["current_view"],
                "user_role": status["user_role"],
            },
        )

    except Exception as e:
        logger.error(f"Context update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/switch-mode", response_model=FrenlyModeSwitchResponse)
async def switch_mode(request: FrenlyModeSwitchRequest):
    """Switch between different modes (app mode or AI mode)."""
    try:
        agent = get_frenly_agent()

        if request.mode_type == "app_mode":
            command = AppCommand(
                command_type="switch_mode", parameters={"mode": request.new_mode}
            )
            old_mode = agent.app_context.app_mode.value
        elif request.mode_type == "ai_mode":
            command = AppCommand(
                command_type="change_ai_mode", parameters={"ai_mode": request.new_mode}
            )
            old_mode = agent.app_context.ai_mode.value
        else:
            raise HTTPException(
                status_code=400, detail="Invalid mode_type. Use 'app_mode' or 'ai_mode'"
            )

        # Execute mode switch
        response = await agent.manage_app(command)

        if not response.success:
            raise HTTPException(status_code=400, detail=response.message)

        # Get updated mode intersection
        mode_intersection = None
        if agent.app_context.current_intersection:
            mode_intersection = {
                "description": agent.app_context.current_intersection.description,
                "features": agent.app_context.current_intersection.features,
                "limitations": agent.app_context.current_intersection.limitations,
                "recommended_views": [
                    view.value
                    for view in agent.app_context.current_intersection.recommended_views
                ],
                "agent_priorities": agent.app_context.current_intersection.agent_priorities,
            }

        return FrenlyModeSwitchResponse(
            success=True,
            message=response.message,
            old_mode=old_mode,
            new_mode=request.new_mode,
            mode_intersection=mode_intersection,
        )

    except Exception as e:
        logger.error(f"Mode switch error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mode-intersection")
async def get_mode_intersection():
    """Get information about the current mode intersection."""
    try:
        agent = get_frenly_agent()

        command = AppCommand(command_type="get_mode_intersection", parameters={})

        response = await agent.manage_app(command)

        if not response.success:
            raise HTTPException(status_code=400, detail=response.message)

        return response.data["intersection"]

    except Exception as e:
        logger.error(f"Mode intersection retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflow", response_model=FrenlyWorkflowResponse)
async def execute_workflow(request: FrenlyWorkflowRequest):
    """Execute a workflow through Frenly."""
    start_time = time.time()

    try:
        agent = get_frenly_agent()

        command = AppCommand(
            command_type="workflow_execution",
            parameters={"workflow": request.workflow, "context": request.context or {}},
        )

        response = await agent.manage_app(command)

        return FrenlyWorkflowResponse(
            success=response.success,
            message=response.message,
            workflow_results=(
                response.data.get("workflow_results") if response.success else None
            ),
        )

    except Exception as e:
        logger.error(f"Workflow execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def get_available_agents():
    """Get list of available AI agents and their capabilities."""
    try:
        bridge = get_mcp_bridge()
        agents = bridge.get_registered_agents()
        capabilities = bridge.get_agent_capabilities()

        return {"agents": agents, "capabilities": capabilities}

    except Exception as e:
        logger.error(f"Agent retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def get_frenly_router() -> APIRouter:
    """Get the Frenly API router."""
    return router
