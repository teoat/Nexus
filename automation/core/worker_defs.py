#!/usr/bin/env python3
"""
WORKER DEFINITIONS
"""
from enum import Enum

class WorkerState(Enum):
    """Worker operational states"""
    INITIALIZING = "initializing"
    IDLE = "idle"
    WORKING = "working"
    PAUSED = "paused"
    ERROR = "error"
    SHUTTING_DOWN = "shutting_down"
    OFFLINE = "offline"

class WorkerType(Enum):
    """Worker type classifications"""
    GENERAL = "general"
    WORKFLOW = "workflow"
    ML = "machine_learning"
    FRONTEND = "frontend"
    BACKEND = "backend"
    MONITORING = "monitoring"
    DATA = "data_processing"
    SECURITY = "security"
    INTEGRATION = "integration"
    TESTING = "testing"
