#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
📋 API Models - Nexus Platform
Pydantic models for API request/response validation
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

# ============================================================================
# USER MANAGEMENT MODELS
# ============================================================================

class UserCreate(BaseModel):
    """User creation model"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

class UserUpdate(BaseModel):
    """User update model"""
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class User(BaseModel):
    """User model"""
    id: str
    email: str
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None

class UserProfileResponse(BaseModel):
    """User profile response model"""
    id: str
    email: str
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    preferences: Dict[str, Any] = {}
    subscription: Dict[str, Any] = {}
    usage_stats: Dict[str, Any] = {}

class UserProfileUpdate(BaseModel):
    """User profile update model"""
    full_name: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class UserActivityResponse(BaseModel):
    """User activity response model"""
    id: str
    user_id: str
    action: str
    description: str
    timestamp: datetime
    metadata: Dict[str, Any] = {}

# ============================================================================
# WORKFLOW MANAGEMENT MODELS
# ============================================================================

class WorkflowUpdate(BaseModel):
    """Workflow update model"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class Workflow(BaseModel):
    """Workflow model"""
    id: str
    name: str
    description: Optional[str] = None
    status: str = "draft"
    owner_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

class WorkflowCreate(BaseModel):
    """Workflow creation model"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = "draft"
    config: Optional[Dict[str, Any]] = {}
    steps: Optional[List[Dict[str, Any]]] = []

class WorkflowUpdate(BaseModel):
    """Workflow update model"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    steps: Optional[List[Dict[str, Any]]] = None

class WorkflowResponse(BaseModel):
    """Workflow response model"""
    id: str
    name: str
    description: Optional[str] = None
    status: str
    owner_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    config: Dict[str, Any] = {}
    steps: List[Dict[str, Any]] = []

# ============================================================================
# DATA PROCESSING MODELS
# ============================================================================

class DataProcessingRequest(BaseModel):
    """Data processing request model"""
    data: Union[List[Dict[str, Any]], Dict[str, Any]]
    workflow_id: Optional[str] = None
    processing_options: Optional[Dict[str, Any]] = {}

class DataProcessingResponse(BaseModel):
    """Data processing response model"""
    processing_id: str
    status: str
    input_data: Union[List[Dict[str, Any]], Dict[str, Any]]
    output_data: Dict[str, Any]
    created_at: datetime
    completed_at: Optional[datetime] = None

# ============================================================================
# ANALYTICS MODELS
# ============================================================================

class DashboardAnalyticsResponse(BaseModel):
    """Dashboard analytics response model"""
    total_workflows: int
    active_workflows: int
    completed_tasks: int
    pending_tasks: int
    success_rate: float
    performance_metrics: Dict[str, Any]
    recent_activity: List[Dict[str, Any]]
    chart_data: Dict[str, Any]

class ReportResponse(BaseModel):
    """Report response model"""
    report_id: str
    report_type: str
    format: str
    status: str
    download_url: str
    created_at: datetime
    expires_at: datetime
    metadata: Dict[str, Any] = {}

# ============================================================================
# SYSTEM MODELS
# ============================================================================

class SystemHealthResponse(BaseModel):
    """System health response model"""
    status: str
    timestamp: datetime
    version: str
    uptime: str
    services: Dict[str, Dict[str, Any]]
    metrics: Dict[str, float]

class SystemMetricsResponse(BaseModel):
    """System metrics response model"""
    timestamp: datetime
    performance: Dict[str, Any]
    resource_usage: Dict[str, float]
    database: Dict[str, Any]
    application: Dict[str, Any]

# ============================================================================
# AI AND ML MODELS
# ============================================================================

class AIPredictionRequest(BaseModel):
    """AI prediction request model"""
    model_name: str
    input_data: Dict[str, Any]
    options: Optional[Dict[str, Any]] = {}

class AIPredictionResponse(BaseModel):
    """AI prediction response model"""
    prediction_id: str
    model_name: str
    input_data: Dict[str, Any]
    predictions: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime

class AITrainingRequest(BaseModel):
    """AI training request model"""
    model_name: str
    training_data: List[Dict[str, Any]]
    parameters: Optional[Dict[str, Any]] = {}

class AITrainingResponse(BaseModel):
    """AI training response model"""
    training_id: str
    model_name: str
    status: str
    dataset_size: int
    estimated_duration: str
    created_at: datetime

class AIModelResponse(BaseModel):
    """AI model response model"""
    model_id: str
    name: str
    type: str
    status: str
    accuracy: float
    created_at: datetime
    last_trained: datetime
    metadata: Dict[str, Any]

# ============================================================================
# REAL-TIME MODELS
# ============================================================================

class RealtimeSubscriptionRequest(BaseModel):
    """Real-time subscription request model"""
    channels: List[str]
    filters: Optional[Dict[str, Any]] = {}

class RealtimeSubscriptionResponse(BaseModel):
    """Real-time subscription response model"""
    subscription_id: str
    channels: List[str]
    status: str
    websocket_url: str
    created_at: datetime
    expires_at: datetime

class RealtimePublishRequest(BaseModel):
    """Real-time publish request model"""
    channel: str
    message: Dict[str, Any]
    target_users: Optional[List[str]] = None

