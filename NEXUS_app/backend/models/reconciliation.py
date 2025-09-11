#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🔄 Reconciliation & Human Judgment Pydantic Models
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
import uuid

class ReconciliationStatus(str, Enum):
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

class JudgmentStatus(str, Enum):
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

class EvidenceType(str, Enum):
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

# Reconciliation Job Models
class ReconciliationJobCreate(BaseModel):
    """
    ReconciliationJobCreate Class
    
    Reconciliation Job Create
    
    Attributes:
        TBD: Add attribute descriptions
    
    Methods:
        TBD: Add method descriptions
    
    Example:
        TBD: Add usage example
    """
    name: str = Field(..., description="Job name")
    description: Optional[str] = Field(None, description="Job description")
    source_system: str = Field(..., description="Source system identifier")
    target_system: str = Field(..., description="Target system identifier")
    data_type: str = Field(..., description="Type of data being reconciled")
    matching_criteria: Dict[str, Any] = Field(..., description="Criteria for matching records")
    tolerance_threshold: float = Field(0.0, ge=0.0, le=1.0, description="Acceptable variance threshold")
    source_data: Optional[List[Dict[str, Any]]] = Field(None, description="Source data to reconcile")
    target_data: Optional[List[Dict[str, Any]]] = Field(None, description="Target data to reconcile")

class ReconciliationJobUpdate(BaseModel):
    """
    ReconciliationJobUpdate Class
    
    Reconciliation Job Update
    
    Attributes:
        TBD: Add attribute descriptions
    
    Methods:
        TBD: Add method descriptions
    
    Example:
        TBD: Add usage example
    """
    name: Optional[str] = None
    description: Optional[str] = None
    matching_criteria: Optional[Dict[str, Any]] = None
    tolerance_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)

class ReconciliationJobResponse(BaseModel):
    """
    ReconciliationJobResponse Class
    
    Reconciliation Job Response
    
    Attributes:
        TBD: Add attribute descriptions
    
    Methods:
        TBD: Add method descriptions
    
    Example:
        TBD: Add usage example
    """
    id: uuid.UUID
    name: str
    description: Optional[str]
    status: ReconciliationStatus
    source_system: str
    target_system: str
    data_type: str
    matching_criteria: Dict[str, Any]
    tolerance_threshold: float
    total_records: int
    matched_records: int
    unmatched_records: int
    discrepancy_count: int
    confidence_score: float
    created_by: Optional[uuid.UUID]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        """
        Config Class
        
        Config
        
        Attributes:
            TBD: Add attribute descriptions
        
        Methods:
            TBD: Add method descriptions
        
        Example:
            TBD: Add usage example
        """
        from_attributes = True

# Discrepancy Models
class DiscrepancyResponse(BaseModel):
    """
    DiscrepancyResponse Class
    
    Discrepancy Response
    
    Attributes:
        TBD: Add attribute descriptions
    
    Methods:
        TBD: Add method descriptions
    
    Example:
        TBD: Add usage example
    """
    id: uuid.UUID
    job_id: uuid.UUID
    discrepancy_type: str
    severity: str
    description: str
    source_record_id: Optional[str]
    target_record_id: Optional[str]
    source_data: Optional[Dict[str, Any]]
    target_data: Optional[Dict[str, Any]]
    difference_details: Optional[Dict[str, Any]]
    status: ReconciliationStatus
    resolution_notes: Optional[str]
    resolved_by: Optional[uuid.UUID]
    resolved_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        """
        Config Class
        
        Config
        
        Attributes:
            TBD: Add attribute descriptions
        
        Methods:
            TBD: Add method descriptions
        
        Example:
            TBD: Add usage example
        """
        from_attributes = True

# Human Judgment Models
class JudgmentRequest(BaseModel):
    """
    JudgmentRequest Class
    
    Judgment Request
    
    Attributes:
        TBD: Add attribute descriptions
    
    Methods:
        TBD: Add method descriptions
    
    Example:
        TBD: Add usage example
    """
    job_id: uuid.UUID = Field(..., description="Associated reconciliation job ID")
    discrepancy_id: Optional[uuid.UUID] = Field(None, description="Associated discrepancy ID")
    judgment_type: str = Field(..., description="Type of judgment required")
    title: str = Field(..., description="Judgment request title")
    description: str = Field(..., description="Detailed description of the judgment needed")
    context_data: Optional[Dict[str, Any]] = Field(None, description="Additional context data")
    suggested_action: Optional[str] = Field(None, description="AI-suggested action")
    priority: str = Field("medium", description="Priority level")
    assigned_to: Optional[uuid.UUID] = Field(None, description="User assigned to review")

