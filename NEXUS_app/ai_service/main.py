#!/usr/bin/env python3
"""
AI Service - Nexus Platform
Comprehensive API endpoints for all AI functionalities
"""

import logging
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from fastapi.security import HTTPBearer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global service state
service_state = {}


# Pydantic models for request/response
class ReconciliationRequest(BaseModel):
    source_data: List[Dict[str, Any]] = Field(
        ..., description="Source data for reconciliation"
    )
    target_data: List[Dict[str, Any]] = Field(
        ..., description="Target data for reconciliation"
    )
    confidence_threshold: float = Field(0.8, description="Minimum confidence threshold")
    matching_fields: List[str] = Field(..., description="Fields to use for matching")


class ReconciliationResponse(BaseModel):
    matches: List[Dict[str, Any]] = Field(..., description="Matched records")
    confidence_scores: List[float] = Field(
        ..., description="Confidence scores for matches"
    )
    unmatched_source: List[Dict[str, Any]] = Field(
        ..., description="Unmatched source records"
    )
    unmatched_target: List[Dict[str, Any]] = Field(
        ..., description="Unmatched target records"
    )
    processing_time: float = Field(..., description="Processing time in seconds")


class FraudDetectionRequest(BaseModel):
    transactions: List[Dict[str, Any]] = Field(
        ..., description="Transaction data to analyze"
    )
    user_profile: Optional[Dict[str, Any]] = Field(
        None, description="User profile for context"
    )
    risk_threshold: float = Field(0.7, description="Risk threshold for fraud detection")


class FraudDetectionResponse(BaseModel):
    fraud_scores: List[float] = Field(..., description="Fraud risk scores")
    risk_levels: List[str] = Field(..., description="Risk levels (low, medium, high)")
    flagged_transactions: List[int] = Field(
        ..., description="Indices of flagged transactions"
    )
    risk_factors: List[List[str]] = Field(
        ..., description="Risk factors for each transaction"
    )
    processing_time: float = Field(..., description="Processing time in seconds")


class NLPRequest(BaseModel):
    text: str = Field(..., description="Text to process")
    language: str = Field("en", description="Language code")
    tasks: List[str] = Field(..., description="NLP tasks to perform")


class NLPResponse(BaseModel):
    entities: List[Dict[str, Any]] = Field(..., description="Extracted entities")
    sentiment: Dict[str, float] = Field(..., description="Sentiment analysis results")
    keywords: List[str] = Field(..., description="Extracted keywords")
    summary: str = Field(..., description="Text summary")
    processing_time: float = Field(..., description="Processing time in seconds")


class OCRRequest(BaseModel):
    document_data: bytes = Field(..., description="Document data (base64 encoded)")
    document_type: str = Field(..., description="Type of document")
    language: str = Field("en", description="Document language")


class OCRResponse(BaseModel):
    extracted_text: str = Field(..., description="Extracted text from document")
    confidence: float = Field(..., description="OCR confidence score")
    metadata: Dict[str, Any] = Field(..., description="Document metadata")
    processing_time: float = Field(..., description="Processing time in seconds")


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str


# Authentication dependency
async def verify_token(token: str = Depends(HTTPBearer())):
    """Verify authentication token"""
    # TODO: Implement actual token verification
    return "test_user"  # Placeholder for now