class RealtimePublishResponse(BaseModel):
    """Real-time publish response model"""
    message_id: str
    channel: str
    status: str
    subscribers_notified: int
    created_at: datetime

# ============================================================================
# INTEGRATION MODELS
# ============================================================================

class WebhookCreateRequest(BaseModel):
    """Webhook creation request model"""
    name: str
    url: str
    events: List[str]
    secret: Optional[str] = None

class WebhookResponse(BaseModel):
    """Webhook response model"""
    webhook_id: str
    name: str
    url: str
    events: List[str]
    secret: str
    status: str
    created_at: datetime
    last_triggered: Optional[datetime] = None
    trigger_count: int = 0

class ExportRequest(BaseModel):
    """Export request model"""
    format: str
    data_type: str
    filters: Optional[Dict[str, Any]] = {}
    record_count: Optional[int] = None

class ExportResponse(BaseModel):
    """Export response model"""
    export_id: str
    format: str
    status: str
    download_url: str
    created_at: datetime
    estimated_completion: Optional[datetime] = None
    records_count: int

# ============================================================================
# BATCH PROCESSING MODELS
# ============================================================================

class BatchJobCreateRequest(BaseModel):
    """Batch job creation request model"""
    name: str
    type: str
    total_items: int
    parameters: Optional[Dict[str, Any]] = {}

class BatchJobResponse(BaseModel):
    """Batch job response model"""
    job_id: str
    name: str
    type: str
    status: str
    total_items: int
    processed_items: int
    created_at: datetime
    estimated_completion: Optional[datetime] = None

# ============================================================================
# SEARCH MODELS
# ============================================================================

class SearchRequest(BaseModel):
    """Search request model"""
    query: str
    filters: Optional[Dict[str, Any]] = {}
    limit: int = 20
    offset: int = 0

class SearchResult(BaseModel):
    """Search result model"""
    id: str
    type: str
    title: str
    description: str
    relevance_score: float
    created_at: datetime

class SearchResponse(BaseModel):
    """Search response model"""
    query: str
    total_results: int
    results: List[SearchResult]
    facets: Dict[str, Any]
    search_time: str

# ============================================================================
# FILE MANAGEMENT MODELS
# ============================================================================

class FileUploadResponse(BaseModel):
    """File upload response model"""
    file_id: str
    filename: str
    content_type: str
    size: int
    upload_url: str
    created_at: datetime
    expires_at: datetime

class FileInfoResponse(BaseModel):
    """File info response model"""
    file_id: str
    filename: str
    content_type: str
    size: int
    created_at: datetime
    last_accessed: Optional[datetime] = None
    download_url: str
    metadata: Dict[str, Any] = {}

# ============================================================================
# DATA CONVERSION MODELS
# ============================================================================

class DataConversionResponse(BaseModel):
    """Data conversion response model"""
    conversion_id: str
    input_format: str
    output_format: str
    input_size: int
    output_size: int
    records_count: int
    download_url: str
    created_at: datetime

# ============================================================================
# VALIDATION MODELS
# ============================================================================

class ValidationResponse(BaseModel):
    """Validation response model"""
    field: str
    value: str
    is_valid: bool
    errors: List[str] = []
    suggestions: List[str] = []

class DataValidationRequest(BaseModel):
    """Data validation request model"""
    data: List[Dict[str, Any]]
    schema: Dict[str, Any]

class ValidationResult(BaseModel):
    """Validation result model"""
    item_id: str
    is_valid: bool
    errors: List[str] = []

class DataValidationResponse(BaseModel):
    """Data validation response model"""
    validation_id: str
    total_items: int
    valid_items: int
    invalid_items: int
    results: List[ValidationResult]
    created_at: datetime

# ============================================================================
# NOTIFICATION MODELS
# ============================================================================

class NotificationRequest(BaseModel):
    """Notification request model"""
    recipient: str
    type: str
    subject: str
    content: str
    delivery_method: str = "email"

class NotificationResponse(BaseModel):
    """Notification response model"""
    notification_id: str
    recipient: str
    type: str
    status: str
    sent_at: datetime
    delivery_method: str
    metadata: Dict[str, Any] = {}

class NotificationHistoryResponse(BaseModel):
    """Notification history response model"""
    notification_id: str
    recipient: str
    type: str
    status: str
    sent_at: datetime
    read_at: Optional[datetime] = None
    subject: str
    content: str

# ============================================================================
# CONFIGURATION MODELS
# ============================================================================

class ConfigSettingsResponse(BaseModel):
    """Config settings response model"""
    user_settings: Dict[str, Any]
    system_settings: Dict[str, Any]
    feature_flags: Dict[str, bool]

class ConfigSettingsUpdate(BaseModel):
    """Config settings update model"""
    user_settings: Optional[Dict[str, Any]] = None
    system_settings: Optional[Dict[str, Any]] = None
    feature_flags: Optional[Dict[str, bool]] = None

# ============================================================================
# BACKUP MODELS
# ============================================================================

class BackupRequest(BaseModel):
    """Backup request model"""
    name: str
    type: str = "full"
    include_data: bool = True
    include_config: bool = True

class BackupResponse(BaseModel):
    """Backup response model"""
    backup_id: str
    name: str
    type: str
    status: str
    size: str
    download_url: str
    created_at: datetime
    expires_at: datetime

if __name__ == "__main__":
    pass