class JudgmentResponse(BaseModel):
    """
    JudgmentResponse Class
    
    Judgment Response
    
    Attributes:
        TBD: Add attribute descriptions
    
    Methods:
        TBD: Add method descriptions
    
    Example:
        TBD: Add usage example
    """
    id: uuid.UUID
    job_id: uuid.UUID
    discrepancy_id: Optional[uuid.UUID]
    judgment_type: str
    status: JudgmentStatus
    priority: str
    title: str
    description: str
    context_data: Optional[Dict[str, Any]]
    suggested_action: Optional[str]
    decision: Optional[str]
    decision_reasoning: Optional[str]
    decision_confidence: Optional[float]
    alternative_solution: Optional[str]
    assigned_to: Optional[uuid.UUID]
    assigned_at: Optional[datetime]
    reviewed_by: Optional[uuid.UUID]
    reviewed_at: Optional[datetime]
    escalated_to: Optional[uuid.UUID]
    escalated_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        """
        Config Class
        
        Config
        
        Attributes:
            TBD: Add attribute descriptions
        
        Methods:
            TBD: Add method descriptions
        
        Example:
            TBD: Add usage example
        """
        from_attributes = True

# Evidence Models
class EvidenceCreate(BaseModel):
    """
    EvidenceCreate Class
    
    Evidence Create
    
    Attributes:
        TBD: Add attribute descriptions
    
    Methods:
        TBD: Add method descriptions
    
    Example:
        TBD: Add usage example
    """
    job_id: uuid.UUID = Field(..., description="Associated reconciliation job ID")
    discrepancy_id: Optional[uuid.UUID] = Field(None, description="Associated discrepancy ID")
    judgment_id: Optional[uuid.UUID] = Field(None, description="Associated judgment ID")
    evidence_type: EvidenceType = Field(..., description="Type of evidence")
    title: str = Field(..., description="Evidence title")
    description: Optional[str] = Field(None, description="Evidence description")
    data: Optional[Dict[str, Any]] = Field(None, description="Structured evidence data")
    file_path: Optional[str] = Field(None, description="Path to evidence file")
    file_hash: Optional[str] = Field(None, description="File hash for integrity")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    mime_type: Optional[str] = Field(None, description="MIME type of file")
    source_system: Optional[str] = Field(None, description="Source system")
    timestamp: Optional[datetime] = Field(None, description="Evidence timestamp")

# Summary and Dashboard Models
class ReconciliationSummary(BaseModel):
    """
    ReconciliationSummary Class
    
    Reconciliation Summary
    
    Attributes:
        TBD: Add attribute descriptions
    
    Methods:
        TBD: Add method descriptions
    
    Example:
        TBD: Add usage example
    """
    job_id: uuid.UUID
    job_name: str
    status: ReconciliationStatus
    total_records: int
    matched_records: int
    unmatched_records: int
    discrepancy_count: int
    confidence_score: float
    total_discrepancies: int
    pending_judgments: int
    completed_judgments: int
    created_at: datetime
    completed_at: Optional[datetime]

class JudgmentDashboard(BaseModel):
    """
    JudgmentDashboard Class
    
    Judgment Dashboard
    
    Attributes:
        TBD: Add attribute descriptions
    
    Methods:
        TBD: Add method descriptions
    
    Example:
        TBD: Add usage example
    """
    total_judgments: int
    pending_judgments: int
    in_review_judgments: int
    completed_judgments: int
    urgent_judgments: int
    my_judgments: int
    recent_judgments: List[JudgmentResponse]

# Reconciliation Engine Models
class ReconciliationResult(BaseModel):
    """
    ReconciliationResult Class
    
    Reconciliation Result
    
    Attributes:
        TBD: Add attribute descriptions
    
    Methods:
        TBD: Add method descriptions
    
    Example:
        TBD: Add usage example
    """
    job_id: uuid.UUID
    total_records: int
    matched_records: int
    unmatched_records: int
    discrepancies: List[DiscrepancyResponse]
    confidence_score: float
    processing_time: float
    requires_human_judgment: bool

