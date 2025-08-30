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

from automation.workers.base_worker import BaseWorker
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


from .worker_defs import WorkerState, WorkerType

logger = logging.getLogger(__name__)

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

@dataclass
class Worker:
    """Worker instance representation (data only)"""
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
    """
    
    WORKER_CLASS_MAP = {
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

    def __init__(self, config_manager, task_manager):
        """Initialize the worker manager"""
        self.config_manager = config_manager
        self.task_manager = task_manager
        
        # Worker storage
        self._workers: Dict[str, Worker] = {}
        self._worker_instances: Dict[str, BaseWorker] = {}
        self._worker_types: Dict[WorkerType, List[str]] = {wt: [] for wt in WorkerType}
        self._available_workers: List[str] = []
        self._busy_workers: List[str] = []
        
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
            self._load_config()
            await self._create_initial_workers()
            await self._start_background_tasks()
            logger.info("✅ Worker Manager initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Worker Manager initialization failed: {e}")
            raise
    
    def _load_config(self):
        """Load configuration from config manager"""
        self._health_check_interval = self.config_manager.get("worker.health_check_interval", 60)
        self._worker_timeout = self.config_manager.get("worker.worker_timeout", 1800)
        self._auto_scaling = self.config_manager.get("worker.auto_scaling", True)
        self._scaling_threshold = self.config_manager.get("worker.scaling_threshold", 0.8)
        self._scaling_cooldown = self.config_manager.get("worker.scaling_cooldown", 300)
    
    async def _create_initial_workers(self):
        """Create one of each worker type for testing purposes."""
        logger.info("Creating one of each worker type...")

        for worker_type in self.WORKER_CLASS_MAP.keys():
            worker_type_str = worker_type.value
            worker_dataclass = await self.create_worker(
                name=f"{worker_type_str}_worker_1",
                worker_type=worker_type,
                capabilities=self._get_default_capabilities(worker_type_str)
            )
            if worker_dataclass:
                await self.start_worker(worker_dataclass.id)
    
    def _get_default_capabilities(self, worker_type: str) -> List[WorkerCapability]:
        """Get default capabilities for a worker type"""
        # This can be expanded with more specific capabilities
        return [
            WorkerCapability(
                name=f"{worker_type}_capability",
                version="1.0.0",
                supported_task_types=[worker_type],
                max_concurrent_tasks=1 # Simplified for now
            )
        ]

    async def create_worker(self, name: str, worker_type: WorkerType, 
                           capabilities: List[WorkerCapability]) -> Optional[Worker]:
        """Create a new worker instance and its data representation"""
        try:
            worker_id = str(uuid.uuid4())
            
            worker_dataclass = Worker(
                id=worker_id,
                name=name,
                worker_type=worker_type,
                capabilities=capabilities,
                state=WorkerState.INITIALIZING,
                created_at=datetime.now()
            )
            
            self._workers[worker_id] = worker_dataclass
            self._worker_types[worker_type].append(worker_id)
            
            worker_class = self.WORKER_CLASS_MAP.get(worker_type)
            if not worker_class:
                logger.error(f"No worker class found for type: {worker_type.value}")
                return None

            worker_instance = worker_class(
                worker_id=worker_id,
                worker_name=name,
                worker_manager=self,
                task_manager=self.task_manager
            )
            self._worker_instances[worker_id] = worker_instance

            logger.info(f"✅ Worker created: {name} ({worker_id})")
            return worker_dataclass
            
        except Exception as e:
            logger.error(f"Error creating worker {name}: {e}", exc_info=True)
            return None

    async def start_worker(self, worker_id: str) -> bool:
        """Start a worker instance"""
        worker = self._workers.get(worker_id)
        worker_instance = self._worker_instances.get(worker_id)

        if not worker or not worker_instance:
            logger.error(f"Worker not found: {worker_id}")
            return False

        if worker.state not in [WorkerState.INITIALIZING, WorkerState.OFFLINE]:
            logger.warning(f"Worker {worker_id} is already started.")
            return True

        await worker_instance.start()
        worker.state = worker_instance.state
        worker.last_heartbeat = datetime.now()

        if worker_id not in self._available_workers:
            self._available_workers.append(worker_id)

        logger.info(f"✅ Worker started: {worker.name} ({worker_id})")
        return True

    async def stop_worker(self, worker_id: str) -> bool:
        """Stop a worker instance"""
        worker = self._workers.get(worker_id)
        worker_instance = self._worker_instances.get(worker_id)

        if not worker or not worker_instance:
            logger.error(f"Worker not found: {worker_id}")
            return False

        if worker.state == WorkerState.OFFLINE:
            return True

        await worker_instance.stop()
        worker.state = WorkerState.OFFLINE

        if worker_id in self._available_workers:
            self._available_workers.remove(worker_id)
        if worker_id in self._busy_workers:
            self._busy_workers.remove(worker_id)

        logger.info(f"✅ Worker stopped: {worker.name} ({worker_id})")
        return True
    
    async def assign_task(self, worker_id: str, task_id: str) -> bool:
        """Assign a task to a worker instance"""
        worker = self._workers.get(worker_id)
        worker_instance = self._worker_instances.get(worker_id)

        if not worker or not worker_instance:
            logger.error(f"Worker or instance not found for ID {worker_id}")
            return False

        if worker.state != WorkerState.IDLE:
            logger.warning(f"Worker {worker_id} is not idle.")
            return False

        if worker_instance.assign_task(task_id):
            worker.state = WorkerState.WORKING
            worker.current_task_id = task_id
            if worker_id in self._available_workers:
                self._available_workers.remove(worker_id)
            self._busy_workers.append(worker_id)
            logger.debug(f"Task {task_id} assigned to worker {worker_id}")
            return True
        
        logger.warning(f"Failed to assign task {task_id} to worker instance {worker_id}")
        return False

    async def receive_heartbeat(self, worker_id: str, state: WorkerState):
        """Receives a heartbeat from a worker."""
        if worker_id in self._workers:
            self._workers[worker_id].last_heartbeat = datetime.now()
            self._workers[worker_id].state = state
            logger.debug(f"Heartbeat received from worker {worker_id} with state {state.value}")

    async def complete_task(self, worker_id: str, task_id: str, success: bool, error_message: Optional[str] = None):
        """Mark a task as completed by a worker"""
        worker = self._workers.get(worker_id)
        if not worker:
            logger.error(f"Worker not found for completion: {worker_id}")
            return

        if worker.current_task_id != task_id:
            logger.warning(f"Completed task {task_id} does not match worker's current task {worker.current_task_id}")
            return

        worker.current_task_id = None
        worker.state = WorkerState.IDLE
        
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
        
        logger.debug(f"Task {task_id} completed by worker {worker_id} (success: {success})")
        
        # This is a bit of a hack, we should be passing the task manager to the worker manager
        # But for now, we assume the automation engine will call the task manager.
        # await self.task_manager.complete_task(task_id, success, error_message)


    async def get_available_workers(self) -> List[Worker]:
        """Get list of available workers"""
        return [self._workers[wid] for wid in self._available_workers if self._workers[wid].state == WorkerState.IDLE]
    
    async def get_status(self) -> Dict[str, Any]:
        """Get overall worker manager status"""
        return {
            "total_workers": len(self._workers),
            "available_workers": len(self._available_workers),
            "busy_workers": len(self._busy_workers),
            "worker_types": {wt.value: len(wids) for wt, wids in self._worker_types.items()},
            "auto_scaling": self._auto_scaling,
        }

    async def shutdown(self):
        """Shutdown the worker manager and all worker instances"""
        logger.info("🔄 Shutting down Worker Manager...")
        self._shutdown_event.set()
        
        if self._health_monitor_task:
            self._health_monitor_task.cancel()

        for worker_id in list(self._worker_instances.keys()):
            await self.stop_worker(worker_id)
        
        logger.info("✅ Worker Manager shutdown completed")

    async def _start_background_tasks(self):
        """Start background monitoring tasks"""
        self._health_monitor_task = asyncio.create_task(self._health_monitoring_loop())
        
    async def _health_monitoring_loop(self):
        """Background health monitoring loop"""
        while not self._shutdown_event.is_set():
            try:
                await self._perform_health_check()
                await asyncio.sleep(self._health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}", exc_info=True)
                await asyncio.sleep(10)

    async def _perform_health_check(self):
        """Perform health check on all workers"""
        for worker_id, worker in list(self._workers.items()):
            if worker.state == WorkerState.OFFLINE:
                continue
            
            if worker.last_heartbeat and (datetime.now() - worker.last_heartbeat).total_seconds() > self._worker_timeout:
                logger.warning(f"Worker {worker_id} timed out. Marking as offline.")
                await self.stop_worker(worker_id)

    async def get_health_status(self) -> float:
        """Get overall worker health status (0.0 to 1.0)"""
        if not self._workers:
            return 1.0

        active_workers = [w for w in self._workers.values() if w.state not in [WorkerState.OFFLINE, WorkerState.SHUTTING_DOWN]]

        if not active_workers:
            return 0.0

        health_scores = [w.health_score for w in active_workers]
        return statistics.mean(health_scores) if health_scores else 0.0

    async def get_statistics(self) -> Dict[str, Any]:
        """Get worker statistics"""
        if not self._workers:
            return {
                "total_workers": 0, "active_workers": 0, "average_health_score": 0.0,
                "average_performance_score": 0.0, "total_tasks_processed": 0
            }
        
        active_workers = [w for w in self._workers.values() if w.state not in [WorkerState.OFFLINE, WorkerState.SHUTTING_DOWN]]
        health_scores = [w.health_score for w in active_workers if w.health_score is not None]
        performance_scores = [w.performance_score for w in active_workers if w.performance_score is not None]
        total_tasks = sum(w.metrics.total_tasks_processed for w in self._workers.values())
        
        return {
            "total_workers": len(self._workers),
            "active_workers": len(active_workers),
            "average_health_score": statistics.mean(health_scores) if health_scores else 0.0,
            "average_performance_score": statistics.mean(performance_scores) if performance_scores else 0.0,
            "total_tasks_processed": total_tasks
        }

    async def get_utilization_rate(self) -> float:
        """Get worker utilization rate (0.0 to 1.0)"""
        active_workers = [w for w in self._workers.values() if w.state not in [WorkerState.OFFLINE, WorkerState.SHUTTING_DOWN]]
        if not active_workers:
            return 0.0
        
        busy_workers = sum(1 for w in active_workers if w.state == WorkerState.WORKING)
        return busy_workers / len(active_workers)

    async def optimize_scaling(self):
        """Placeholder for scaling logic"""
        logger.debug("Scaling optimization check.")
        pass # To be implemented later based on Phase 2 TODOs.
