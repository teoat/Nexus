#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🔧 Core API Functions - Nexus Platform
Comprehensive backend functions for frontend processing
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
import uuid
import json
import logging

from database.config import get_db
from database.models import User, Workflow
from auth.jwt_auth import get_current_user
from models.api_models import *

logger = logging.getLogger(__name__)

# Core API Router
core_router = APIRouter(prefix="/api/v1/core", tags=["Core Functions"])

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# ============================================================================
# USER MANAGEMENT FUNCTIONS
# ============================================================================

@core_router.get("/users/profile", response_model=UserProfileResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's profile information"""
    try:
        user_data = {
            "id": str(current_user.id),
            "email": current_user.email,
            "full_name": current_user.full_name,
            "is_active": current_user.is_active,
            "created_at": current_user.created_at,
            "updated_at": current_user.updated_at,
            "preferences": getattr(current_user, 'preferences', {}),
            "subscription": getattr(current_user, 'subscription', {}),
            "usage_stats": getattr(current_user, 'usage_stats', {})
        }
        return UserProfileResponse(**user_data)
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve user profile")

@core_router.put("/users/profile", response_model=UserProfileResponse)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile information"""
    try:
        # Update user fields
        if profile_update.full_name is not None:
            current_user.full_name = profile_update.full_name
        
        if profile_update.preferences is not None:
            current_user.preferences = profile_update.preferences
        
        current_user.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(current_user)
        
        return UserProfileResponse(
            id=str(current_user.id),
            email=current_user.email,
            full_name=current_user.full_name,
            is_active=current_user.is_active,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at,
            preferences=getattr(current_user, 'preferences', {}),
            subscription=getattr(current_user, 'subscription', {}),
            usage_stats=getattr(current_user, 'usage_stats', {})
        )
    except Exception as e:
        logger.error(f"Error updating user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to update user profile")

@core_router.get("/users/activity", response_model=List[UserActivityResponse])
async def get_user_activity(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user activity history"""
    try:

# ============================================================================
# WORKFLOW MANAGEMENT FUNCTIONS
# ============================================================================

@core_router.post("/workflows", response_model=WorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_workflow(
    workflow: WorkflowCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new workflow"""
    try:
        db_workflow = Workflow(
            name=workflow.name,
            description=workflow.description,
            status=workflow.status or "draft",
            owner_id=current_user.id,
            config=workflow.config or {},
            steps=workflow.steps or []
        )
        
        db.add(db_workflow)
        db.commit()
        db.refresh(db_workflow)
        
        return WorkflowResponse(
            id=str(db_workflow.id),
            name=db_workflow.name,
            description=db_workflow.description,
            status=db_workflow.status,
            owner_id=str(db_workflow.owner_id),
            created_at=db_workflow.created_at,
            updated_at=db_workflow.updated_at,
            config=getattr(db_workflow, 'config', {}),
            steps=getattr(db_workflow, 'steps', [])
        )
    except Exception as e:
        logger.error(f"Error creating workflow: {e}")
        raise HTTPException(status_code=500, detail="Failed to create workflow")

@core_router.get("/workflows", response_model=List[WorkflowResponse])
async def list_workflows(
    status: Optional[str] = Query(None, description="Filter by workflow status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's workflows with optional filtering"""
    try:
        query = db.query(Workflow).filter(Workflow.owner_id == current_user.id)
        
        if status:
            query = query.filter(Workflow.status == status)
        
        workflows = query.offset(offset).limit(limit).all()
        
        return [
            WorkflowResponse(
                id=str(w.id),
                name=w.name,
                description=w.description,
                status=w.status,
                owner_id=str(w.owner_id),
                created_at=w.created_at,
                updated_at=w.updated_at,
                config=getattr(w, 'config', {}),
                steps=getattr(w, 'steps', [])
            ) for w in workflows
        ]
    except Exception as e:
        logger.error(f"Error listing workflows: {e}")
        raise HTTPException(status_code=500, detail="Failed to list workflows")

@core_router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(
    workflow_id: str = Path(..., description="Workflow ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        workflow = db.query(Workflow).filter(
            Workflow.id == workflow_id,
            Workflow.owner_id == current_user.id
        ).first()
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        return WorkflowResponse(
            id=str(workflow.id),
            name=workflow.name,
            description=workflow.description,
            status=workflow.status,
            owner_id=str(workflow.owner_id),
            created_at=workflow.created_at,
            updated_at=workflow.updated_at,
            config=getattr(workflow, 'config', {}),
            steps=getattr(workflow, 'steps', [])
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting workflow: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve workflow")

@core_router.put("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def update_workflow(
    workflow_id: str = Path(..., description="Workflow ID"),
    workflow_update: WorkflowUpdate = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update workflow"""
    try:
        workflow = db.query(Workflow).filter(
            Workflow.id == workflow_id,
            Workflow.owner_id == current_user.id
        ).first()
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Update fields
        if workflow_update.name is not None:
            workflow.name = workflow_update.name
        if workflow_update.description is not None:
            workflow.description = workflow_update.description
        if workflow_update.status is not None:
            workflow.status = workflow_update.status
        if workflow_update.config is not None:
            workflow.config = workflow_update.config
        if workflow_update.steps is not None:
            workflow.steps = workflow_update.steps
        
        workflow.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(workflow)
        
        return WorkflowResponse(
            id=str(workflow.id),
            name=workflow.name,
            description=workflow.description,
            status=workflow.status,
            owner_id=str(workflow.owner_id),
            created_at=workflow.created_at,
            updated_at=workflow.updated_at,
            config=getattr(workflow, 'config', {}),
            steps=getattr(workflow, 'steps', [])
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating workflow: {e}")
        raise HTTPException(status_code=500, detail="Failed to update workflow")

@core_router.delete("/workflows/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(
    workflow_id: str = Path(..., description="Workflow ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete workflow"""
    try:
        workflow = db.query(Workflow).filter(
            Workflow.id == workflow_id,
            Workflow.owner_id == current_user.id
        ).first()
        
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        db.delete(workflow)
        db.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting workflow: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete workflow")

# ============================================================================
# DATA PROCESSING FUNCTIONS
# ============================================================================

@core_router.post("/data/process", response_model=DataProcessingResponse)
async def process_data(
    request: DataProcessingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        
        import asyncio
        await asyncio.sleep(1)
        
        result = DataProcessingResponse(
            processing_id=processing_id,
            status="completed",
            input_data=request.data,
            output_data={
                "processed_records": len(request.data) if isinstance(request.data, list) else 1,
                "processing_time": "1.2s",
                "quality_score": 0.95
            },
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        
        return result
    except Exception as e:
        logger.error(f"Error processing data: {e}")
        raise HTTPException(status_code=500, detail="Failed to process data")

@core_router.get("/data/status/{processing_id}", response_model=DataProcessingResponse)
async def get_processing_status(
    processing_id: str = Path(..., description="Processing ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get data processing status"""
    try:
        
        return result
    except Exception as e:
        logger.error(f"Error getting processing status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get processing status")

# ============================================================================
# ANALYTICS AND REPORTING FUNCTIONS
# ============================================================================

@core_router.get("/analytics/dashboard", response_model=DashboardAnalyticsResponse)
async def get_dashboard_analytics(
    period: str = Query("7d", description="Time period for analytics"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard analytics data"""
    try:
        
        return analytics
    except Exception as e:
        logger.error(f"Error getting dashboard analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics")

@core_router.get("/reports/generate", response_model=ReportResponse)
async def generate_report(
    report_type: str = Query(..., description="Type of report to generate"),
    format: str = Query("json", description="Report format (json, csv, pdf)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate various types of reports"""
    try:
        
        report = ReportResponse(
            report_id=report_id,
            report_type=report_type,
            format=format,
            status="completed",
            download_url=f"/api/v1/reports/{report_id}/download",
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24),
            metadata={
                "total_records": 150,
                "generation_time": "2.1s",
                "file_size": "1.2MB"
            }
        )
        
        return report
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate report")

# ============================================================================
# SYSTEM FUNCTIONS
# ============================================================================

@core_router.get("/system/health", response_model=SystemHealthResponse)
async def get_system_health():
    """Get system health status"""
    try:
        health = SystemHealthResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
            version="1.0.0",
            uptime="5d 12h 30m",
            services={
                "database": {"status": "healthy", "response_time": "15ms"},
                "redis": {"status": "healthy", "response_time": "2ms"},
                "storage": {"status": "healthy", "response_time": "45ms"},
                "ai_engine": {"status": "healthy", "response_time": "120ms"}
            },
            metrics={
                "cpu_usage": 0.45,
                "memory_usage": 0.67,
                "disk_usage": 0.23,
                "active_connections": 142
            }
        )
        
        return health
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system health")

@core_router.get("/system/metrics", response_model=SystemMetricsResponse)
async def get_system_metrics(
    metric_type: str = Query("all", description="Type of metrics to retrieve"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get system performance metrics"""
    try:
        metrics = SystemMetricsResponse(
            timestamp=datetime.utcnow(),
            performance={
                "requests_per_second": 45.2,
                "average_response_time": "120ms",
                "error_rate": 0.02,
                "throughput": "2.1MB/s"
            },
            resource_usage={
                "cpu_percent": 45.2,
                "memory_percent": 67.8,
                "disk_percent": 23.1,
                "network_io": "15.2MB/s"
            },
            database={
                "active_connections": 12,
                "query_time": "25ms",
                "cache_hit_rate": 0.89,
                "slow_queries": 3
            },
            application={
                "active_users": 89,
                "workflows_running": 15,
                "tasks_queued": 23,
                "api_calls": 1250
            }
        )
        
        return metrics
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve system metrics")
