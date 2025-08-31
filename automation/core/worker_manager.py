#!/usr/bin/env python3
"""
👷 WORKER MANAGER - UNIFIED WORKER MANAGEMENT SYSTEM 👷

This module provides unified worker management for the consolidated automation system.
It handles worker lifecycle, health monitoring, auto-scaling, and task assignment.

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

from automation.workers.base_worker import BaseWorker, Task
from automation.workers.general_worker import GeneralWorker
from automation.workers.workflow_worker import WorkflowWorker
from automation.workers.ml_worker import MLWorker
from automation.workers.frontend_worker import FrontendWorker
from automation.workers.backend_worker import BackendWorker
from automation.workers.monitoring_worker import MonitoringWorker
from automation.workers.data_worker import DataWorker
from automation.workers.security_worker import SecurityWorker
from automation.workers.integration_worker import IntegrationWorker
from automation.workers.testing_worker import TestingWorker


logger = logging.getLogger(__name__)

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
    ML = "ml"
    FRONTEND = "frontend"
    BACKEND = "backend"
    MONITORING = "monitoring"
    DATA = "data"
    SECURITY = "security"
    INTEGRATION = "integration"
    TESTING = "testing"

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
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    last_updated: Optional[datetime] = None

@dataclass
class Worker:
    """Worker instance representation"""
    id: str
    name: str
    worker_type: WorkerType
    capabilities: List[WorkerCapability]
    state: WorkerState
    current_task_id: Optional[str] = None
    assigned_tasks: List[str] = field(default_factory=list)
    metrics: WorkerMetrics = field(default_factory=WorkerMetrics)
    created_at: datetime = field(default_factory=datetime.now)
    last_heartbeat: Optional[datetime] = None
    health_score: float = 1.0
    performance_score: float = 1.0

class WorkerManager:
    """
    Unified worker management system for the consolidated automation system.
    
    This class provides:
    - Worker lifecycle management (create, start, stop, monitor)
    - Health monitoring and failure detection
    - Auto-scaling based on load and performance
    - Task assignment and worker selection
    - Performance optimization and load balancing
    """
    
    def __init__(self, config_manager, task_manager=None):
        """Initialize the worker manager"""
        self.config_manager = config_manager
        self.task_manager = task_manager
        
        # Worker storage
        self._workers: Dict[str, Worker] = {}
        self._worker_instances: Dict[str, BaseWorker] = {}
        self._worker_types: Dict[WorkerType, List[str]] = {wt: [] for wt in WorkerType}
        self._available_workers: List[str] = []
        self._busy_workers: List[str] = []
        self._round_robin_index: int = 0
        
        # Performance tracking
        self._performance_history: List[float] = []
        self._scaling_history: List[Dict[str, Any]] = []
        self._last_scaling_decision: Optional[datetime] = None
        
        # Health monitoring
        self._health_check_interval: int = 60
        self._worker_timeout: int = 1800
        self._auto_scaling: bool = True
        self._scaling_threshold: float = 0.8
        self._scaling_cooldown: int = 300
        
        # Background tasks
        self._health_monitor_task: Optional[asyncio.Task] = None
        self._performance_optimizer_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        logger.info("👷 Worker Manager initialized")
    
    async def initialize(self):
        """Initialize the worker manager"""
        try:
            logger.info("🔄 Initializing Worker Manager...")
            
            # Load configuration
            self._load_config()
            
            # Create initial workers
            await self._create_initial_workers()
            
            # Start background tasks
            await self._start_background_tasks()
            
            logger.info("✅ Worker Manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Worker Manager initialization failed: {e}")
            raise
    
    def _load_config(self):
        """Load configuration from config manager"""
        try:
            self._health_check_interval = self.config_manager.get("worker.health_check_interval", 60)
            self._worker_timeout = self.config_manager.get("worker.worker_timeout", 1800)
            self._auto_scaling = self.config_manager.get("worker.auto_scaling", True)
            self._scaling_threshold = self.config_manager.get("worker.scaling_threshold", 0.8)
            self._scaling_cooldown = self.config_manager.get("worker.scaling_cooldown", 300)
            self._load_balancing_strategy = self.config_manager.get("worker.load_balancing_strategy", "round_robin")
            
            logger.debug("Worker configuration loaded")
            
        except Exception as e:
            logger.warning(f"Error loading worker configuration: {e}")
            logger.info("Using default worker configuration")
    
    async def _create_initial_workers(self):
        """Create initial set of workers"""
        try:
            min_workers = self.config_manager.get("worker.min_workers", 5)
            worker_type = self.config_manager.get("worker.default_type", "general")
            
            logger.info(f"Creating {min_workers} initial {worker_type} workers...")
            
            for i in range(min_workers):
                worker = await self.create_worker(
                    name=f"{worker_type}_worker_{i+1}",
                    worker_type=WorkerType(worker_type),
                    capabilities=self._get_default_capabilities(worker_type)
                )
                
                if worker:
                    await self.start_worker(worker.id)
            
            logger.info(f"✅ {min_workers} initial workers created and started")
            
        except Exception as e:
            logger.error(f"Error creating initial workers: {e}")
            raise
    
    def _get_default_capabilities(self, worker_type: str) -> List[WorkerCapability]:
        """Get default capabilities for worker type"""
        if worker_type == "workflow":
            return [
                WorkerCapability(
                    name="workflow_automation",
                    version="1.0.0",
                    supported_task_types=["workflow", "automation", "orchestration"],
                    max_concurrent_tasks=3
                )
            ]
        elif worker_type == "ml":
            return [
                WorkerCapability(
                    name="machine_learning",
                    version="1.0.0",
                    supported_task_types=["ml", "ai", "prediction", "analysis"],
                    max_concurrent_tasks=2
                )
            ]
        else:  # general
            return [
                WorkerCapability(
                    name="general_automation",
                    version="1.0.0",
                    supported_task_types=["general", "automation", "processing"],
                    max_concurrent_tasks=5
                )
            ]
    
    async def create_worker(self, name: str, worker_type: WorkerType, 
                           capabilities: List[WorkerCapability]) -> Optional[Worker]:
        """Create a new worker"""
        try:
            worker_id = str(uuid.uuid4())
            
            worker = Worker(
                id=worker_id,
                name=name,
                worker_type=worker_type,
                capabilities=capabilities,
                state=WorkerState.INITIALIZING,
                created_at=datetime.now()
            )

            # Map worker type to worker class
            worker_class_map = {
                WorkerType.GENERAL: GeneralWorker,
                WorkerType.WORKFLOW: WorkflowWorker,
                WorkerType.ML: MLWorker,
                WorkerType.FRONTEND: FrontendWorker,
                WorkerType.BACKEND: BackendWorker,
                WorkerType.MONITORING: MonitoringWorker,
                WorkerType.DATA: DataWorker,
                WorkerType.SECURITY: SecurityWorker,
                WorkerType.INTEGRATION: IntegrationWorker,
                WorkerType.TESTING: TestingWorker,
            }

            worker_class = worker_class_map.get(worker_type)
            if not worker_class:
                logger.error(f"Unknown worker type: {worker_type}")
                return None

            # Create worker instance
            worker_instance = worker_class(worker_id=worker_id)
            
            # Add to storage
            self._workers[worker_id] = worker
            self._worker_instances[worker_id] = worker_instance
            self._worker_types[worker_type].append(worker_id)
            
            logger.info(f"✅ Worker created: {name} ({worker_id})")
            return worker
            
        except Exception as e:
            logger.error(f"Error creating worker {name}: {e}")
            return None
    
    async def start_worker(self, worker_id: str) -> bool:
        """Start a worker"""
        try:
            if worker_id not in self._workers:
                logger.error(f"Worker not found: {worker_id}")
                return False
            
            worker = self._workers[worker_id]
            
            if worker.state in [WorkerState.WORKING, WorkerState.IDLE]:
                logger.warning(f"Worker {worker_id} is already running")
                return True
            
            # Start the worker instance
            worker_instance = self._worker_instances[worker_id]
            await worker_instance.start()

            # Update worker state
            worker.state = WorkerState.IDLE
            worker.last_heartbeat = datetime.now()
            
            # Add to available workers
            if worker_id not in self._available_workers:
                self._available_workers.append(worker_id)
            
            logger.info(f"✅ Worker started: {worker.name} ({worker_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error starting worker {worker_id}: {e}")
            return False
    
    async def stop_worker(self, worker_id: str) -> bool:
        """Stop a worker"""
        try:
            if worker_id not in self._workers:
                logger.error(f"Worker not found: {worker_id}")
                return False
            
            worker = self._workers[worker_id]
            
            if worker.state == WorkerState.OFFLINE:
                logger.warning(f"Worker {worker_id} is already stopped")
                return True
            
            # Stop the worker instance
            worker_instance = self._worker_instances[worker_id]
            await worker_instance.stop()

            # Update worker state
            worker.state = WorkerState.SHUTTING_DOWN
            
            # Remove from available and busy lists
            if worker_id in self._available_workers:
                self._available_workers.remove(worker_id)
            if worker_id in self._busy_workers:
                self._busy_workers.remove(worker_id)
            
            # Wait for current task to complete
            if worker.current_task_id:
                logger.info(f"Waiting for worker {worker_id} to complete current task...")
                # In a real implementation, you'd wait for task completion
            
            # Set final state
            worker.state = WorkerState.OFFLINE
            
            # Remove from instances
            if worker_id in self._worker_instances:
                del self._worker_instances[worker_id]

            logger.info(f"✅ Worker stopped: {worker.name} ({worker_id})")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping worker {worker_id}: {e}")
            return False
    
    def set_task_manager(self, task_manager):
        self.task_manager = task_manager

    async def assign_task(self, worker_id: str, task: Task) -> bool:
        """Assign a task to a worker"""
        try:
            if worker_id not in self._workers:
                logger.error(f"Worker not found: {worker_id}")
                return False
            
            worker = self._workers[worker_id]
            
            if worker.state != WorkerState.IDLE:
                logger.warning(f"Worker {worker_id} is not available (state: {worker.state.value})")
                return False
            
            # Check worker capacity
            current_task_count = len(worker.assigned_tasks)
            max_tasks = max(cap.max_concurrent_tasks for cap in worker.capabilities)
            
            if current_task_count >= max_tasks:
                logger.warning(f"Worker {worker_id} is at capacity ({current_task_count}/{max_tasks})")
                return False
            
            # Assign task
            worker.current_task_id = task.id
            worker.assigned_tasks.append(task.id)
            worker.state = WorkerState.WORKING
            worker.last_heartbeat = datetime.now()
            
            # Move to busy list
            if worker_id in self._available_workers:
                self._available_workers.remove(worker_id)
            if worker_id not in self._busy_workers:
                self._busy_workers.append(worker_id)

            # Run the task in the background
            asyncio.create_task(self._run_and_complete_task(worker_id, task))
            
            logger.debug(f"✅ Task {task.id} assigned to worker {worker_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error assigning task {task.id} to worker {worker_id}: {e}")
            return False

    async def _run_and_complete_task(self, worker_id: str, task: Task):
        """Helper function to run a task and handle its completion."""
        try:
            worker_instance = self._worker_instances[worker_id]
            result = await worker_instance.run_task(task)

            # Mark task as complete in TaskManager
            if self.task_manager:
                await self.task_manager.complete_task(task.id, success=True)

            # Mark task as complete in WorkerManager
            await self.complete_task(worker_id, task.id, success=True)

        except Exception as e:
            logger.error(f"Task {task.id} failed on worker {worker_id}: {e}", exc_info=True)
            # Mark task as failed in TaskManager
            if self.task_manager:
                await self.task_manager.complete_task(task.id, success=False, error_message=str(e))

            # Mark task as failed in WorkerManager
            await self.complete_task(worker_id, task.id, success=False)
    
    async def complete_task(self, worker_id: str, task_id: str, success: bool = True) -> bool:
        """Mark a task as completed by a worker"""
        try:
            if worker_id not in self._workers:
                logger.error(f"Worker not found: {worker_id}")
                return False
            
            worker = self._workers[worker_id]
            
            if task_id not in worker.assigned_tasks:
                logger.warning(f"Task {task_id} not assigned to worker {worker_id}")
                return False
            
            # Update worker state
            worker.assigned_tasks.remove(task_id)
            
            if not worker.assigned_tasks:
                worker.current_task_id = None
                worker.state = WorkerState.IDLE
                
                # Move back to available list
                if worker_id in self._busy_workers:
                    self._busy_workers.remove(worker_id)
                if worker_id not in self._available_workers:
                    self._available_workers.append(worker_id)
            
            # Update metrics
            worker.metrics.total_tasks_processed += 1
            if success:
                worker.metrics.successful_tasks += 1
            else:
                worker.metrics.failed_tasks += 1
            
            worker.metrics.last_task_time = datetime.now()
            worker.metrics.last_updated = datetime.now()
            
            logger.debug(f"✅ Task {task_id} completed by worker {worker_id} (success: {success})")
            return True
            
        except Exception as e:
            logger.error(f"Error completing task {task_id} for worker {worker_id}: {e}")
            return False
    
    async def get_available_workers(self) -> List[Worker]:
        """Get list of available workers"""
        available_workers = []
        
        for worker_id in self._available_workers:
            if worker_id in self._workers:
                worker = self._workers[worker_id]
                if worker.state == WorkerState.IDLE:
                    available_workers.append(worker)
        
        return available_workers

    async def get_next_available_worker(self) -> Optional[Worker]:
        """Get the next available worker based on the load balancing strategy."""
        available_workers = await self.get_available_workers()
        if not available_workers:
            return None

        if self._load_balancing_strategy == "least_connections":
            return min(available_workers, key=lambda w: len(w.assigned_tasks))

        # Default to round_robin
        if self._round_robin_index >= len(available_workers):
            self._round_robin_index = 0

        worker = available_workers[self._round_robin_index]
        self._round_robin_index += 1
        return worker
    
    async def get_worker_status(self, worker_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed status of a specific worker"""
        if worker_id not in self._workers:
            return None
        
        worker = self._workers[worker_id]
        
        return {
            "id": worker.id,
            "name": worker.name,
            "type": worker.worker_type.value,
            "state": worker.state.value,
            "current_task": worker.current_task_id,
            "assigned_tasks": worker.assigned_tasks,
            "capabilities": [asdict(cap) for cap in worker.capabilities],
            "metrics": asdict(worker.metrics),
            "health_score": worker.health_score,
            "performance_score": worker.performance_score,
            "created_at": worker.created_at.isoformat(),
            "last_heartbeat": worker.last_heartbeat.isoformat() if worker.last_heartbeat else None
        }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get overall worker manager status"""
        total_workers = len(self._workers)
        available_workers = len(self._available_workers)
        busy_workers = len(self._busy_workers)
        offline_workers = sum(1 for w in self._workers.values() if w.state == WorkerState.OFFLINE)
        
        return {
            "total_workers": total_workers,
            "available_workers": available_workers,
            "busy_workers": busy_workers,
            "offline_workers": offline_workers,
            "worker_types": {wt.value: len(worker_ids) for wt, worker_ids in self._worker_types.items()},
            "auto_scaling": self._auto_scaling,
            "scaling_threshold": self._scaling_threshold,
            "last_scaling_decision": self._last_scaling_decision.isoformat() if self._last_scaling_decision else None
        }
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get worker statistics"""
        if not self._workers:
            return {
                "total_workers": 0,
                "active_workers": 0,
                "average_health_score": 0.0,
                "average_performance_score": 0.0,
                "total_tasks_processed": 0
            }
        
        active_workers = [w for w in self._workers.values() if w.state not in [WorkerState.OFFLINE, WorkerState.SHUTTING_DOWN]]
        
        health_scores = [w.health_score for w in active_workers]
        performance_scores = [w.performance_score for w in active_workers]
        total_tasks = sum(w.metrics.total_tasks_processed for w in self._workers.values())
        
        return {
            "total_workers": len(self._workers),
            "active_workers": len(active_workers),
            "average_health_score": statistics.mean(health_scores) if health_scores else 0.0,
            "average_performance_score": statistics.mean(performance_scores) if performance_scores else 0.0,
            "total_tasks_processed": total_tasks
        }
    
    async def get_health_status(self) -> float:
        """Get overall worker health status (0.0 to 1.0)"""
        if not self._workers:
            return 1.0
        
        active_workers = [w for w in self._workers.values() if w.state not in [WorkerState.OFFLINE, WorkerState.SHUTTING_DOWN]]
        
        if not active_workers:
            return 0.0
        
        health_scores = [w.health_score for w in active_workers]
        return statistics.mean(health_scores)
    
    async def get_utilization_rate(self) -> float:
        """Get worker utilization rate (0.0 to 1.0)"""
        if not self._workers:
            return 0.0
        
        active_workers = [w for w in self._workers.values() if w.state not in [WorkerState.OFFLINE, WorkerState.SHUTTING_DOWN]]
        
        if not active_workers:
            return 0.0
        
        total_capacity = sum(max(cap.max_concurrent_tasks for cap in w.capabilities) for w in active_workers)
        current_usage = sum(len(w.assigned_tasks) for w in active_workers)
        
        if total_capacity == 0:
            return 0.0
        
        return min(1.0, current_usage / total_capacity)
    
    async def optimize_scaling(self):
        """Optimize worker scaling based on current load and performance"""
        try:
            if not self._auto_scaling:
                return
            
            # Check cooldown period
            if (self._last_scaling_decision and 
                (datetime.now() - self._last_scaling_decision).total_seconds() < self._scaling_cooldown):
                return
            
            current_utilization = await self.get_utilization_rate()
            current_health = await self.get_health_status()
            
            logger.debug(f"Scaling optimization - Utilization: {current_utilization:.2f}, Health: {current_health:.2f}")
            
            # Scale up if utilization is high and health is good
            if current_utilization > self._scaling_threshold and current_health > 0.8:
                await self._scale_up()
            # Scale down if utilization is low
            elif current_utilization < 0.3 and len(self._workers) > self.config_manager.get("worker.min_workers", 5):
                await self._scale_down()
            
            self._last_scaling_decision = datetime.now()
            
        except Exception as e:
            logger.error(f"Error during scaling optimization: {e}")
    
    async def _scale_up(self):
        """Scale up by adding more workers"""
        try:
            current_workers = len(self._workers)
            max_workers = self.config_manager.get("worker.max_workers", 100)
            
            if current_workers >= max_workers:
                logger.debug("Maximum workers reached, cannot scale up")
                return
            
            # Determine how many workers to add
            scale_factor = min(2, max(1, int(current_workers * 0.2)))  # Add 20% or 1-2 workers
            workers_to_add = min(scale_factor, max_workers - current_workers)
            
            logger.info(f"Scaling up: Adding {workers_to_add} workers")
            
            # Add workers
            for i in range(workers_to_add):
                worker_type = WorkerType.GENERAL  # Default type for scaling
                worker = await self.create_worker(
                    name=f"scaled_worker_{current_workers + i + 1}",
                    worker_type=worker_type,
                    capabilities=self._get_default_capabilities("general")
                )
                
                if worker:
                    await self.start_worker(worker.id)
            
            # Record scaling decision
            self._scaling_history.append({
                "timestamp": datetime.now().isoformat(),
                "action": "scale_up",
                "workers_added": workers_to_add,
                "reason": "high_utilization"
            })
            
            logger.info(f"✅ Scaled up: Added {workers_to_add} workers")
            
        except Exception as e:
            logger.error(f"Error scaling up: {e}")
    
    async def _scale_down(self):
        """Scale down by removing workers"""
        try:
            current_workers = len(self._workers)
            min_workers = self.config_manager.get("worker.min_workers", 5)
            
            if current_workers <= min_workers:
                logger.debug("Minimum workers reached, cannot scale down")
                return
            
            # Determine how many workers to remove
            workers_to_remove = min(1, int(current_workers * 0.1))  # Remove 10% or 1 worker
            
            logger.info(f"Scaling down: Removing {workers_to_remove} workers")
            
            # Remove least performing workers
            workers_by_performance = sorted(
                [w for w in self._workers.values() if w.state == WorkerState.IDLE],
                key=lambda w: w.performance_score
            )
            
            removed_count = 0
            for worker in workers_by_performance[:workers_to_remove]:
                if await self.stop_worker(worker.id):
                    removed_count += 1
            
            # Record scaling decision
            self._scaling_history.append({
                "timestamp": datetime.now().isoformat(),
                "action": "scale_down",
                "workers_removed": removed_count,
                "reason": "low_utilization"
            })
            
            logger.info(f"✅ Scaled down: Removed {removed_count} workers")
            
        except Exception as e:
            logger.error(f"Error scaling down: {e}")
    
    async def _start_background_tasks(self):
        """Start background monitoring and optimization tasks"""
        logger.info("🔄 Starting background tasks...")
        
        # Health monitoring task
        self._health_monitor_task = asyncio.create_task(self._health_monitoring_loop())
        
        # Performance optimization task
        self._performance_optimizer_task = asyncio.create_task(self._performance_optimization_loop())
        
        logger.info("✅ Background tasks started successfully")
    
    async def _health_monitoring_loop(self):
        """Background health monitoring loop"""
        while not self._shutdown_event.is_set():
            try:
                await self._perform_health_check()
                await asyncio.sleep(self._health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(10)
    
    async def _performance_optimization_loop(self):
        """Background performance optimization loop"""
        while not self._shutdown_event.is_set():
            try:
                await self.optimize_scaling()
                await asyncio.sleep(60)  # Check every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in performance optimization loop: {e}")
                await asyncio.sleep(60)
    
    async def _perform_health_check(self):
        """Perform health check on all workers"""
        try:
            current_time = datetime.now()
            
            for worker_id, worker in list(self._workers.items()):
                if worker.state in [WorkerState.OFFLINE, WorkerState.SHUTTING_DOWN]:
                    continue

                worker_instance = self._worker_instances.get(worker_id)
                if not worker_instance:
                    logger.warning(f"Worker instance for {worker_id} not found. Marking as offline.")
                    worker.state = WorkerState.OFFLINE
                    continue

                # Get heartbeat from the worker instance
                heartbeat_data = worker_instance.heartbeat()
                worker.last_heartbeat = datetime.fromtimestamp(heartbeat_data['timestamp'])
                worker.metrics.cpu_usage = heartbeat_data.get('cpu_usage', 0.0)
                worker.metrics.memory_usage = heartbeat_data.get('memory_usage', 0.0)

                # Check worker timeout
                if (current_time - worker.last_heartbeat).total_seconds() > self._worker_timeout:
                    logger.warning(f"Worker {worker_id} timed out, marking as offline")
                    worker.state = WorkerState.OFFLINE
                    worker.health_score = 0.0
                    continue
                
                # Update state based on heartbeat
                if heartbeat_data['is_busy']:
                    if worker.state == WorkerState.IDLE:
                         worker.state = WorkerState.WORKING
                else:
                    if worker.state == WorkerState.WORKING:
                        worker.state = WorkerState.IDLE


                # Update health score based on recent performance
                if worker.metrics.total_tasks_processed > 0:
                    success_rate = worker.metrics.successful_tasks / worker.metrics.total_tasks_processed
                    worker.health_score = success_rate
                else:
                    worker.health_score = 1.0  # New worker, assume healthy
                
                # Update performance score
                if worker.metrics.total_tasks_processed > 0:
                    # Simple performance calculation based on success rate and task count
                    worker.performance_score = (worker.health_score + 
                                             min(1.0, worker.metrics.total_tasks_processed / 100)) / 2
                else:
                    worker.performance_score = 1.0
                
                # Update metrics
                if worker.created_at:
                    worker.metrics.uptime_seconds = int((current_time - worker.created_at).total_seconds())
                worker.metrics.last_updated = current_time
            
        except Exception as e:
            logger.error(f"Error during health check: {e}")
    
    async def shutdown(self):
        """Shutdown the worker manager"""
        try:
            logger.info("🔄 Shutting down Worker Manager...")
            
            self._shutdown_event.set()
            
            # Stop all workers
            for worker_id in list(self._workers.keys()):
                await self.stop_worker(worker_id)
            
            # Cancel background tasks
            if self._health_monitor_task:
                self._health_monitor_task.cancel()
            if self._performance_optimizer_task:
                self._performance_optimizer_task.cancel()
            
            # Wait for tasks to complete (handle cancellation gracefully)
            if self._health_monitor_task:
                try:
                    await self._health_monitor_task
                except asyncio.CancelledError:
                    pass
            if self._performance_optimizer_task:
                try:
                    await self._performance_optimizer_task
                except asyncio.CancelledError:
                    pass
            
            logger.info("✅ Worker Manager shutdown completed")
            
        except Exception as e:
            logger.error(f"❌ Worker Manager shutdown failed: {e}")


# Main entry point for testing
async def main():
    """Main entry point for testing the worker manager"""
    # Create a mock config manager for testing
    class MockConfigManager:
        def get(self, key, default=None):
            config = {
                "worker.health_check_interval": 60,
                "worker.worker_timeout": 1800,
                "worker.auto_scaling": True,
                "worker.scaling_threshold": 0.8,
                "worker.scaling_cooldown": 300,
                "worker.min_workers": 5,
                "worker.max_workers": 100,
                "worker.default_type": "general"
            }
            return config.get(key, default)
    
    config_manager = MockConfigManager()
    worker_manager = WorkerManager(config_manager, None)
    
    try:
        await worker_manager.initialize()
        
        # Test worker creation and management
        print("Worker Manager initialized successfully!")
        print(f"Total workers: {len(worker_manager._workers)}")
        print(f"Available workers: {len(worker_manager._available_workers)}")
        
        # Wait for a bit to see background tasks in action
        print("Worker manager running. Press Ctrl+C to exit...")
        await asyncio.sleep(30)
        
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt, shutting down...")
    finally:
        await worker_manager.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