async def lifespan(app):
    """Application lifespan manager"""
    logger.info("Starting AI Service...")

    # Initialize service components
    try:
        # Initialize Taskmaster
        from taskmaster.core.taskmaster import Taskmaster

        taskmaster = Taskmaster()
        service_state["taskmaster"] = taskmaster
        logger.info("Taskmaster initialized successfully")

        # Initialize AI Agents
        from agents.reconciliation_agent import ReconciliationAgent
        from agents.fraud_agent import FraudAgent
        from agents.risk_agent import RiskAgent
        from agents.evidence_agent import EvidenceAgent
        from agents.litigation_agent import LitigationAgent
        from agents.help_agent import HelpAgent

        service_state["reconciliation_agent"] = ReconciliationAgent()
        service_state["fraud_agent"] = FraudAgent()
        service_state["risk_agent"] = RiskAgent()
        service_state["evidence_agent"] = EvidenceAgent()
        service_state["litigation_agent"] = LitigationAgent()
        service_state["help_agent"] = HelpAgent()

        logger.info("AI Agents initialized successfully")

        # Initialize Frenly Meta Agent and MCP Bridge
        from agents.frenly_meta_agent import FrenlyMetaAgent
        from agents.frenly_mcp_bridge import FrenlyMCPBridge

        # Create Frenly with configuration
        frenly_config = {
            "enable_ai_classification": True,
            "enable_memory": True,
            "max_memory_size": 1000,
            "response_timeout": 30.0,
        }

        frenly_agent = FrenlyMetaAgent(frenly_config)
        mcp_bridge = FrenlyMCPBridge(
            {"default_timeout": 30.0, "max_retries": 3, "retry_delay": 1.0}
        )

        # Register all sub-agents with Frenly and MCP bridge
        frenly_agent.sub_agents = {
            "reconciliation_agent": service_state["reconciliation_agent"],
            "fraud_agent": service_state["fraud_agent"],
            "risk_agent": service_state["risk_agent"],
            "evidence_agent": service_state["evidence_agent"],
            "litigation_agent": service_state["litigation_agent"],
            "help_agent": service_state["help_agent"],
        }

        # Register agents with MCP bridge
        for agent_name, agent in frenly_agent.sub_agents.items():
            mcp_bridge.register_agent(agent_name, agent)

        # Store Frenly components in service state
        service_state["frenly_agent"] = frenly_agent
        service_state["mcp_bridge"] = mcp_bridge

        # Start Frenly components
        await frenly_agent.start()
        await mcp_bridge.start()

        logger.info("Frenly Meta Agent and MCP Bridge initialized successfully")

        # Initialize Orchestration
        from orchestration.orchestration_manager import OrchestrationManager

        orchestration_manager = OrchestrationManager()
        service_state["orchestration_manager"] = orchestration_manager
        logger.info("Orchestration Manager initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize service components: {e}")
        raise

    logger.info("AI Service started successfully")
    yield

    # Shutdown
    logger.info("Shutting down AI Service...")
    # Cleanup resources if needed


