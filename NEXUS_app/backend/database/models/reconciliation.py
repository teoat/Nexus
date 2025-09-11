#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🔄 Reconciliation & Human Judgment System Models
"""

from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey, Integer, Float, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from enum import Enum as PyEnum

from ..config import Base

class ReconciliationStatus(PyEnum):
    """
    ReconciliationStatus Class
    
    Reconciliation Status
    
    Attributes:
        TBD: Add attribute descriptions
    
    Methods:
        TBD: Add method descriptions
    
    Example:
        TBD: Add usage example
    """
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REQUIRES_HUMAN_JUDGMENT = "requires_human_judgment"
    ESCALATED = "escalated"

class JudgmentStatus(PyEnum):
    """
    JudgmentStatus Class
    
    Judgment Status
    
    Attributes:
        TBD: Add attribute descriptions
    
    Methods:
        TBD: Add method descriptions
    
    Example:
        TBD: Add usage example
    """
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"

class EvidenceType(PyEnum):
    """
    EvidenceType Class
    
    Evidence Type
    
    Attributes:
        TBD: Add attribute descriptions
    
    Methods:
        TBD: Add method descriptions
    
    Example:
        TBD: Add usage example
    """
    TRANSACTION_LOG = "transaction_log"
    AUDIT_TRAIL = "audit_trail"
    SYSTEM_LOG = "system_log"
    USER_ACTION = "user_action"
    API_CALL = "api_call"
    DATABASE_CHANGE = "database_change"
    FILE_UPLOAD = "file_upload"
    EMAIL = "email"
    DOCUMENT = "document"

class ReconciliationJob(Base):
    """Main reconciliation job that processes data discrepancies"""
    __tablename__ = "reconciliation_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(Enum(ReconciliationStatus), default=ReconciliationStatus.PENDING)
    
    # Data sources and targets
    source_system = Column(String(100), nullable=False)
    target_system = Column(String(100), nullable=False)
    data_type = Column(String(100), nullable=False)  # transactions, users, orders, etc.
    
    # Reconciliation criteria
    matching_criteria = Column(JSON)  # Rules for matching records
    tolerance_threshold = Column(Float, default=0.0)  # Acceptable variance
    
    # Results
    total_records = Column(Integer, default=0)
    matched_records = Column(Integer, default=0)
    unmatched_records = Column(Integer, default=0)
    discrepancy_count = Column(Integer, default=0)
    confidence_score = Column(Float, default=0.0)
    
    # Metadata
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    discrepancies = relationship("ReconciliationDiscrepancy", back_populates="job")
    judgments = relationship("HumanJudgment", back_populates="job")
    evidence = relationship("Evidence", back_populates="job")

class ReconciliationDiscrepancy(Base):
    """Individual discrepancies found during reconciliation"""
    __tablename__ = "reconciliation_discrepancies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("reconciliation_jobs.id"), nullable=False)
    
    # Discrepancy details
    discrepancy_type = Column(String(100), nullable=False)  # missing, extra, mismatch, etc.
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    description = Column(Text, nullable=False)
    
    # Data involved
    source_record_id = Column(String(255))
    target_record_id = Column(String(255))
    source_data = Column(JSON)
    target_data = Column(JSON)
    difference_details = Column(JSON)
    
    # Resolution
    status = Column(Enum(ReconciliationStatus), default=ReconciliationStatus.PENDING)
    resolution_notes = Column(Text)
    resolved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    resolved_at = Column(DateTime(timezone=True))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    job = relationship("ReconciliationJob", back_populates="discrepancies")
    judgments = relationship("HumanJudgment", back_populates="discrepancy")
    evidence = relationship("Evidence", back_populates="discrepancy")

class HumanJudgment(Base):
    """Human judgment requests and decisions"""
    __tablename__ = "human_judgments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("reconciliation_jobs.id"), nullable=False)
    discrepancy_id = Column(UUID(as_uuid=True), ForeignKey("reconciliation_discrepancies.id"))
    
    # Judgment details
    judgment_type = Column(String(100), nullable=False)  # approve, reject, escalate, modify
    status = Column(Enum(JudgmentStatus), default=JudgmentStatus.PENDING)
    priority = Column(String(20), default="medium")  # low, medium, high, urgent
    
    # Request details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    context_data = Column(JSON)  # Additional context for human reviewer
    suggested_action = Column(Text)  # AI-suggested action
    
    # Human decision
    decision = Column(String(100))  # approve, reject, modify, escalate
    decision_reasoning = Column(Text)
    decision_confidence = Column(Float)  # Human's confidence in their decision
    alternative_solution = Column(Text)  # If human suggests different approach
    
    # Assignment and workflow
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    assigned_at = Column(DateTime(timezone=True))
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    reviewed_at = Column(DateTime(timezone=True))
    escalated_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    escalated_at = Column(DateTime(timezone=True))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    job = relationship("ReconciliationJob", back_populates="judgments")
    discrepancy = relationship("ReconciliationDiscrepancy", back_populates="judgments")
    evidence = relationship("Evidence", back_populates="judgment")

class Evidence(Base):
    """Evidence and supporting documentation for reconciliation"""
    __tablename__ = "evidence"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("reconciliation_jobs.id"), nullable=False)
    discrepancy_id = Column(UUID(as_uuid=True), ForeignKey("reconciliation_discrepancies.id"))
    judgment_id = Column(UUID(as_uuid=True), ForeignKey("human_judgments.id"))
    
    # Evidence details
    evidence_type = Column(Enum(EvidenceType), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Data and files
    data = Column(JSON)  # Structured evidence data
    file_path = Column(String(500))  # Path to file evidence
    file_hash = Column(String(64))  # SHA-256 hash for integrity
    file_size = Column(Integer)
    mime_type = Column(String(100))
    
    # Metadata
    source_system = Column(String(100))
    timestamp = Column(DateTime(timezone=True))
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    job = relationship("ReconciliationJob", back_populates="evidence")
    discrepancy = relationship("ReconciliationDiscrepancy", back_populates="evidence")
    judgment = relationship("HumanJudgment", back_populates="evidence")

class ReconciliationRule(Base):
    """Rules and policies for automated reconciliation"""
    __tablename__ = "reconciliation_rules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Rule configuration
    source_system = Column(String(100), nullable=False)
    target_system = Column(String(100), nullable=False)
    data_type = Column(String(100), nullable=False)
    
    # Matching criteria
    matching_fields = Column(JSON)  # Fields to match on
    matching_algorithm = Column(String(100), default="exact")  # exact, fuzzy, custom
    tolerance_settings = Column(JSON)  # Tolerance for different field types
    
    # Action rules
    auto_resolve_threshold = Column(Float, default=0.95)  # Confidence threshold for auto-resolution
    escalation_threshold = Column(Float, default=0.7)  # Threshold for human escalation
    rejection_threshold = Column(Float, default=0.3)  # Threshold for auto-rejection
    
    # Status and metadata
    is_active = Column(Boolean, default=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ReconciliationAuditLog(Base):
    """Audit trail for all reconciliation activities"""
    __tablename__ = "reconciliation_audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("reconciliation_jobs.id"))
    discrepancy_id = Column(UUID(as_uuid=True), ForeignKey("reconciliation_discrepancies.id"))
    judgment_id = Column(UUID(as_uuid=True), ForeignKey("human_judgments.id"))
    
    # Action details
    action = Column(String(100), nullable=False)  # created, updated, resolved, escalated, etc.
    entity_type = Column(String(50), nullable=False)  # job, discrepancy, judgment, evidence
    entity_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Changes
    old_values = Column(JSON)
    new_values = Column(JSON)
    change_summary = Column(Text)
    
    # Actor and context
    performed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    performed_at = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Additional context
    reason = Column(Text)
    metadata = Column(JSON)
