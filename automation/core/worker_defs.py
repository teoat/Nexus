#!/usr/bin/env python3
"""
WORKER DEFINITIONS
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class WorkerCapability:
    """Worker capability definition"""
    name: str
    version: str
    supported_task_types: List[str]
    max_concurrent_tasks: int
    performance_score: float = 1.0
    reliability_score: float = 1.0

@dataclass
class WorkerMetrics:
    """Worker performance metrics"""
    total_tasks_processed: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    average_task_duration: float = 0.0
    last_task_time: Optional[datetime] = None
    uptime_seconds: int = 0
    last_updated: Optional[datetime] = None


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
