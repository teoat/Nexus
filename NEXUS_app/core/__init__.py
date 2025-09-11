"""
NEXUS Platform Core Package

This package contains the core system components for the Nexus Platform:
- Docker service management
- Agent system management
- Frontend service management
- API gateway management
- Monitoring system management
- Automation system management
- Performance optimization
- Agent coordination
- Process monitoring
- Meta agent coordination
- Compliance validation
- Collaborative features
- Workflow orchestration
"""

__version__ = "1.0.0"
__author__ = "Nexus Platform Team"

# Core managers
from .docker_manager import DockerManager
from .agent_manager import AgentManager
from .frontend_manager import FrontendManager
from .managers.api_gateway_manager import APIGatewayManager
from .monitoring_manager import MonitoringManager
from .managers.automation_manager import AutomationManager
from .managers.performance_manager import PerformanceManager

# Agent coordination
from .agent_coordinator import AgentCoordinator
from .process_monitor import ProcessMonitor
from .frenly_meta_agent import FrenlyMetaAgent
from .agent_compliance_checker import AgentComplianceChecker

# Advanced features
from .collaborative_agent_system import CollaborativeAgentSystem
from .agent_workflow_orchestrator import AgentWorkflowOrchestrator

# Compliance
from .compliance_validator import ComplianceValidator

__all__ = [
    # Core managers
    "DockerManager",
    "AgentManager", 
    "FrontendManager",
    "APIGatewayManager",
    "MonitoringManager",
    "AutomationManager",
    "PerformanceManager",
    
    # Agent coordination
    "AgentCoordinator",
    "ProcessMonitor",
    "FrenlyMetaAgent",
    "AgentComplianceChecker",
    
    # Advanced features
    "CollaborativeAgentSystem",
    "AgentWorkflowOrchestrator",
    
    # Compliance
    "ComplianceValidator",
]