class MatchingRule(BaseModel):
    """
    MatchingRule Class
    
    Matching Rule
    
    Attributes:
        TBD: Add attribute descriptions
    
    Methods:
        TBD: Add method descriptions
    
    Example:
        TBD: Add usage example
    """
    field_name: str
    matching_type: str = Field(..., description="exact, fuzzy, numeric, date")
    tolerance: Optional[float] = Field(None, ge=0.0, le=1.0)
    weight: float = Field(1.0, ge=0.0, le=1.0)

class ReconciliationConfig(BaseModel):
    """
    ReconciliationConfig Class
    
    Reconciliation Config
    
    Attributes:
        TBD: Add attribute descriptions
    
    Methods:
        TBD: Add method descriptions
    
    Example:
        TBD: Add usage example
    """
    source_system: str
    target_system: str
    data_type: str
    matching_rules: List[MatchingRule]
    auto_resolve_threshold: float = Field(0.95, ge=0.0, le=1.0)
    escalation_threshold: float = Field(0.7, ge=0.0, le=1.0)
    rejection_threshold: float = Field(0.3, ge=0.0, le=1.0)

# Notification Models
class ReconciliationNotification(BaseModel):
    """
    ReconciliationNotification Class
    
    Reconciliation Notification
    
    Attributes:
        TBD: Add attribute descriptions
    
    Methods:
        TBD: Add method descriptions
    
    Example:
        TBD: Add usage example
    """
    type: str = Field(..., description="notification type")
    job_id: uuid.UUID
    title: str
    message: str
    priority: str = Field("medium", description="low, medium, high, urgent")
    recipients: List[uuid.UUID] = Field(..., description="User IDs to notify")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional notification data")

# Audit and Reporting Models
class ReconciliationAuditEntry(BaseModel):
    """
    ReconciliationAuditEntry Class
    
    Reconciliation Audit Entry
    
    Attributes:
        TBD: Add attribute descriptions
    
    Methods:
        TBD: Add method descriptions
    
    Example:
        TBD: Add usage example
    """
    id: uuid.UUID
    job_id: Optional[uuid.UUID]
    action: str
    entity_type: str
    entity_id: uuid.UUID
    old_values: Optional[Dict[str, Any]]
    new_values: Optional[Dict[str, Any]]
    change_summary: Optional[str]
    performed_by: Optional[uuid.UUID]
    performed_at: datetime
    reason: Optional[str]

    class Config:
        """
        Config Class
        
        Config
        
        Attributes:
            TBD: Add attribute descriptions
        
        Methods:
            TBD: Add method descriptions
        
        Example:
            TBD: Add usage example
        """
        from_attributes = True

class ReconciliationReport(BaseModel):
    """
    ReconciliationReport Class
    
    Reconciliation Report
    
    Attributes:
        TBD: Add attribute descriptions
    
    Methods:
        TBD: Add method descriptions
    
    Example:
        TBD: Add usage example
    """
    job_id: uuid.UUID
    report_type: str
    generated_at: datetime
    generated_by: uuid.UUID
    summary: ReconciliationSummary
    discrepancies: List[DiscrepancyResponse]
    judgments: List[JudgmentResponse]
    evidence: List[Dict[str, Any]]
    recommendations: List[str]
    next_steps: List[str]

# Validation helpers
@validator('tolerance_threshold')
def validate_tolerance_threshold(cls, v):
    """
    Validate Tolerance Threshold
    
    
    Args:
        cls: Description of cls
        v: Description of v

    Example:
        TBD: Add usage example
    """
    if v is not None and (v < 0.0 or v > 1.0):
        raise ValueError('Tolerance threshold must be between 0.0 and 1.0')
    return v

@validator('confidence_score')
def validate_confidence_score(cls, v):
    """
    Validate Confidence Score
    
    
    Args:
        cls: Description of cls
        v: Description of v

    Example:
        TBD: Add usage example
    """
    if v is not None and (v < 0.0 or v > 1.0):
        raise ValueError('Confidence score must be between 0.0 and 1.0')
    return v

@validator('priority')
def validate_priority(cls, v):
    """
    Validate Priority
    
    
    Args:
        cls: Description of cls
        v: Description of v

    Example:
        TBD: Add usage example
    """
    if v not in ['low', 'medium', 'high', 'urgent']:
        raise ValueError('Priority must be one of: low, medium, high, urgent')
    return v

@validator('severity')
def validate_severity(cls, v):
    """
    Validate Severity
    
    
    Args:
        cls: Description of cls
        v: Description of v

    Example:
        TBD: Add usage example
    """
    if v not in ['low', 'medium', 'high', 'critical']:
        raise ValueError('Severity must be one of: low, medium, high, critical')
    return v