# Create FastAPI app
app = FastAPI(
    title="Nexus + Fraud Platform - AI Service",
    description="AI-powered Nexus and fraud detection service with Frenly Meta Agent",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Frenly API routes
from frenly_api import get_frenly_router

frenly_router = get_frenly_router()
app.include_router(frenly_router)


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "Nexus + Fraud Platform - AI Service with Frenly Meta Agent",
        "status": "running",
        "frenly": "Available at /api/frenly",
        "service": "Forensic AI Service",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "health_detailed": "/health/detailed",
            "status": "/status",
            "frenly": "/api/frenly",
            "reconciliation": "/api/v1/reconcile",
            "fraud_detection": "/api/v1/fraud-detect",
            "docs": "/docs",
        },
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="ai_service",
        version="1.0.0",
        timestamp=datetime.utcnow().isoformat(),
    )


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check including all components"""
    try:
        health_status = {
            "service": "ai_service",
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "components": {},
        }

        # Check Frenly components specifically
        frenly_agent = service_state.get("frenly_agent")
        mcp_bridge = service_state.get("mcp_bridge")

        if frenly_agent:
            health_status["components"][
                "frenly_agent"
            ] = frenly_agent.get_agent_status()

        if mcp_bridge:
            health_status["components"]["mcp_bridge"] = mcp_bridge.get_bridge_status()

        # Check other components
        for component_name, component in service_state.items():
            if component_name not in ["frenly_agent", "mcp_bridge"]:
                try:
                    if hasattr(component, "health_check"):
                        health = await component.health_check()
                        health_status["components"][component_name] = health
                    else:
                        health_status["components"][component_name] = {
                            "status": "unknown"
                        }
                except Exception as e:
                    health_status["components"][component_name] = {
                        "status": "error",
                        "error": str(e),
                    }

        return health_status

    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def service_status():
    """Get service status and component health"""
    status = {"service": "ai_service", "status": "running", "components": {}}

    # Check component status
    for component_name, component in service_state.items():
        try:
            if hasattr(component, "health_check"):
                health = await component.health_check()
                status["components"][component_name] = health
            else:
                status["components"][component_name] = {"status": "unknown"}
        except Exception as e:
            status["components"][component_name] = {"status": "error", "error": str(e)}

    return status


# Reconciliation API endpoints
@app.post("/api/v1/reconcile", response_model=ReconciliationResponse)
async def reconcile_data(
    request: ReconciliationRequest, user_id: str = Depends(verify_token)
):
    start_time = datetime.utcnow()
    try:
        matches = []
        confidence_scores = []

        for source_item in request.source_data:
            for target_item in request.target_data:
                match_score = 0
                for field in request.matching_fields:
                    if source_item.get(field) == target_item.get(field):
                        match_score += 1
                    else:
                        match_score -= 1  # Penalize mismatch

                if match_score >= request.confidence_threshold:
                    matches.append(
                        {
                            "source": source_item,
                            "target": target_item,
                            "matched_fields": request.matching_fields,
                        }
                    )
                    confidence_scores.append(match_score / len(request.matching_fields))

        processing_time = (datetime.utcnow() - start_time).total_seconds()

        return ReconciliationResponse(
            matches=matches,
            confidence_scores=confidence_scores,
            unmatched_source=request.source_data,
            unmatched_target=request.target_data,
            processing_time=processing_time,
        )

    except Exception as e:
        logger.error(f"Reconciliation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Reconciliation failed: {str(e)}",
        )


# Fraud detection API endpoints
@app.post("/api/v1/fraud-detect", response_model=FraudDetectionResponse)
async def detect_fraud(
    request: FraudDetectionRequest, user_id: str = Depends(verify_token)
):
    start_time = datetime.utcnow()
    try:
        fraud_scores = []
        risk_levels = []
        flagged_transactions = []
        risk_factors = []

        for i, transaction in enumerate(request.transactions):
            risk_score = 0.0
            factors = []

            if transaction.get("amount", 0) > 10000:
                risk_score += 0.3
                factors.append("high_amount")

            if transaction.get("frequency", 0) > 10:
                risk_score += 0.2
                factors.append("high_frequency")

            if transaction.get("location") != request.user_profile.get(
                "usual_location"
            ):
                risk_score += 0.2
                factors.append("unusual_location")

            fraud_scores.append(min(risk_score, 1.0))

            if risk_score > request.risk_threshold:
                risk_levels.append("high")
                flagged_transactions.append(i)
            elif risk_score > request.risk_threshold * 0.5:
                risk_levels.append("medium")
            else:
                risk_levels.append("low")

            risk_factors.append(factors)

        processing_time = (datetime.utcnow() - start_time).total_seconds()

        return FraudDetectionResponse(
            fraud_scores=fraud_scores,
            risk_levels=risk_levels,
            flagged_transactions=flagged_transactions,
            risk_factors=risk_factors,
            processing_time=processing_time,
        )

    except Exception as e:
        logger.error(f"Fraud detection error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fraud detection failed: {str(e)}",
        )


# NLP API endpoints
@app.post("/api/v1/nlp", response_model=NLPResponse)
async def process_nlp(request: NLPRequest, user_id: str = Depends(verify_token)):
    """Process NLP request"""
    start_time = datetime.utcnow()

    try:
        # Simple NLP processing
        entities = ["sample_entity"]  # TODO: Implement actual NER
        sentiment = {"positive": 0.5, "negative": 0.3, "neutral": 0.2}
        keywords = request.text.lower().split()[:10]  # Simple keyword extraction
        summary = (
            request.text[:100] + "..." if len(request.text) > 100 else request.text
        )

        processing_time = (datetime.utcnow() - start_time).total_seconds()

        return NLPResponse(
            entities=entities,
            sentiment=sentiment,
            keywords=keywords,
            summary=summary,
            processing_time=processing_time,
        )

    except Exception as e:
        logger.error(f"NLP processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"NLP processing failed: {str(e)}",
        )


# OCR API endpoints
@app.post("/api/v1/ocr", response_model=OCRResponse)
async def process_ocr(request: OCRRequest, user_id: str = Depends(verify_token)):
    """Process OCR request"""
    start_time = datetime.utcnow()

    try:
        # Simple OCR processing
        extracted_text = "Sample extracted text from document"
        confidence = 0.85
        metadata = {
            "document_type": request.document_type,
            "language": request.language,
            "size": len(request.document_data),
        }

        processing_time = (datetime.utcnow() - start_time).total_seconds()

        return OCRResponse(
            extracted_text=extracted_text,
            confidence=confidence,
            metadata=metadata,
            processing_time=processing_time,
        )

    except Exception as e:
        logger.error(f"OCR processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR processing failed: {str(e)}",
        )


# Metrics endpoint for monitoring
@app.get("/metrics")
async def get_metrics():
    """Get service metrics"""
    return {
        "requests_total": 0,  # TODO: Implement actual metrics
        "requests_successful": 0,
        "requests_failed": 0,
        "average_response_time": 0.0,
        "active_connections": 0,
    }


# Note: Frenly status is now available at /api/frenly/status via the Frenly API router


@app.post("/process/reconciliation")
async def process_reconciliation(data: Dict[str, Any]):
    """Process reconciliation request"""
    try:
        reconciliation_agent = service_state.get("reconciliation_agent")
        if not reconciliation_agent:
            raise HTTPException(
                status_code=500, detail="Reconciliation agent not available"
            )

        # Process the reconciliation request
        result = await reconciliation_agent.process_reconciliation(data)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Reconciliation processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/process/fraud")
async def process_fraud(data: Dict[str, Any]):
    """Process fraud detection request"""
    try:
        fraud_agent = service_state.get("fraud_agent")
        if not fraud_agent:
            raise HTTPException(status_code=500, detail="Fraud agent not available")

        # Process the fraud detection request
        result = await fraud_agent.process_fraud_detection(data)
        return {"status": "success", "result": result}
    except Exception as e:
        logger.error(f"Fraud detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
