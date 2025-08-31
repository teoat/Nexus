#!/usr/bin/env python3
"""
📋 TASK MANAGER - UNIFIED TASK MANAGEMENT SYSTEM 📋

This module provides unified task management for the consolidated automation system.
It handles task lifecycle, scheduling, dependencies, and execution tracking.

Version: 1.0.0
Status: Production Ready
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import statistics
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    RETRYING = "retrying"

class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    MINIMAL = 1

class TaskType(Enum):
    """Task type classifications"""
    WORKFLOW = "workflow"
    AUTOMATION = "automation"
    ML = "machine_learning"
    FRONTEND = "frontend"
    BACKEND = "backend"
    MONITORING = "monitoring"
    DATA = "data_processing"
    SECURITY = "security"
    INTEGRATION = "integration"
    TESTING = "testing"
    GENERAL = "general"

@dataclass
class TaskDependency:
    """Task dependency definition"""
    task_id: str
    dependency_type: str = "required"
    satisfied: bool = False

@dataclass
class TaskMetrics:
    """Task performance metrics"""
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    retry_count: int = 0
    worker_id: Optional[str] = None
    error_message: Optional[str] = None

@dataclass
class Task:
    """Task instance representation"""
    id: str
    title: str
    description: str
    task_type: TaskType
    priority: TaskPriority
    status: TaskStatus
    dependencies: List[TaskDependency] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    metrics: TaskMetrics = field(default_factory=TaskMetrics)
    timeout_seconds: int = 1800
    max_retries: int = 3
    retry_delay_seconds: int = 60

class TaskManager:
    """
    Unified task management system for the consolidated automation system.
    """
    
    def __init__(self, config_manager):
        """Initialize the task manager"""
        self.config_manager = config_manager
        
        self._tasks: Dict[str, Task] = {}
        self._pending_tasks: Dict[TaskPriority, deque] = {p: deque() for p in TaskPriority}
        self._running_tasks: Dict[str, Task] = {}
        self._completed_tasks: Dict[str, Task] = {}
        self._failed_tasks: Dict[str, Task] = {}
        
        self._dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        self._reverse_dependencies: Dict[str, Set[str]] = defaultdict(set)
        
        self._load_config()
        
        self._task_monitor_task: Optional[asyncio.Task] = None
        self._priority_escalation_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        logger.info("📋 Task Manager initialized")
    
    async def initialize(self):
        """Initialize the task manager"""
        try:
            logger.info("🔄 Initializing Task Manager...")
            await self._start_background_tasks()
            logger.info("✅ Task Manager initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Task Manager initialization failed: {e}")
            raise
    
    def _load_config(self):
        """Load configuration from config manager"""
        self._task_timeout = self.config_manager.get("task.task_timeout", 1800)
        self._retry_attempts = self.config_manager.get("task.retry_attempts", 3)
        self._enable_dependencies = self.config_manager.get("task.enable_dependencies", True)
        self._priority_escalation_threshold_seconds = self.config_manager.get("task.priority_escalation_threshold_seconds", 3600)

    async def create_task(self, title: str, description: str, task_type: TaskType,
                         priority: TaskPriority = TaskPriority.MEDIUM,
                         dependencies: Optional[List[str]] = None,
                         metadata: Optional[Dict[str, Any]] = None,
                         timeout_seconds: Optional[int] = None,
                         max_retries: Optional[int] = None) -> str:
        """Create a new task"""
        task_id = str(uuid.uuid4())

        if self._enable_dependencies and dependencies:
            if self._detect_circular_dependency(task_id, dependencies):
                raise ValueError(f"Circular dependency detected for task {title}")

        task_dependencies = [TaskDependency(dep_id) for dep_id in dependencies or [] if dep_id in self._tasks]

        task = Task(
            id=task_id, title=title, description=description, task_type=task_type,
            priority=priority, status=TaskStatus.PENDING, dependencies=task_dependencies,
            metadata=metadata or {}, timeout_seconds=timeout_seconds or self._task_timeout,
            max_retries=max_retries or self._retry_attempts
        )

        self._tasks[task_id] = task
        self._pending_tasks[priority].append(task_id)

        if self._enable_dependencies and dependencies:
            self._update_dependency_graph(task_id, dependencies)

        logger.info(f"✅ Task created: {title} ({task_id}) with priority {priority.name}")
        return task_id
    
    def _detect_circular_dependency(self, new_task_id: str, dependencies: List[str]) -> bool:
        q = deque(dependencies)
        visited = set(dependencies)
        while q:
            current_dep = q.popleft()
            if current_dep == new_task_id: return True
            if current_dep in self._dependency_graph:
                for upstream_dep in self._dependency_graph[current_dep]:
                    if upstream_dep not in visited:
                        visited.add(upstream_dep)
                        q.append(upstream_dep)
        return False

    def _update_dependency_graph(self, task_id: str, dependencies: List[str]):
        for dep_id in dependencies:
            self._dependency_graph[task_id].add(dep_id)
            self._reverse_dependencies[dep_id].add(task_id)
    
    async def get_pending_tasks(self) -> List[Task]:
        """Get list of ready-to-run tasks, ordered by priority."""
        ready_tasks = []
        for priority in sorted(TaskPriority, key=lambda p: p.value, reverse=True):
            queue = self._pending_tasks[priority]
            # Check tasks in the queue without removing them yet
            for task_id in list(queue):
                task = self._tasks.get(task_id)
                if task and await self._is_task_ready(task):
                    ready_tasks.append(task)
        return ready_tasks
    
    async def _is_task_ready(self, task: Task) -> bool:
        if not self._enable_dependencies or not task.dependencies: return True
        for dep in task.dependencies:
            if dep.dependency_type == "required":
                dep_task = self._tasks.get(dep.task_id)
                if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                    return False
        return True
    
    async def start_task(self, task_id: str, worker_id: str) -> bool:
        task = self._tasks.get(task_id)
        if not task or task.status != TaskStatus.PENDING or not await self._is_task_ready(task):
            return False
        
        task.status = TaskStatus.RUNNING
        task.metrics.started_at = datetime.now()
        task.metrics.worker_id = worker_id
        
        self._pending_tasks[task.priority].remove(task_id)
        self._running_tasks[task_id] = task
        
        logger.info(f"✅ Task started: {task.title} ({task_id}) on worker {worker_id}")
        return True
    
    async def complete_task(self, task_id: str, success: bool = True, error_message: Optional[str] = None) -> bool:
        task = self._tasks.get(task_id)
        if not task or task.status != TaskStatus.RUNNING: return False

        if task_id in self._running_tasks: del self._running_tasks[task_id]

        if success:
            task.status = TaskStatus.COMPLETED
            task.metrics.completed_at = datetime.now()
            if task.metrics.started_at:
                task.metrics.duration_seconds = (task.metrics.completed_at - task.metrics.started_at).total_seconds()
            self._completed_tasks[task_id] = task
            logger.info(f"✅ Task completed: {task.title} ({task_id})")
        else:
            if task.metrics.retry_count < task.max_retries:
                task.status = TaskStatus.RETRYING
                task.metrics.retry_count += 1
                self._pending_tasks[task.priority].append(task_id)
                logger.warning(f"🔄 Task failed, retrying: {task.title} ({task_id})")
            else:
                task.status = TaskStatus.FAILED
                task.metrics.error_message = error_message
                self._failed_tasks[task_id] = task
                logger.error(f"❌ Task failed permanently: {task.title} ({task_id})")
        
        await self._resolve_dependencies(task_id)
        return True
    
    async def _resolve_dependencies(self, completed_task_id: str):
        if completed_task_id in self._reverse_dependencies:
            for dep_task_id in self._reverse_dependencies[completed_task_id]:
                if dep_task := self._tasks.get(dep_task_id):
                    for dep in dep_task.dependencies:
                        if dep.task_id == completed_task_id:
                            dep.satisfied = True
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        return asdict(self._tasks[task_id]) if task_id in self._tasks else None
    
    async def _start_background_tasks(self):
        self._task_monitor_task = asyncio.create_task(self._task_monitoring_loop())
        self._priority_escalation_task = asyncio.create_task(self._priority_escalation_loop())
    
    async def _task_monitoring_loop(self):
        while not self._shutdown_event.is_set():
            try:
                for task_id, task in list(self._running_tasks.items()):
                    if task.metrics.started_at and (datetime.now() - task.metrics.started_at).total_seconds() > task.timeout_seconds:
                        logger.warning(f"Task {task_id} timed out.")
                        await self.complete_task(task_id, success=False, error_message="Task execution timeout")
                await asyncio.sleep(30)
            except asyncio.CancelledError: break
            except Exception as e: logger.error(f"Error in task monitoring loop: {e}", exc_info=True)

    async def _priority_escalation_loop(self):
        """Periodically escalate priority of old pending tasks."""
        while not self._shutdown_event.is_set():
            try:
                await asyncio.sleep(self._priority_escalation_threshold_seconds / 2) # Check periodically
                now = datetime.now()
                for priority in sorted(TaskPriority, key=lambda p: p.value):
                    if priority == TaskPriority.CRITICAL: continue # Cannot escalate further

                    queue = self._pending_tasks[priority]
                    for task_id in list(queue):
                        task = self._tasks.get(task_id)
                        if task and (now - task.metrics.created_at).total_seconds() > self._priority_escalation_threshold_seconds:
                            new_priority_val = min(TaskPriority.CRITICAL.value, priority.value + 1)
                            new_priority = TaskPriority(new_priority_val)

                            task.priority = new_priority
                            queue.remove(task_id)
                            self._pending_tasks[new_priority].append(task_id)
                            logger.info(f"Escalated task {task.title} ({task.id}) to {new_priority.name}")

            except asyncio.CancelledError: break
            except Exception as e: logger.error(f"Error in priority escalation loop: {e}", exc_info=True)

    async def shutdown(self):
        logger.info("🔄 Shutting down Task Manager...")
        self._shutdown_event.set()
        if self._task_monitor_task: self._task_monitor_task.cancel()
        if self._priority_escalation_task: self._priority_escalation_task.cancel()
        logger.info("✅ Task Manager shutdown completed")
