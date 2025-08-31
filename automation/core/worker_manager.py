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


from .worker_defs import WorkerState, WorkerType, WorkerCapability, WorkerMetrics

logger = logging.getLogger(__name__)

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
        
        # Health and scaling config
        self._health_check_interval: int = 60
        self._worker_timeout: int = 30
        self._auto_scaling: bool = True
        self._scaling_check_interval: int = 60
        self._scaling_up_threshold: float = 0.8
        self._scaling_down_threshold: float = 0.2
        self._scaling_cooldown: int = 120
        self._min_workers: int = 5
        self._max_workers: int = 100
        
        # Background tasks
        self._health_monitor_task: Optional[asyncio.Task] = None
        self._scaling_optimizer_task: Optional[asyncio.Task] = None
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
        self._worker_timeout = self.config_manager.get("worker.worker_timeout", 30)
        self._auto_scaling = self.config_manager.get("worker.auto_scaling", True)
        self._scaling_check_interval = self.config_manager.get("worker.scaling_check_interval", 60)
        self._scaling_up_threshold = self.config_manager.get("worker.scaling_up_threshold", 0.8)
        self._scaling_down_threshold = self.config_manager.get("worker.scaling_down_threshold", 0.2)
        self._scaling_cooldown = self.config_manager.get("worker.scaling_cooldown", 120)
        self._min_workers = self.config_manager.get("worker.min_workers", 5)
        self._max_workers = self.config_manager.get("worker.max_workers", 100)

    async def _create_initial_workers(self):
        """Create initial set of workers based on config."""
        logger.info(f"Creating {self._min_workers} initial workers...")

        for i in range(self._min_workers):
            # Creating general workers initially. Specific workers can be added via API or config.
            worker_type = WorkerType.GENERAL
            worker_type_str = worker_type.value
            worker_dataclass = await self.create_worker(
                name=f"{worker_type_str}_worker_{i+1}",
                worker_type=worker_type,
                capabilities=self._get_default_capabilities(worker_type_str)
            )
            if worker_dataclass:
                await self.start_worker(worker_dataclass.id)
    
    def _get_default_capabilities(self, worker_type: str) -> List[WorkerCapability]:
        """Get default capabilities for a worker type"""
        return [
            WorkerCapability(
                name=f"{worker_type}_capability",
                version="1.0.0",
                supported_task_types=[worker_type],
                max_concurrent_tasks=1
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
            if worker_type not in self._worker_types:
                self._worker_types[worker_type] = []
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
    
    async def remove_worker(self, worker_id: str):
        """Removes a worker completely from the manager."""
        if worker_id in self._workers:
            worker = self._workers[worker_id]
            if worker_id in self._worker_types[worker.worker_type]:
                self._worker_types[worker.worker_type].remove(worker_id)
            del self._workers[worker_id]
        if worker_id in self._worker_instances:
            del self._worker_instances[worker_id]
        if worker_id in self._available_workers:
            self._available_workers.remove(worker_id)
        if worker_id in self._busy_workers:
            self._busy_workers.remove(worker_id)
        logger.info(f"Worker {worker_id} removed from manager.")

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

    async def receive_heartbeat(self, worker_id: str, state: WorkerState, metrics: WorkerMetrics):
        """Receives a heartbeat from a worker."""
        if worker_id in self._workers:
            worker_data = self._workers[worker_id]
            worker_data.last_heartbeat = datetime.now()
            worker_data.state = state
            worker_data.metrics = metrics
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

        worker.metrics.last_task_time = datetime.now()
        
        logger.debug(f"Task {task_id} completed by worker {worker_id} (success: {success})")

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
        
        if self._health_monitor_task: self._health_monitor_task.cancel()
        if self._scaling_optimizer_task: self._scaling_optimizer_task.cancel()

        for worker_id in list(self._worker_instances.keys()):
            await self.stop_worker(worker_id)
        
        logger.info("✅ Worker Manager shutdown completed")

    async def _start_background_tasks(self):
        """Start background monitoring tasks"""
        self._health_monitor_task = asyncio.create_task(self._health_monitoring_loop())
        self._scaling_optimizer_task = asyncio.create_task(self._scaling_optimization_loop())
        
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

    async def _scaling_optimization_loop(self):
        """Background scaling optimization loop"""
        while not self._shutdown_event.is_set():
            try:
                await self.optimize_scaling()
                await asyncio.sleep(self._scaling_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scaling optimization loop: {e}", exc_info=True)

    async def _perform_health_check(self):
        """Perform health check on all workers, with recovery."""
        for worker_id, worker in list(self._workers.items()):
            if worker.state == WorkerState.OFFLINE:
                continue
            
            if worker.last_heartbeat and (datetime.now() - worker.last_heartbeat).total_seconds() > self._worker_timeout:
                logger.warning(f"Worker {worker.name} ({worker_id}) timed out. Recovering...")

                original_name = worker.name
                original_type = worker.worker_type
                original_caps = worker.capabilities

                await self.stop_worker(worker_id)
                await self.remove_worker(worker_id)

                new_worker = await self.create_worker(name=original_name, worker_type=original_type, capabilities=original_caps)
                if new_worker:
                    await self.start_worker(new_worker.id)
                    logger.info(f"Worker {original_name} recovered with new ID {new_worker.id}")
                else:
                    logger.error(f"Failed to recover worker {original_name}")
                continue

            if worker.metrics.total_tasks_processed > 0:
                worker.health_score = worker.metrics.successful_tasks / worker.metrics.total_tasks_processed
            else:
                worker.health_score = 1.0

            perf_score = worker.health_score * 0.5
            if worker.metrics.uptime_seconds > 60:
                throughput = worker.metrics.total_tasks_processed / (worker.metrics.uptime_seconds / 60)
                perf_score += min(1.0, throughput / 10.0) * 0.3

            if worker.metrics.average_task_duration > 0:
                perf_score += max(0.0, 1.0 - (worker.metrics.average_task_duration / 60.0)) * 0.2

            worker.performance_score = max(0.0, min(1.0, perf_score))

    async def optimize_scaling(self):
        """Optimize worker scaling based on load."""
        if not self._auto_scaling: return

        if self._last_scaling_decision and (datetime.now() - self._last_scaling_decision).total_seconds() < self._scaling_cooldown:
            return

        utilization = await self.get_utilization_rate()
        num_pending = len(await self.task_manager.get_pending_tasks())

        if utilization > self._scaling_up_threshold or num_pending > len(self._workers) * 2:
            await self._scale_up()
            self._last_scaling_decision = datetime.now()
        elif utilization < self._scaling_down_threshold and num_pending == 0:
            await self._scale_down()
            self._last_scaling_decision = datetime.now()

    async def _scale_up(self):
        """Scale up by adding a new general worker."""
        if len(self._workers) >= self._max_workers:
            logger.info("Max workers reached, cannot scale up.")
            return

        logger.info("Scaling up: adding a new worker.")
        worker_dataclass = await self.create_worker(
            name=f"general_worker_scaled_{len(self._workers) + 1}",
            worker_type=WorkerType.GENERAL,
            capabilities=self._get_default_capabilities(WorkerType.GENERAL.value)
        )
        if worker_dataclass:
            await self.start_worker(worker_dataclass.id)
            logger.info(f"Scaled up successfully. New worker: {worker_dataclass.id}")

    async def _scale_down(self):
        """Scale down by removing an idle worker."""
        if len(self._workers) <= self._min_workers:
            logger.info("Min workers reached, cannot scale down.")
            return

        idle_workers = [self._workers[wid] for wid in self._available_workers if self._workers[wid].state == WorkerState.IDLE]
        if not idle_workers:
            logger.info("No idle workers to scale down.")
            return

        # Remove the one with the lowest performance score
        worker_to_remove = sorted(idle_workers, key=lambda w: w.performance_score)[0]

        logger.info(f"Scaling down: removing worker {worker_to_remove.id}")
        await self.stop_worker(worker_to_remove.id)
        await self.remove_worker(worker_to_remove.id)
        logger.info(f"Scaled down successfully. Removed worker: {worker_to_remove.id}")

    async def get_health_status(self) -> float:
        """Get overall worker health status (0.0 to 1.0)"""
        if not self._workers: return 1.0
        active = [w for w in self._workers.values() if w.state not in [WorkerState.OFFLINE, WorkerState.SHUTTING_DOWN]]
        if not active: return 0.0
        return statistics.mean([w.health_score for w in active]) if active else 0.0

    async def get_statistics(self) -> Dict[str, Any]:
        """Get worker statistics"""
        if not self._workers:
            return {"total_workers": 0, "active_workers": 0, "average_health_score": 0.0, "average_performance_score": 0.0, "total_tasks_processed": 0}

        active = [w for w in self._workers.values() if w.state not in [WorkerState.OFFLINE, WorkerState.SHUTTING_DOWN]]
        health_scores = [w.health_score for w in active if w.health_score is not None]
        perf_scores = [w.performance_score for w in active if w.performance_score is not None]
        total_tasks = sum(w.metrics.total_tasks_processed for w in self._workers.values())
        
        return {
            "total_workers": len(self._workers),
            "active_workers": len(active),
            "average_health_score": statistics.mean(health_scores) if health_scores else 0.0,
            "average_performance_score": statistics.mean(perf_scores) if perf_scores else 0.0,
            "total_tasks_processed": total_tasks
        }

    async def get_utilization_rate(self) -> float:
        """Get worker utilization rate (0.0 to 1.0)"""
        active = [w for w in self._workers.values() if w.state not in [WorkerState.OFFLINE, WorkerState.SHUTTING_DOWN]]
        if not active: return 0.0
        busy = sum(1 for w in active if w.state == WorkerState.WORKING)
        return busy / len(active)
