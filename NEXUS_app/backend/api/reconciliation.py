#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🔄 Reconciliation & Human Judgment API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from database.config import get_db
from database.models.reconciliation import (
    ReconciliationJob, ReconciliationDiscrepancy, HumanJudgment, 
    Evidence, ReconciliationRule, ReconciliationAuditLog,
    ReconciliationStatus, JudgmentStatus, EvidenceType
)
from models.reconciliation import (
    ReconciliationJobCreate, ReconciliationJobUpdate, ReconciliationJobResponse,
    DiscrepancyResponse, JudgmentRequest, JudgmentResponse, EvidenceCreate,
    ReconciliationSummary, JudgmentDashboard
)
from auth.jwt_auth import get_current_user
from core.reconciliation.engine import ReconciliationEngine
from core.reconciliation.judgment_processor import JudgmentProcessor

router = APIRouter(prefix="/reconciliation", tags=["Reconciliation"])

# Initialize reconciliation engine
reconciliation_engine = ReconciliationEngine()
judgment_processor = JudgmentProcessor()

@router.post("/jobs", response_model=ReconciliationJobResponse)
async def create_reconciliation_job(
    job_data: ReconciliationJobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new reconciliation job"""
    try:
        # Create job
        job = ReconciliationJob(
            name=job_data.name,
            description=job_data.description,
            source_system=job_data.source_system,
            target_system=job_data.target_system,
            data_type=job_data.data_type,
            matching_criteria=job_data.matching_criteria,
            tolerance_threshold=job_data.tolerance_threshold,
            created_by=current_user.id
        )
        
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Start reconciliation process in background
        background_tasks.add_task(
            reconciliation_engine.process_reconciliation,
            job.id,
            job_data.source_data,
            job_data.target_data
        )
        
        # Log audit trail
        audit_log = ReconciliationAuditLog(
            job_id=job.id,
            action="created",
            entity_type="job",
            entity_id=job.id,
            new_values=job_data.dict(),
            performed_by=current_user.id,
            reason="New reconciliation job created"
        )
        db.add(audit_log)
        db.commit()
        
        return job
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create reconciliation job: {str(e)}"
        )

@router.get("/jobs", response_model=List[ReconciliationJobResponse])
async def get_reconciliation_jobs(
    status: Optional[ReconciliationStatus] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get reconciliation jobs with optional filtering"""
    query = db.query(ReconciliationJob)
    
    if status:
        query = query.filter(ReconciliationJob.status == status)
    
    jobs = query.offset(offset).limit(limit).all()
    return jobs

@router.get("/jobs/{job_id}", response_model=ReconciliationJobResponse)
async def get_reconciliation_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    job = db.query(ReconciliationJob).filter(ReconciliationJob.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reconciliation job not found"
        )
    return job

@router.get("/jobs/{job_id}/summary", response_model=ReconciliationSummary)
async def get_reconciliation_summary(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get reconciliation job summary with statistics"""
    job = db.query(ReconciliationJob).filter(ReconciliationJob.id == job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reconciliation job not found"
        )
    
    # Get discrepancy statistics
    discrepancies = db.query(ReconciliationDiscrepancy).filter(
        ReconciliationDiscrepancy.job_id == job_id
    ).all()
    
    # Get judgment statistics
    judgments = db.query(HumanJudgment).filter(
        HumanJudgment.job_id == job_id
    ).all()
    
    summary = ReconciliationSummary(
        job_id=job.id,
        job_name=job.name,
        status=job.status,
        total_records=job.total_records,
        matched_records=job.matched_records,
        unmatched_records=job.unmatched_records,
        discrepancy_count=job.discrepancy_count,
        confidence_score=job.confidence_score,
        total_discrepancies=len(discrepancies),
        pending_judgments=len([j for j in judgments if j.status == JudgmentStatus.PENDING]),
        completed_judgments=len([j for j in judgments if j.status == JudgmentStatus.APPROVED]),
        created_at=job.created_at,
        completed_at=job.completed_at
    )
    
    return summary

@router.get("/jobs/{job_id}/discrepancies", response_model=List[DiscrepancyResponse])
async def get_discrepancies(
    job_id: uuid.UUID,
    severity: Optional[str] = None,
    status: Optional[ReconciliationStatus] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get discrepancies for a reconciliation job"""
    query = db.query(ReconciliationDiscrepancy).filter(
        ReconciliationDiscrepancy.job_id == job_id
    )
    
    if severity:
        query = query.filter(ReconciliationDiscrepancy.severity == severity)
    if status:
        query = query.filter(ReconciliationDiscrepancy.status == status)
    
    discrepancies = query.offset(offset).limit(limit).all()
    return discrepancies

@router.post("/judgments", response_model=JudgmentResponse)
async def create_judgment_request(
    judgment_data: JudgmentRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a human judgment request"""
    try:
        judgment = HumanJudgment(
            job_id=judgment_data.job_id,
            discrepancy_id=judgment_data.discrepancy_id,
            judgment_type=judgment_data.judgment_type,
            title=judgment_data.title,
            description=judgment_data.description,
            context_data=judgment_data.context_data,
            suggested_action=judgment_data.suggested_action,
            priority=judgment_data.priority,
            assigned_to=judgment_data.assigned_to
        )
        
        db.add(judgment)
        db.commit()
        db.refresh(judgment)
        
        # Log audit trail
        audit_log = ReconciliationAuditLog(
            job_id=judgment_data.job_id,
            judgment_id=judgment.id,
            action="created",
            entity_type="judgment",
            entity_id=judgment.id,
            new_values=judgment_data.dict(),
            performed_by=current_user.id,
            reason="Human judgment request created"
        )
        db.add(audit_log)
        db.commit()
        
        return judgment
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create judgment request: {str(e)}"
        )

@router.put("/judgments/{judgment_id}/review", response_model=JudgmentResponse)
async def review_judgment(
    judgment_id: uuid.UUID,
    decision: str,
    reasoning: str,
    confidence: float,
    alternative_solution: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Submit human judgment decision"""
    try:
        judgment = db.query(HumanJudgment).filter(
            HumanJudgment.id == judgment_id
        ).first()
        
        if not judgment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Judgment not found"
            )
        
        # Update judgment
        judgment.decision = decision
        judgment.decision_reasoning = reasoning
        judgment.decision_confidence = confidence
        judgment.alternative_solution = alternative_solution
        judgment.reviewed_by = current_user.id
        judgment.reviewed_at = datetime.utcnow()
        judgment.status = JudgmentStatus.APPROVED if decision == "approve" else JudgmentStatus.REJECTED
        
        db.commit()
        db.refresh(judgment)
        
        # Process judgment decision
        await judgment_processor.process_judgment_decision(judgment.id, db)
        
        # Log audit trail
        audit_log = ReconciliationAuditLog(
            job_id=judgment.job_id,
            judgment_id=judgment.id,
            action="reviewed",
            entity_type="judgment",
            entity_id=judgment.id,
            old_values={"status": "pending"},
            new_values={"status": judgment.status, "decision": decision},
            performed_by=current_user.id,
            reason=f"Judgment {decision}ed by human reviewer"
        )
        db.add(audit_log)
        db.commit()
        
        return judgment
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process judgment: {str(e)}"
        )

@router.get("/judgments/dashboard", response_model=JudgmentDashboard)
async def get_judgment_dashboard(
    assigned_to: Optional[uuid.UUID] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get human judgment dashboard data"""
    query = db.query(HumanJudgment)
    
    if assigned_to:
        query = query.filter(HumanJudgment.assigned_to == assigned_to)
    
    judgments = query.all()
    
    dashboard = JudgmentDashboard(
        total_judgments=len(judgments),
        pending_judgments=len([j for j in judgments if j.status == JudgmentStatus.PENDING]),
        in_review_judgments=len([j for j in judgments if j.status == JudgmentStatus.IN_REVIEW]),
        completed_judgments=len([j for j in judgments if j.status == JudgmentStatus.APPROVED]),
        urgent_judgments=len([j for j in judgments if j.priority == "urgent"]),
        my_judgments=len([j for j in judgments if j.assigned_to == current_user.id]),
        recent_judgments=judgments[-10:] if judgments else []
    )
    
    return dashboard

@router.post("/evidence", response_model=Dict[str, Any])
async def upload_evidence(
    evidence_data: EvidenceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Upload evidence for reconciliation"""
    try:
        evidence = Evidence(
            job_id=evidence_data.job_id,
            discrepancy_id=evidence_data.discrepancy_id,
            judgment_id=evidence_data.judgment_id,
            evidence_type=evidence_data.evidence_type,
            title=evidence_data.title,
            description=evidence_data.description,
            data=evidence_data.data,
            file_path=evidence_data.file_path,
            file_hash=evidence_data.file_hash,
            file_size=evidence_data.file_size,
            mime_type=evidence_data.mime_type,
            source_system=evidence_data.source_system,
            timestamp=evidence_data.timestamp,
            created_by=current_user.id
        )
        
        db.add(evidence)
        db.commit()
        db.refresh(evidence)
        
        return {"evidence_id": evidence.id, "status": "uploaded"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload evidence: {str(e)}"
        )

@router.get("/rules", response_model=List[Dict[str, Any]])
async def get_reconciliation_rules(
    source_system: Optional[str] = None,
    target_system: Optional[str] = None,
    data_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get reconciliation rules"""
    query = db.query(ReconciliationRule).filter(ReconciliationRule.is_active == True)
    
    if source_system:
        query = query.filter(ReconciliationRule.source_system == source_system)
    if target_system:
        query = query.filter(ReconciliationRule.target_system == target_system)
    if data_type:
        query = query.filter(ReconciliationRule.data_type == data_type)
    
    rules = query.all()
    return [rule.__dict__ for rule in rules]

@router.post("/jobs/{job_id}/resolve", response_model=Dict[str, Any])
async def resolve_discrepancy(
    job_id: uuid.UUID,
    discrepancy_id: uuid.UUID,
    resolution: str,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Manually resolve a discrepancy"""
    try:
        discrepancy = db.query(ReconciliationDiscrepancy).filter(
            ReconciliationDiscrepancy.id == discrepancy_id,
            ReconciliationDiscrepancy.job_id == job_id
        ).first()
        
        if not discrepancy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Discrepancy not found"
            )
        
        # Update discrepancy
        discrepancy.status = ReconciliationStatus.COMPLETED
        discrepancy.resolution_notes = notes
        discrepancy.resolved_by = current_user.id
        discrepancy.resolved_at = datetime.utcnow()
        
        db.commit()
        
        # Log audit trail
        audit_log = ReconciliationAuditLog(
            job_id=job_id,
            discrepancy_id=discrepancy_id,
            action="resolved",
            entity_type="discrepancy",
            entity_id=discrepancy_id,
            old_values={"status": "pending"},
            new_values={"status": "completed", "resolution": resolution},
            performed_by=current_user.id,
            reason=f"Discrepancy manually resolved: {resolution}"
        )
        db.add(audit_log)
        db.commit()
        
        return {"status": "resolved", "discrepancy_id": discrepancy_id}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resolve discrepancy: {str(e)}"
        )
