"""
🤖 AI Service Models
Data models and configurations for AI services in the Nexus Platform.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from enum import Enum
import json
from pathlib import Path

class AIServiceStatus(Enum):
    """AI service status"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    ERROR = "error"
    STOPPED = "stopped"
    MAINTENANCE = "maintenance"

class AIServicePriority(Enum):
    """AI service priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class AIServiceConfig:
    """Configuration for an AI service"""
    name: str
    provider: str
    api_key: Optional[str] = None
    endpoint: Optional[str] = None
    models: List[str] = field(default_factory=list)
    max_concurrent_requests: int = 10
    timeout_seconds: int = 30
    retry_attempts: int = 3
    priority: AIServicePriority = AIServicePriority.MEDIUM
    enabled: bool = True
    cost_per_token: Optional[float] = None
    rate_limit_per_minute: Optional[int] = None

@dataclass
class AIServiceMetrics:
    """Metrics for an AI service"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_tokens_used: int = 0
    total_cost: float = 0.0
    average_response_time: float = 0.0
    last_request_time: Optional[str] = None
    uptime_seconds: int = 0

@dataclass
class AIServiceInstance:
    """Instance of an AI service"""
    config: AIServiceConfig
    status: AIServiceStatus = AIServiceStatus.INITIALIZING
    metrics: AIServiceMetrics = field(default_factory=AIServiceMetrics)
    health_score: float = 0.0
    last_health_check: Optional[str] = None
    error_message: Optional[str] = None

@dataclass
class AIWorkflowStep:
    """Step in an AI workflow"""
    step_id: str
    service_name: str
    model: str
    prompt_template: str
    input_mapping: Dict[str, str]
    output_mapping: Dict[str, str]
    dependencies: List[str] = field(default_factory=list)
    timeout_seconds: int = 30
    retry_on_failure: bool = True

@dataclass
class AIWorkflow:
    """AI workflow definition"""
    workflow_id: str
    name: str
    description: str
    steps: List[AIWorkflowStep]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    max_execution_time: int = 300
    version: str = "1.0.0"
    enabled: bool = True

@dataclass
class AIWorkflowExecution:
    """Execution of an AI workflow"""
    execution_id: str
    workflow_id: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    error_message: Optional[str] = None
    step_results: Dict[str, Any] = field(default_factory=dict)

class AIServiceRegistry:
    """Registry for managing AI services"""
    
    def __init__(self):
        """
          Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        self.services: Dict[str, AIServiceInstance] = {}
        self.workflows: Dict[str, AIWorkflow] = {}
        self.executions: Dict[str, AIWorkflowExecution] = {}
    
    def register_service(self, service: AIServiceInstance) -> bool:
        """Register a new AI service"""
        if service.config.name in self.services:
            return False
        
        self.services[service.config.name] = service
        return True
    
    def get_service(self, name: str) -> Optional[AIServiceInstance]:
        """Get a service by name"""
        return self.services.get(name)
    
    def list_services(self) -> List[str]:
        """List all registered services"""
        return list(self.services.keys())
    
    def get_services_by_provider(self, provider: str) -> List[AIServiceInstance]:
        """Get services by provider"""
        return [
            service for service in self.services.values()
            if service.config.provider == provider
        ]
    
    def get_healthy_services(self) -> List[AIServiceInstance]:
        """Get all healthy services"""
        return [
            service for service in self.services.values()
            if service.status == AIServiceStatus.RUNNING
        ]
    
    def register_workflow(self, workflow: AIWorkflow) -> bool:
        """Register a new workflow"""
        if workflow.workflow_id in self.workflows:
            return False
        
        self.workflows[workflow.workflow_id] = workflow
        return True
    
    def get_workflow(self, workflow_id: str) -> Optional[AIWorkflow]:
        """Get a workflow by ID"""
        return self.workflows.get(workflow_id)
    
    def list_workflows(self) -> List[str]:
        """List all registered workflows"""
        return list(self.workflows.keys())
    
    def create_execution(self, workflow_id: str, input_data: Dict[str, Any]) -> AIWorkflowExecution:
        """Create a new workflow execution"""
        execution = AIWorkflowExecution(
            execution_id=f"exec_{len(self.executions) + 1}",
            workflow_id=workflow_id,
            input_data=input_data
        )
        self.executions[execution.execution_id] = execution
        return execution
    
    def get_execution(self, execution_id: str) -> Optional[AIWorkflowExecution]:
        """Get an execution by ID"""
        return self.executions.get(execution_id)
    
    def update_execution(self, execution_id: str, **kwargs) -> bool:
        """Update an execution"""
        if execution_id not in self.executions:
            return False
        
        execution = self.executions[execution_id]
        for key, value in kwargs.items():
            if hasattr(execution, key):
                setattr(execution, key, value)
        
        return True
