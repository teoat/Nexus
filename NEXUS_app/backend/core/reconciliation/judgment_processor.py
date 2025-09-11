#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
👥 Human Judgment Processor - Manages human decision workflow
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid

from sqlalchemy.orm import Session
from database.models.reconciliation import (
    HumanJudgment, ReconciliationDiscrepancy, ReconciliationJob,
    JudgmentStatus, ReconciliationStatus
)
from models.reconciliation import JudgmentRequest, JudgmentResponse
from core.notifications.notification_service import NotificationService

logger = logging.getLogger(__name__)

class JudgmentProcessor:
    """Processes human judgment requests and decisions"""
    
    def __init__(self):
        """
          Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        self.notification_service = NotificationService()
        self.auto_escalation_hours = 24  # Auto-escalate after 24 hours
        self.urgent_escalation_hours = 4  # Escalate urgent items after 4 hours
    
    async def create_judgment_request(
        self, 
        job_id: uuid.UUID, 
        discrepancy_id: Optional[uuid.UUID],
        judgment_data: JudgmentRequest,
        db: Session
    ) -> HumanJudgment:
        """Create a new human judgment request"""
        try:
            # Create judgment request
            judgment = HumanJudgment(
                job_id=job_id,
                discrepancy_id=discrepancy_id,
                judgment_type=judgment_data.judgment_type,
                title=judgment_data.title,
                description=judgment_data.description,
                context_data=judgment_data.context_data,
                suggested_action=judgment_data.suggested_action,
                priority=judgment_data.priority,
                assigned_to=judgment_data.assigned_to,
                status=JudgmentStatus.PENDING
            )
            
            db.add(judgment)
            db.commit()
            db.refresh(judgment)
            
            # Send notification to assigned user
            if judgment.assigned_to:
                await self._send_judgment_notification(judgment, "new_assignment", db)
            
            # Set up auto-escalation
            await self._schedule_auto_escalation(judgment.id, db)
            
            logger.info(f"Created judgment request {judgment.id} for job {job_id}")
            return judgment
            
        except Exception as e:
            logger.error(f"Failed to create judgment request: {str(e)}")
            db.rollback()
            raise
    
    async def process_judgment_decision(
        self, 
        judgment_id: uuid.UUID, 
        db: Session
    ) -> Dict[str, Any]:
        """Process a human judgment decision"""
        try:
            judgment = db.query(HumanJudgment).filter(
                HumanJudgment.id == judgment_id
            ).first()
            
            if not judgment:
                raise ValueError(f"Judgment {judgment_id} not found")
            
            # Process based on decision
            if judgment.decision == "approve":
                result = await self._process_approval(judgment, db)
            elif judgment.decision == "reject":
                result = await self._process_rejection(judgment, db)
            elif judgment.decision == "modify":
                result = await self._process_modification(judgment, db)
            elif judgment.decision == "escalate":
                result = await self._process_escalation(judgment, db)
            else:
                raise ValueError(f"Unknown decision: {judgment.decision}")
            
            # Update judgment status
            judgment.status = JudgmentStatus.APPROVED if judgment.decision == "approve" else JudgmentStatus.REJECTED
            db.commit()
            
            # Send completion notification
            await self._send_judgment_notification(judgment, "decision_made", db)
            
            logger.info(f"Processed judgment decision {judgment.decision} for judgment {judgment_id}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process judgment decision: {str(e)}")
            db.rollback()
            raise
    
    async def _process_approval(
        self, 
        judgment: HumanJudgment, 
        db: Session
    ) -> Dict[str, Any]:
        """Process approval decision"""
        result = {"action": "approve", "status": "completed"}
        
        # If associated with a discrepancy, resolve it
        if judgment.discrepancy_id:
            discrepancy = db.query(ReconciliationDiscrepancy).filter(
                ReconciliationDiscrepancy.id == judgment.discrepancy_id
            ).first()
            
            if discrepancy:
                discrepancy.status = ReconciliationStatus.COMPLETED
                discrepancy.resolution_notes = f"Approved by human judgment: {judgment.decision_reasoning}"
                discrepancy.resolved_by = judgment.reviewed_by
                discrepancy.resolved_at = datetime.utcnow()
                
                result["discrepancy_resolved"] = True
                result["discrepancy_id"] = discrepancy.id
        
        # If associated with a job, update job status
        if judgment.job_id:
            job = db.query(ReconciliationJob).filter(
                ReconciliationJob.id == judgment.job_id
            ).first()
            
            if job:
                # Check if all judgments for this job are completed
                pending_judgments = db.query(HumanJudgment).filter(
                    HumanJudgment.job_id == job.id,
                    HumanJudgment.status == JudgmentStatus.PENDING
                ).count()
                
                if pending_judgments == 0:
                    job.status = ReconciliationStatus.COMPLETED
                    job.completed_at = datetime.utcnow()
                    result["job_completed"] = True
        
        return result
    
    async def _process_rejection(
        self, 
        judgment: HumanJudgment, 
        db: Session
    ) -> Dict[str, Any]:
        """Process rejection decision"""
        result = {"action": "reject", "status": "completed"}
        
        # If associated with a discrepancy, mark it as rejected
        if judgment.discrepancy_id:
            discrepancy = db.query(ReconciliationDiscrepancy).filter(
                ReconciliationDiscrepancy.id == judgment.discrepancy_id
            ).first()
            
            if discrepancy:
                discrepancy.status = ReconciliationStatus.FAILED
                discrepancy.resolution_notes = f"Rejected by human judgment: {judgment.decision_reasoning}"
                discrepancy.resolved_by = judgment.reviewed_by
                discrepancy.resolved_at = datetime.utcnow()
                
                result["discrepancy_rejected"] = True
                result["discrepancy_id"] = discrepancy.id
        
        return result
    
    async def _process_modification(
        self, 
        judgment: HumanJudgment, 
        db: Session
    ) -> Dict[str, Any]:
        """Process modification decision"""
        result = {"action": "modify", "status": "requires_implementation"}
        
        # Create a new judgment request for the modified approach
        if judgment.alternative_solution:
            new_judgment = HumanJudgment(
                job_id=judgment.job_id,
                discrepancy_id=judgment.discrepancy_id,
                judgment_type="implementation",
                title=f"Modified approach: {judgment.title}",
                description=judgment.alternative_solution,
                context_data=judgment.context_data,
                suggested_action=judgment.alternative_solution,
                priority=judgment.priority,
                status=JudgmentStatus.PENDING
            )
            
            db.add(new_judgment)
            result["new_judgment_created"] = True
            result["new_judgment_id"] = new_judgment.id
        
        return result
    
    async def _process_escalation(
        self, 
        judgment: HumanJudgment, 
        db: Session
    ) -> Dict[str, Any]:
        """Process escalation decision"""
        result = {"action": "escalate", "status": "escalated"}
        
        # Update judgment with escalation details
        judgment.status = JudgmentStatus.ESCALATED
        judgment.escalated_at = datetime.utcnow()
        
        # Send escalation notification
        await self._send_judgment_notification(judgment, "escalated", db)
        
        result["escalated_at"] = judgment.escalated_at
        return result
    
    async def auto_escalate_overdue_judgments(self, db: Session) -> List[uuid.UUID]:
        """Auto-escalate overdue judgment requests"""
        try:
            # Find overdue judgments
            cutoff_time = datetime.utcnow() - timedelta(hours=self.auto_escalation_hours)
            urgent_cutoff = datetime.utcnow() - timedelta(hours=self.urgent_escalation_hours)
            
            overdue_judgments = db.query(HumanJudgment).filter(
                HumanJudgment.status == JudgmentStatus.PENDING,
                HumanJudgment.created_at < cutoff_time
            ).all()
            
            urgent_judgments = db.query(HumanJudgment).filter(
                HumanJudgment.status == JudgmentStatus.PENDING,
                HumanJudgment.priority == "urgent",
                HumanJudgment.created_at < urgent_cutoff
            ).all()
            
            escalated_judgments = []
            
            # Escalate overdue judgments
            for judgment in overdue_judgments:
                judgment.status = JudgmentStatus.ESCALATED
                judgment.escalated_at = datetime.utcnow()
                escalated_judgments.append(judgment.id)
                
                # Send escalation notification
                await self._send_judgment_notification(judgment, "auto_escalated", db)
            
            # Escalate urgent judgments
            for judgment in urgent_judgments:
                if judgment.id not in escalated_judgments:
                    judgment.status = JudgmentStatus.ESCALATED
                    judgment.escalated_at = datetime.utcnow()
                    escalated_judgments.append(judgment.id)
                    
                    # Send urgent escalation notification
                    await self._send_judgment_notification(judgment, "urgent_escalated", db)
            
            if escalated_judgments:
                db.commit()
                logger.info(f"Auto-escalated {len(escalated_judgments)} overdue judgments")
            
            return escalated_judgments
            
        except Exception as e:
            logger.error(f"Failed to auto-escalate judgments: {str(e)}")
            db.rollback()
            return []
    
    async def get_judgment_workload(
        self, 
        user_id: uuid.UUID, 
        db: Session
    ) -> Dict[str, Any]:
        """Get judgment workload for a user"""
        try:
            # Get assigned judgments
            assigned_judgments = db.query(HumanJudgment).filter(
                HumanJudgment.assigned_to == user_id,
                HumanJudgment.status.in_([JudgmentStatus.PENDING, JudgmentStatus.IN_REVIEW])
            ).all()
            
            # Get overdue judgments
            cutoff_time = datetime.utcnow() - timedelta(hours=self.auto_escalation_hours)
            overdue_judgments = [
                j for j in assigned_judgments 
                if j.created_at < cutoff_time
            ]
            
            # Get urgent judgments
            urgent_judgments = [
                j for j in assigned_judgments 
                if j.priority == "urgent"
            ]
            
            return {
                "total_assigned": len(assigned_judgments),
                "overdue": len(overdue_judgments),
                "urgent": len(urgent_judgments),
                "pending": len([j for j in assigned_judgments if j.status == JudgmentStatus.PENDING]),
                "in_review": len([j for j in assigned_judgments if j.status == JudgmentStatus.IN_REVIEW])
            }
            
        except Exception as e:
            logger.error(f"Failed to get judgment workload: {str(e)}")
            return {"error": str(e)}
    
    async def _send_judgment_notification(
        self, 
        judgment: HumanJudgment, 
        notification_type: str, 
        db: Session
    ):
        """Send notification for judgment events"""
        try:
            if judgment.assigned_to:
                await self.notification_service.send_notification(
                    user_id=judgment.assigned_to,
                    notification_type=notification_type,
                    title=f"Judgment Update: {judgment.title}",
                    message=f"Judgment {judgment.id} has been {notification_type}",
                    data={
                        "judgment_id": str(judgment.id),
                        "job_id": str(judgment.job_id),
                        "priority": judgment.priority,
                        "type": notification_type
                    }
                )
        except Exception as e:
            logger.error(f"Failed to send judgment notification: {str(e)}")
    
    async def _schedule_auto_escalation(
        self, 
        judgment_id: uuid.UUID, 
        db: Session
    ):
        """Schedule auto-escalation for judgment request"""
        # In a real implementation, this would use a task queue like Celery
        # For now, we'll rely on the periodic auto-escalation check
        pass
