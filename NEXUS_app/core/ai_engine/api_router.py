#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🌐 Frenly AI API Router
FastAPI router for Frenly AI service endpoints
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import json

from agent_manager import agent_manager, AgentType
from .config import get_config

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1", tags=["frenly-ai"])

# Request/Response Models
class FrenlyAIRequest(BaseModel):
    """Request model for Frenly AI service"""
    message: str = Field(..., description="User message or query", min_length=1, max_length=10000)
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    agent_type: Optional[str] = Field("general", description="Type of agent to handle request")
    priority: int = Field(1, description="Request priority (1-10)", ge=1, le=10)
    session_id: Optional[str] = Field(None, description="Session identifier")
    timeout: Optional[int] = Field(30, description="Request timeout in seconds", ge=1, le=300)

class FrenlyAIResponse(BaseModel):
    """Response model for Frenly AI service"""
    response: str = Field(..., description="AI generated response")
    confidence: float = Field(..., description="Confidence score (0-1)", ge=0, le=1)
    agent_used: str = Field(..., description="Agent that processed the request")
    agent_type: str = Field(..., description="Type of agent used")
    processing_time: float = Field(..., description="Processing time in seconds")
    timestamp: str = Field(..., description="Response timestamp")
    session_id: Optional[str] = Field(None, description="Session identifier")
    request_id: str = Field(..., description="Unique request identifier")

class AgentStatusResponse(BaseModel):
    """Agent status response model"""
    id: str
    name: str
    type: str
    status: str
    capabilities: List[str]
    metrics: Dict[str, Any]
    created_at: str
    last_active: str

class HealthCheckResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: str
    version: str
    uptime: float
    active_agents: int
    total_requests: int
    database_connected: bool
    redis_connected: bool

class MetricsResponse(BaseModel):
    """Metrics response model"""
    timestamp: str
    total_agents: int
    active_agents: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    error_rate: float
    agent_metrics: Dict[str, Any]

# Dependency functions
async def get_agent_manager():
    """Get agent manager instance"""
    return agent_manager

async def validate_agent_type(agent_type: str) -> str:
    """Validate agent type"""
    valid_types = [agent_type.value for agent_type in AgentType]
    if agent_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid agent type. Must be one of: {', '.join(valid_types)}"
        )
    return agent_type

# API Endpoints

