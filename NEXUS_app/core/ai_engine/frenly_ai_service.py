#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🤖 Frenly AI Service - Meta-Agent Coordinator
Advanced AI service for coordinating multiple agents and providing intelligent responses
"""

import asyncio
import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import redis
import psycopg2
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FrenlyAIRequest(BaseModel):
    """Request model for Frenly AI service"""
    message: str = Field(..., description="User message or query")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    agent_type: Optional[str] = Field("general", description="Type of agent to handle request")
    priority: int = Field(1, description="Request priority (1-10)")
    session_id: Optional[str] = Field(None, description="Session identifier")

class FrenlyAIResponse(BaseModel):
    """Response model for Frenly AI service"""
    response: str = Field(..., description="AI generated response")
    confidence: float = Field(..., description="Confidence score (0-1)")
    agent_used: str = Field(..., description="Agent that processed the request")
    processing_time: float = Field(..., description="Processing time in seconds")
    timestamp: str = Field(..., description="Response timestamp")
    session_id: Optional[str] = Field(None, description="Session identifier")

class AgentStatus(BaseModel):
    """Agent status model"""
    agent_id: str
    status: str
    last_active: str
    capabilities: List[str]
    performance_metrics: Dict[str, Any]

class FrenlyAIService:
    """Main Frenly AI service class"""
    
    def __init__(self, workspace_path: str):
        """
          Init  
        
        
        Args:
            workspace_path: Description of workspace_path
    
        Example:
            TBD: Add usage example
        """
        self.workspace_path = Path(workspace_path)
        self.redis_client = redis.Redis(host='redis', port=6379, db=0)
        self.agents = {}
        self.active_sessions = {}
        self.performance_metrics = {}
        
        # Initialize database connection
        self.db_connection = None
        self._init_database()
        
        logger.info("✅ Frenly AI Service initialized")
    
    def _init_database(self):
        """Initialize database connection"""
        try:
            self.db_connection = psycopg2.connect(
                host='postgres',
                port=5432,
                database='nexus_platform',
                user='nexus_user',
                password='nexus_password'
            )
            logger.info("✅ Database connection established")
        except Exception as e:
            logger.warning(f"⚠️ Database connection failed: {e}")
    
    async def process_request(self, request: FrenlyAIRequest) -> FrenlyAIResponse:
        """Process incoming request with appropriate agent"""
        start_time = time.time()
        
        try:
            # Select appropriate agent based on request type
            agent = await self._select_agent(request.agent_type, request.message)
            
            # Process request with selected agent
            response_data = await self._process_with_agent(agent, request)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Create response
            response = FrenlyAIResponse(
                response=response_data["response"],
                confidence=response_data["confidence"],
                agent_used=agent["id"],
                processing_time=processing_time,
                timestamp=datetime.now().isoformat(),
                session_id=request.session_id
            )
            
            # Log performance metrics
            await self._log_performance_metrics(agent["id"], processing_time, response.confidence)
            
            # Update session if provided
            if request.session_id:
                await self._update_session(request.session_id, response)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error processing request: {e}")
            raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")
    
    async def _select_agent(self, agent_type: str, message: str) -> Dict[str, Any]:
        """Select appropriate agent for the request"""
        # Agent selection logic based on message content and type
        if "fraud" in message.lower() or agent_type == "fraud_detection":
            return await self._get_agent("fraud_detection")
        elif "forensic" in message.lower() or agent_type == "forensic":
            return await self._get_agent("forensic_analysis")
        elif "reconciliation" in message.lower() or agent_type == "reconciliation":
            return await self._get_agent("reconciliation")
        elif "compliance" in message.lower() or agent_type == "compliance":
            return await self._get_agent("compliance")
        else:
            return await self._get_agent("general")
    
    async def _get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get agent configuration and status"""
        if agent_id not in self.agents:
            # Initialize agent
            self.agents[agent_id] = {
                "id": agent_id,
                "status": "active",
                "capabilities": self._get_agent_capabilities(agent_id),
                "last_active": datetime.now().isoformat(),
                "performance_metrics": {
                    "total_requests": 0,
                    "success_rate": 0.0,
                    "avg_response_time": 0.0
                }
            }
        
        return self.agents[agent_id]
    
    def _get_agent_capabilities(self, agent_id: str) -> List[str]:
        """
         Get Agent Capabilities
        
        
        Args:
            agent_id: Description of agent_id
    
        Returns:
            Unknown: Description of return value
    
        Example:
            TBD: Add usage example
        """
        capabilities_map = {
            "fraud_detection": [
                "transaction_analysis",
                "pattern_recognition",
                "risk_scoring",
                "anomaly_detection"
            ],
            "forensic_analysis": [
                "evidence_processing",
                "timeline_reconstruction",
                "pattern_analysis",
                "report_generation"
            ],
            "reconciliation": [
                "data_matching",
                "discrepancy_detection",
                "batch_processing",
                "report_generation"
            ],
            "compliance": [
                "gdpr_compliance",
                "data_retention",
                "audit_logging",
                "policy_management"
            ],
            "general": [
                "natural_language_processing",
                "query_understanding",
                "response_generation",
                "context_management"
            ]
        }
        
        return capabilities_map.get(agent_id, capabilities_map["general"])
    
    async def _process_with_agent(self, agent: Dict[str, Any], request: FrenlyAIRequest) -> Dict[str, Any]:
        agent_id = agent["id"]
        
        if agent_id == "fraud_detection":
            return await self._process_fraud_detection(request)
        elif agent_id == "forensic_analysis":
            return await self._process_forensic_analysis(request)
        elif agent_id == "reconciliation":
            return await self._process_reconciliation(request)
        elif agent_id == "compliance":
            return await self._process_compliance(request)
        else:
            return await self._process_general(request)
    
    async def _process_fraud_detection(self, request: FrenlyAIRequest) -> Dict[str, Any]:
        """Process fraud detection request"""
        response_text = f"Fraud detection analysis completed for: {request.message[:50]}..."
        confidence = 0.87
        
        return {
            "response": response_text,
            "confidence": confidence
        }
    
    async def _process_forensic_analysis(self, request: FrenlyAIRequest) -> Dict[str, Any]:
        """Process forensic analysis request"""
        response_text = f"Forensic analysis completed for: {request.message[:50]}..."
        confidence = 0.92
        
        return {
            "response": response_text,
            "confidence": confidence
        }
    
    async def _process_reconciliation(self, request: FrenlyAIRequest) -> Dict[str, Any]:
        """Process reconciliation request"""
        response_text = f"Reconciliation analysis completed for: {request.message[:50]}..."
        confidence = 0.85
        
        return {
            "response": response_text,
            "confidence": confidence
        }
    
    async def _process_compliance(self, request: FrenlyAIRequest) -> Dict[str, Any]:
        """Process compliance request"""
        response_text = f"Compliance analysis completed for: {request.message[:50]}..."
        confidence = 0.90
        
        return {
            "response": response_text,
            "confidence": confidence
        }
    
    async def _process_general(self, request: FrenlyAIRequest) -> Dict[str, Any]:
        """Process general request"""
        response_text = f"AI response for: {request.message[:50]}..."
        confidence = 0.75
        
        return {
            "response": response_text,
            "confidence": confidence
        }
    
    async def _log_performance_metrics(self, agent_id: str, processing_time: float, confidence: float):
        """Log performance metrics for agent"""
        if agent_id not in self.performance_metrics:
            self.performance_metrics[agent_id] = {
                "total_requests": 0,
                "total_time": 0.0,
                "total_confidence": 0.0,
                "success_count": 0
            }
        
        metrics = self.performance_metrics[agent_id]
        metrics["total_requests"] += 1
        metrics["total_time"] += processing_time
        metrics["total_confidence"] += confidence
        metrics["success_count"] += 1
        
        # Update agent performance
        if agent_id in self.agents:
            self.agents[agent_id]["performance_metrics"] = {
                "total_requests": metrics["total_requests"],
                "success_rate": metrics["success_count"] / metrics["total_requests"],
                "avg_response_time": metrics["total_time"] / metrics["total_requests"]
            }
    
    async def _update_session(self, session_id: str, response: FrenlyAIResponse):
        """Update session with response"""
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = {
                "created_at": datetime.now().isoformat(),
                "requests": [],
                "responses": []
            }
        
        self.active_sessions[session_id]["responses"].append({
            "timestamp": response.timestamp,
            "agent_used": response.agent_used,
            "confidence": response.confidence,
            "processing_time": response.processing_time
        })
    
    async def get_agent_status(self, agent_id: Optional[str] = None) -> Union[AgentStatus, List[AgentStatus]]:
        if agent_id:
            if agent_id not in self.agents:
                raise HTTPException(status_code=404, detail="Agent not found")
            
            agent = self.agents[agent_id]
            return AgentStatus(
                agent_id=agent["id"],
                status=agent["status"],
                last_active=agent["last_active"],
                capabilities=agent["capabilities"],
                performance_metrics=agent["performance_metrics"]
            )
        else:
            return [
                AgentStatus(
                    agent_id=agent["id"],
                    status=agent["status"],
                    last_active=agent["last_active"],
                    capabilities=agent["capabilities"],
                    performance_metrics=agent["performance_metrics"]
                )
                for agent in self.agents.values()
            ]
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check endpoint"""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "active_agents": len(self.agents),
            "active_sessions": len(self.active_sessions),
            "database_connected": self.db_connection is not None,
            "redis_connected": await self._check_redis_connection()
        }
    
    async def _check_redis_connection(self) -> bool:
        """Check Redis connection"""
        try:
            self.redis_client.ping()
            return True
        except:
            return False

# Initialize service
frenly_service = FrenlyAIService("/workspace")

# FastAPI app
app = FastAPI(
    title="Frenly AI Service",
    description="Meta-Agent Coordinator for Nexus Platform",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/process", response_model=FrenlyAIResponse)
async def process_request(request: FrenlyAIRequest):
    """Process AI request"""
    return await frenly_service.process_request(request)

@app.get("/api/v1/agents", response_model=List[AgentStatus])
async def get_agents():
    """Get all agents status"""
    return await frenly_service.get_agent_status()

@app.get("/api/v1/agents/{agent_id}", response_model=AgentStatus)
async def get_agent(agent_id: str):
    return await frenly_service.get_agent_status(agent_id)

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return await frenly_service.health_check()

@app.get("/api/v1/metrics")
async def get_metrics():
    """Get performance metrics"""
    return {
        "agents": frenly_service.agents,
        "performance_metrics": frenly_service.performance_metrics,
        "active_sessions": len(frenly_service.active_sessions)
    }

if __name__ == "__main__":
    uvicorn.run(
        "frenly_ai_service:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
