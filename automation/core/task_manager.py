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
    dependency_type: str = "required"  # required, optional, parallel
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
    complexity: int = 1 # Default complexity
    dependencies: List[TaskDependency] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    metrics: TaskMetrics = field(default_factory=TaskMetrics)
    timeout_seconds: int = 1800  # 30 minutes default
    max_retries: int = 3
    retry_delay_seconds: int = 60

class TaskManager:
    """
    Unified task management system for the consolidated automation system.
    
    This class provides:
    - Task lifecycle management (create, schedule, execute, complete)
    - Priority-based scheduling
    - Dependency management and resolution
    - Task execution tracking and metrics
    - Performance optimization and load balancing
    """
    
    def __init__(self, config_manager, alert_manager=None):
        """Initialize the task manager"""
        self.config_manager = config_manager
        self.alert_manager = alert_manager
        
        # Task storage
        self._tasks: Dict[str, Task] = {}
        self._pending_tasks: deque = deque()
        self._running_tasks: Dict[str, Task] = {}
        self._completed_tasks: Dict[str, Task] = {}
        self._failed_tasks: Dict[str, Task] = {}
        
        # Task organization
        self._tasks_by_type: Dict[TaskType, List[str]] = {tt: [] for tt in TaskType}
        self._tasks_by_priority: Dict[TaskPriority, List[str]] = {tp: [] for tp in TaskPriority}
        self._tasks_by_status: Dict[TaskStatus, List[str]] = {ts: [] for ts in TaskStatus}
        
        # Dependency tracking
        self._dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        self._reverse_dependencies: Dict[str, Set[str]] = defaultdict(set)
        
        # Performance tracking
        self._performance_history: List[float] = []
        self._throughput_history: List[float] = []
        self._last_optimization: Optional[datetime] = None
        
        # Configuration
        self._max_concurrent_tasks: int = 50
        self._task_timeout: int = 1800
        self._retry_attempts: int = 3
        self._retry_delay: int = 60
        self._enable_dependencies: bool = True
        self._max_dependency_depth: int = 10
        
        # Background tasks
        self._task_monitor_task: Optional[asyncio.Task] = None
        self._dependency_resolver_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        logger.info("📋 Task Manager initialized")
    
    async def initialize(self):
        """Initialize the task manager"""
        try:
            logger.info("🔄 Initializing Task Manager...")
            
            # Load configuration
            self._load_config()
            
            # Start background tasks
            await self._start_background_tasks()
            
            logger.info("✅ Task Manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Task Manager initialization failed: {e}")
            raise
    
    def _load_config(self):
        """Load configuration from config manager"""
        try:
            self._max_concurrent_tasks = self.config_manager.get("task.max_concurrent_tasks", 50)
            self._task_timeout = self.config_manager.get("task.task_timeout", 1800)
            self._retry_attempts = self.config_manager.get("task.retry_attempts", 3)
            self._retry_delay = self.config_manager.get("task.retry_delay", 60)
            self._enable_dependencies = self.config_manager.get("task.enable_dependencies", True)
            self._max_dependency_depth = self.config_manager.get("task.max_dependency_depth", 10)
            
            logger.debug("Task configuration loaded")
            
        except Exception as e:
            logger.warning(f"Error loading task configuration: {e}")
            logger.info("Using default task configuration")
    
    def _assess_complexity(self, task_type: TaskType, metadata: Dict[str, Any]) -> int:
        """Assess the complexity of a task."""
        complexity_map = {
            TaskType.ML: 5,
            TaskType.DATA: 4,
            TaskType.WORKFLOW: 3,
            TaskType.BACKEND: 2,
            TaskType.INTEGRATION: 2,
            TaskType.FRONTEND: 2,
            TaskType.SECURITY: 3,
            TaskType.MONITORING: 1,
            TaskType.TESTING: 1,
            TaskType.GENERAL: 1,
        }
        return complexity_map.get(task_type, 1)

    async def create_task(self, title: str, description: str, task_type: TaskType,
                         priority: TaskPriority = TaskPriority.MEDIUM,
                         dependencies: Optional[List[str]] = None,
                         metadata: Optional[Dict[str, Any]] = None,
                         timeout_seconds: Optional[int] = None,
                         max_retries: Optional[int] = None) -> str:
        """Create a new task"""
        try:
            task_id = str(uuid.uuid4())
            
            # Create task dependencies
            task_dependencies = []
            if dependencies and self._enable_dependencies:
                for dep_id in dependencies:
                    if dep_id in self._tasks:
                        task_dependencies.append(TaskDependency(task_id=dep_id))
                    else:
                        logger.warning(f"Dependency task {dep_id} not found, ignoring")

            # Assess complexity
            complexity = self._assess_complexity(task_type, metadata or {})
            
            # Create task
            task = Task(
                id=task_id,
                title=title,
                description=description,
                task_type=task_type,
                priority=priority,
                status=TaskStatus.PENDING,
                complexity=complexity,
                dependencies=task_dependencies,
                metadata=metadata or {},
                timeout_seconds=timeout_seconds or self._task_timeout,
                max_retries=max_retries or self._retry_attempts
            )
            
            # Add to storage
            self._tasks[task_id] = task
            self._tasks_by_type[task_type].append(task_id)
            self._tasks_by_priority[priority].append(task_id)
            self._tasks_by_status[TaskStatus.PENDING].append(task_id)
            
            # Add to pending queue
            self._pending_tasks.append(task_id)
            
            # Update dependency graph
            if task_dependencies:
                self._update_dependency_graph(task_id, [dep.task_id for dep in task_dependencies])
            
            logger.info(f"✅ Task created: {title} ({task_id})")
            return task_id
            
        except Exception as e:
            logger.error(f"Error creating task {title}: {e}")
            raise
    
    def _update_dependency_graph(self, task_id: str, dependencies: List[str]):
        """Update dependency graph for a task"""
        try:
            # Add dependencies
            for dep_id in dependencies:
                self._dependency_graph[task_id].add(dep_id)
                self._reverse_dependencies[dep_id].add(task_id)
            
            logger.debug(f"Dependency graph updated for task {task_id}")
            
        except Exception as e:
            logger.error(f"Error updating dependency graph: {e}")
    
    async def get_pending_tasks(self) -> List[Task]:
        """Get list of pending tasks that are ready for execution"""
        try:
            ready_tasks = []
            
            for task_id in list(self._pending_tasks):
                task = self._tasks.get(task_id)
                if not task:
                    continue
                
                # Check if task is ready (all dependencies satisfied)
                if await self._is_task_ready(task):
                    ready_tasks.append(task)
            
            # Sort by priority (highest first)
            ready_tasks.sort(key=lambda t: t.priority.value, reverse=True)
            
            return ready_tasks
            
        except Exception as e:
            logger.error(f"Error getting pending tasks: {e}")
            return []
    
    async def _is_task_ready(self, task: Task) -> bool:
        """Check if a task is ready for execution"""
        try:
            if not task.dependencies:
                return True
            
            for dependency in task.dependencies:
                dep_task = self._tasks.get(dependency.task_id)
                if not dep_task:
                    logger.warning(f"Dependency task {dependency.task_id} not found")
                    return False
                
                if dep_task.status != TaskStatus.COMPLETED:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking task readiness: {e}")
            return False
    
    async def start_task(self, task_id: str, worker_id: str) -> bool:
        """Start a task execution"""
        try:
            if task_id not in self._tasks:
                logger.error(f"Task not found: {task_id}")
                return False
            
            task = self._tasks[task_id]
            
            if task.status != TaskStatus.PENDING:
                logger.warning(f"Task {task_id} is not pending (status: {task.status.value})")
                return False
            
            # Check if task is ready
            if not await self._is_task_ready(task):
                logger.warning(f"Task {task_id} is not ready for execution")
                return False
            
            # Update task status
            task.status = TaskStatus.RUNNING
            task.metrics.started_at = datetime.now()
            task.metrics.worker_id = worker_id
            
            # Move to running tasks
            if task_id in self._pending_tasks:
                self._pending_tasks.remove(task_id)
            if task_id in self._tasks_by_status[TaskStatus.PENDING]:
                self._tasks_by_status[TaskStatus.PENDING].remove(task_id)
            
            self._running_tasks[task_id] = task
            self._tasks_by_status[TaskStatus.RUNNING].append(task_id)
            
            logger.info(f"✅ Task started: {task.title} ({task_id}) on worker {worker_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting task {task_id}: {e}")
            return False
    
    async def complete_task(self, task_id: str, success: bool = True, 
                           error_message: Optional[str] = None) -> bool:
        """Mark a task as completed"""
        try:
            if task_id not in self._tasks:
                logger.error(f"Task not found: {task_id}")
                return False
            
            task = self._tasks[task_id]
            
            if task.status != TaskStatus.RUNNING:
                logger.warning(f"Task {task_id} is not running (status: {task.status.value})")
                return False
            
            # Update task status
            if success:
                task.status = TaskStatus.COMPLETED
                task.metrics.completed_at = datetime.now()
                
                # Calculate duration
                if task.metrics.started_at:
                    duration = (task.metrics.completed_at - task.metrics.started_at).total_seconds()
                    task.metrics.duration_seconds = duration
                
                # Move to completed tasks
                self._completed_tasks[task_id] = task
                self._tasks_by_status[TaskStatus.COMPLETED].append(task_id)
                
                logger.info(f"✅ Task completed: {task.title} ({task_id})")
                
            else:
                # Handle task failure
                if task.metrics.retry_count < task.max_retries:
                    task.status = TaskStatus.RETRYING
                    task.metrics.retry_count += 1
                    
                    # Add back to pending queue for retry
                    self._pending_tasks.append(task_id)
                    self._tasks_by_status[TaskStatus.PENDING].append(task_id)
                    
                    logger.warning(f"🔄 Task failed, retrying: {task.title} ({task_id}) - Attempt {task.metrics.retry_count}")
                    
                else:
                    task.status = TaskStatus.FAILED
                    task.metrics.error_message = error_message
                    
                    # Move to failed tasks
                    self._failed_tasks[task_id] = task
                    self._tasks_by_status[TaskStatus.FAILED].append(task_id)
                    
                    logger.error(f"❌ Task failed permanently: {task.title} ({task_id})")

                    if self.alert_manager:
                        await self.alert_manager.send_alert(
                            "critical",
                            f"Task Failed Permanently: {task.title}",
                            f"Task {task.id} failed after {task.max_retries} retries. Error: {error_message}"
                        )
            
            # Remove from running tasks
            if task_id in self._running_tasks:
                del self._running_tasks[task_id]
            if task_id in self._tasks_by_status[TaskStatus.RUNNING]:
                self._tasks_by_status[TaskStatus.RUNNING].remove(task_id)
            
            # Resolve dependencies for dependent tasks
            await self._resolve_dependencies(task_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error completing task {task_id}: {e}")
            return False
    
    async def _resolve_dependencies(self, completed_task_id: str):
        """Resolve dependencies for tasks that depend on the completed task"""
        try:
            # Find tasks that depend on this completed task
            dependent_tasks = self._reverse_dependencies.get(completed_task_id, set())
            
            for dep_task_id in dependent_tasks:
                dep_task = self._tasks.get(dep_task_id)
                if not dep_task:
                    continue
                
                # Mark dependency as satisfied
                for dependency in dep_task.dependencies:
                    if dependency.task_id == completed_task_id:
                        dependency.satisfied = True
                        break
                
                # Check if all dependencies are now satisfied
                if await self._is_task_ready(dep_task):
                    logger.debug(f"All dependencies satisfied for task {dep_task_id}")
            
        except Exception as e:
            logger.error(f"Error resolving dependencies: {e}")
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed status of a specific task"""
        if task_id not in self._tasks:
            return None
        
        task = self._tasks[task_id]
        
        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "type": task.task_type.value,
            "priority": task.priority.value,
            "status": task.status.value,
            "complexity": task.complexity,
            "dependencies": [asdict(dep) for dep in task.dependencies],
            "metadata": task.metadata,
            "metrics": asdict(task.metrics),
            "timeout_seconds": task.timeout_seconds,
            "max_retries": task.max_retries,
            "retry_delay_seconds": task.retry_delay_seconds
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get overall task manager status"""
        return {
            "total_tasks": len(self._tasks),
            "pending_tasks": len(self._pending_tasks),
            "running_tasks": len(self._running_tasks),
            "completed_tasks": len(self._completed_tasks),
            "failed_tasks": len(self._failed_tasks),
            "tasks_by_type": {tt.value: len(task_ids) for tt, task_ids in self._tasks_by_type.items()},
            "tasks_by_priority": {tp.value: len(task_ids) for tp, task_ids in self._tasks_by_priority.items()},
            "tasks_by_status": {ts.value: len(task_ids) for ts, task_ids in self._tasks_by_status.items()},
            "max_concurrent_tasks": self._max_concurrent_tasks,
            "enable_dependencies": self._enable_dependencies
        }
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get task statistics"""
        if not self._tasks:
            return {
                "total_processed": 0,
                "successful": 0,
                "failed": 0,
                "average_duration": 0.0,
                "throughput_rate": 0.0
            }
        
        total_processed = len(self._completed_tasks) + len(self._failed_tasks)
        successful = len(self._completed_tasks)
        failed = len(self._failed_tasks)
        
        # Calculate average duration
        durations = [task.metrics.duration_seconds for task in self._completed_tasks.values() 
                    if task.metrics.duration_seconds > 0]
        average_duration = statistics.mean(durations) if durations else 0.0
        
        # Calculate throughput rate (tasks per minute)
        if self._tasks:
            oldest_task = min(self._tasks.values(), key=lambda t: t.metrics.created_at)
            time_span = (datetime.now() - oldest_task.metrics.created_at).total_seconds() / 60  # minutes
            throughput_rate = total_processed / time_span if time_span > 0 else 0.0
        else:
            throughput_rate = 0.0
        
        return {
            "total_processed": total_processed,
            "successful": successful,
            "failed": failed,
            "average_duration": average_duration,
            "throughput_rate": throughput_rate
        }
    
    async def get_health_status(self) -> float:
        """Get overall task manager health status (0.0 to 1.0)"""
        if not self._tasks:
            return 1.0
        
        total_tasks = len(self._tasks)
        failed_tasks = len(self._failed_tasks)
        
        if total_tasks == 0:
            return 1.0
        
        success_rate = (total_tasks - failed_tasks) / total_tasks
        return max(0.0, min(1.0, success_rate))
    
    async def get_throughput_rate(self) -> float:
        """Get task throughput rate (tasks per minute)"""
        stats = await self.get_statistics()
        return stats.get("throughput_rate", 0.0)
    
    async def get_error_rate(self) -> float:
        """Get task error rate (0.0 to 1.0)"""
        if not self._tasks:
            return 0.0
        
        total_tasks = len(self._tasks)
        failed_tasks = len(self._failed_tasks)
        
        if total_tasks == 0:
            return 0.0
        
        return failed_tasks / total_tasks
    
    async def optimize_scheduling(self):
        """Optimize task scheduling based on current performance"""
        try:
            logger.debug("🔄 Starting task scheduling optimization...")
            
            # Get current performance metrics
            current_throughput = await self.get_throughput_rate()
            current_error_rate = await self.get_error_rate()
            
            # Store performance history
            self._throughput_history.append(current_throughput)
            if len(self._throughput_history) > 100:  # Keep last 100 measurements
                self._throughput_history.pop(0)
            
            # Calculate performance score
            if self._throughput_history:
                avg_throughput = statistics.mean(self._throughput_history)
                performance_score = min(1.0, avg_throughput / 10.0)  # Normalize to 0-1
            else:
                performance_score = 1.0
            
            # Store performance history
            self._performance_history.append(performance_score)
            if len(self._performance_history) > 100:
                self._performance_history.pop(0)
            
            self._last_optimization = datetime.now()
            
            logger.debug(f"Task scheduling optimization completed. Performance score: {performance_score:.2f}")
            
        except Exception as e:
            logger.error(f"Error during task scheduling optimization: {e}")
    
    async def _start_background_tasks(self):
        """Start background monitoring and optimization tasks"""
        logger.info("🔄 Starting background tasks...")
        
        # Task monitoring task
        self._task_monitor_task = asyncio.create_task(self._task_monitoring_loop())
        
        # Dependency resolver task
        self._dependency_resolver_task = asyncio.create_task(self._dependency_resolution_loop())
        
        logger.info("✅ Background tasks started successfully")
    
    async def _task_monitoring_loop(self):
        """Background task monitoring loop"""
        while not self._shutdown_event.is_set():
            try:
                await self._monitor_running_tasks()
                await asyncio.sleep(30)  # Check every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in task monitoring loop: {e}")
                await asyncio.sleep(10)
    
    async def _dependency_resolution_loop(self):
        """Background dependency resolution loop"""
        while not self._shutdown_event.is_set():
            try:
                await self._resolve_pending_dependencies()
                await asyncio.sleep(10)  # Check every 10 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in dependency resolution loop: {e}")
                await asyncio.sleep(10)
    
    async def _monitor_running_tasks(self):
        """Monitor running tasks for timeouts and issues"""
        try:
            current_time = datetime.now()
            
            for task_id, task in list(self._running_tasks.items()):
                # Check for timeout
                if (task.metrics.started_at and 
                    (current_time - task.metrics.started_at).total_seconds() > task.timeout_seconds):
                    logger.warning(f"Task {task_id} timed out, marking as failed")
                    await self.complete_task(task_id, success=False, 
                                          error_message="Task execution timeout")
            
        except Exception as e:
            logger.error(f"Error monitoring running tasks: {e}")
    
    async def _resolve_pending_dependencies(self):
        """Resolve pending dependencies for tasks"""
        try:
            for task_id in list(self._pending_tasks):
                task = self._tasks.get(task_id)
                if not task:
                    continue

                if await self._is_task_ready(task):
                    logger.debug(f"Task {task_id} is now ready to be scheduled.")

        except Exception as e:
            logger.error(f"Error resolving pending dependencies: {e}")
    
    async def shutdown(self):
        """Shutdown the task manager"""
        try:
            logger.info("🔄 Shutting down Task Manager...")
            
            self._shutdown_event.set()
            
            # Cancel background tasks
            if self._task_monitor_task:
                self._task_monitor_task.cancel()
            if self._dependency_resolver_task:
                self._dependency_resolver_task.cancel()
            
            # Wait for tasks to complete (handle cancellation gracefully)
            if self._task_monitor_task:
                try:
                    await self._task_monitor_task
                except asyncio.CancelledError:
                    pass
            if self._dependency_resolver_task:
                try:
                    await self._dependency_resolver_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("✅ Task Manager shutdown completed")
            
        except Exception as e:
            logger.error(f"❌ Task Manager shutdown failed: {e}")


# Main entry point for testing
async def main():
    """Main entry point for testing the task manager"""
    # Create a mock config manager for testing
    class MockConfigManager:
        def get(self, key, default=None):
            config = {
                "task.max_concurrent_tasks": 50,
                "task.task_timeout": 1800,
                "task.retry_attempts": 3,
                "task.retry_delay": 60,
                "task.enable_dependencies": True,
                "task.max_dependency_depth": 10
            }
            return config.get(key, default)
    
    config_manager = MockConfigManager()
    task_manager = TaskManager(config_manager)
    
    try:
        await task_manager.initialize()
        
        # Test task creation
        task_id = await task_manager.create_task(
            title="Test Task",
            description="A test task for the task manager",
            task_type=TaskType.GENERAL,
            priority=TaskPriority.MEDIUM
        )
        
        print(f"Task created with ID: {task_id}")
        
        # Test getting pending tasks
        pending_tasks = await task_manager.get_pending_tasks()
        print(f"Pending tasks: {len(pending_tasks)}")
        
        # Test task status
        status = await task_manager.get_status()
        print(f"Task manager status: {status}")
        
        # Wait for a bit to see background tasks in action
        print("Task manager running. Press Ctrl+C to exit...")
        await asyncio.sleep(30)
        
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt, shutting down...")
    finally:
        await task_manager.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