@router.post("/process", response_model=FrenlyAIResponse)
async def process_request(
    request: FrenlyAIRequest,
    background_tasks: BackgroundTasks,
    agent_mgr: agent_manager = Depends(get_agent_manager)
):
    """Process AI request with appropriate agent"""
    try:
        # Validate agent type
        agent_type = await validate_agent_type(request.agent_type)
        
        # Generate request ID
        request_id = f"req_{int(time.time() * 1000)}"
        
        # Prepare request data
        request_data = {
            "message": request.message,
            "context": request.context or {},
            "priority": request.priority,
            "session_id": request.session_id,
            "request_id": request_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Submit request to agent manager
        response = await agent_mgr.submit_request(agent_type, request_data)
        
        # Create response
        frenly_response = FrenlyAIResponse(
            response=response["response"],
            confidence=response["confidence"],
            agent_used=response["agent_id"],
            agent_type=response["agent_type"],
            processing_time=response["processing_time"],
            timestamp=response["timestamp"],
            session_id=request.session_id,
            request_id=request_id
        )
        
        # Log request in background
        background_tasks.add_task(log_request, request_data, frenly_response)
        
        return frenly_response
        
    except Exception as e:
        logger.error(f"❌ Error processing request: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

@router.get("/agents", response_model=List[AgentStatusResponse])
async def get_agents(agent_mgr: agent_manager = Depends(get_agent_manager)):
    """Get all agents status"""
    try:
        agents_data = await agent_mgr.get_agent_status()
        
        return [
            AgentStatusResponse(
                id=agent["id"],
                name=agent["name"],
                type=agent["type"],
                status=agent["status"],
                capabilities=agent["capabilities"],
                metrics=agent["metrics"],
                created_at=agent["created_at"],
                last_active=agent["last_active"]
            )
            for agent in agents_data
        ]
        
    except Exception as e:
        logger.error(f"❌ Error getting agents: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting agents: {str(e)}")

@router.get("/agents/{agent_id}", response_model=AgentStatusResponse)
async def get_agent(
    agent_id: str,
    agent_mgr: agent_manager = Depends(get_agent_manager)
):
    try:
        agent_data = await agent_mgr.get_agent_status(agent_id)
        
        return AgentStatusResponse(
            id=agent_data["id"],
            name=agent_data["name"],
            type=agent_data["type"],
            status=agent_data["status"],
            capabilities=agent_data["capabilities"],
            metrics=agent_data["metrics"],
            created_at=agent_data["created_at"],
            last_active=agent_data["last_active"]
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting agent {agent_id}: {e}")
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")

@router.get("/health", response_model=HealthCheckResponse)
async def health_check(agent_mgr: agent_manager = Depends(get_agent_manager)):
    """Health check endpoint"""
    try:
        # Get agent status
        agents_data = await agent_mgr.get_agent_status()
        active_agents = len([agent for agent in agents_data if agent["status"] == "idle" or agent["status"] == "busy"])
        
        # Calculate total requests
        total_requests = sum(agent["metrics"]["total_requests"] for agent in agents_data)
        
        # Check database and Redis connections
        config = get_config()
        database_connected = True  # Simplified for now
        redis_connected = True     # Simplified for now
        
        return HealthCheckResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            version=config.version,
            uptime=time.time(),  # Simplified uptime calculation
            active_agents=active_agents,
            total_requests=total_requests,
            database_connected=database_connected,
            redis_connected=redis_connected
        )
        
    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        return HealthCheckResponse(
            status="unhealthy",
            timestamp=datetime.now().isoformat(),
            version="unknown",
            uptime=0,
            active_agents=0,
            total_requests=0,
            database_connected=False,
            redis_connected=False
        )

@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics(agent_mgr: agent_manager = Depends(get_agent_manager)):
    """Get performance metrics"""
    try:
        agents_data = await agent_mgr.get_agent_status()
        
        total_agents = len(agents_data)
        active_agents = len([agent for agent in agents_data if agent["status"] in ["idle", "busy"]])
        
        total_requests = sum(agent["metrics"]["total_requests"] for agent in agents_data)
        successful_requests = sum(agent["metrics"]["successful_requests"] for agent in agents_data)
        failed_requests = sum(agent["metrics"]["failed_requests"] for agent in agents_data)
        
        avg_response_times = [agent["metrics"]["avg_response_time"] for agent in agents_data if agent["metrics"]["avg_response_time"] > 0]
        avg_response_time = sum(avg_response_times) / len(avg_response_times) if avg_response_times else 0.0
        
        error_rate = failed_requests / total_requests if total_requests > 0 else 0.0
        
        # Prepare agent metrics
        agent_metrics = {
            agent["id"]: {
                "type": agent["type"],
                "status": agent["status"],
                "metrics": agent["metrics"]
            }
            for agent in agents_data
        }
        
        return MetricsResponse(
            timestamp=datetime.now().isoformat(),
            total_agents=total_agents,
            active_agents=active_agents,
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=avg_response_time,
            error_rate=error_rate,
            agent_metrics=agent_metrics
        )
        
    except Exception as e:
        logger.error(f"❌ Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting metrics: {str(e)}")

@router.get("/capabilities")
async def get_capabilities():
    """Get available capabilities by agent type"""
    try:
        capabilities = {
            agent_type.value: {
                "name": agent_manager.agent_types[agent_type]["name"],
                "capabilities": [
                    {
                        "name": cap.name,
                        "description": cap.description,
                        "enabled": cap.enabled
                    }
                    for cap in agent_manager.agent_types[agent_type]["capabilities"]
                ]
            }
            for agent_type in AgentType
        }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "capabilities": capabilities
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting capabilities: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting capabilities: {str(e)}")

@router.post("/agents/{agent_id}/restart")
async def restart_agent(
    agent_id: str,
    agent_mgr: agent_manager = Depends(get_agent_manager)
):
    try:
        # Check if agent exists
        agent_data = await agent_mgr.get_agent_status(agent_id)
        
        # Restart agent (simplified implementation)
        logger.info(f"🔄 Restarting agent: {agent_id}")
        
        return {
            "message": f"Agent {agent_id} restart initiated",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error restarting agent {agent_id}: {e}")
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")

@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get session information"""
    try:
        # This would typically retrieve session data from Redis or database
        return {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "message_count": 0,  # Would be retrieved from actual session data
            "status": "active"
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting session {session_id}: {e}")
        raise HTTPException(status_code=404, detail=f"Session not found: {session_id}")

# Background task functions
async def log_request(request_data: Dict[str, Any], response: FrenlyAIResponse):
    """Log request and response in background"""
    try:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "request": request_data,
            "response": {
                "response": response.response,
                "confidence": response.confidence,
                "agent_used": response.agent_used,
                "processing_time": response.processing_time
            }
        }
        
        # In a real implementation, this would be stored in a database or log file
        logger.info(f"📝 Request logged: {response.request_id}")
        
    except Exception as e:
        logger.error(f"❌ Error logging request: {e}")

# Error handlers
@router.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat()
        }
    )

@router.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"❌ Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "timestamp": datetime.now().isoformat()
        }
    )
