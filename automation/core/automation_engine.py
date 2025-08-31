#!/usr/bin/env python3
"""
🚀 CONSOLIDATED AUTOMATION ENGINE - CORE SYSTEM 🚀

This is the main automation orchestrator for the consolidated automation system.
It provides the foundation for all automation functionality including worker management,
task management, configuration management, and system monitoring.

Version: 1.0.0
Status: Production Ready
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import signal
import contextlib
import statistics

# Import core components
from .worker_manager import WorkerManager
from .task_manager import TaskManager, TaskType, TaskPriority
from .config_manager import ConfigManager
from automation.tasks.task_scheduler import TaskScheduler
from automation.tasks.task_executor import TaskExecutor


# Setup logging
logger = logging.getLogger(__name__)

class SystemState(Enum):
    """System operational states"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    SHUTTING_DOWN = "shutting_down"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class AutomationEngine:
    """
    Main automation orchestrator for the consolidated automation system.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the automation engine"""
        self.config_path = config_path or "automation/config/settings.json"
        self.state = SystemState.INITIALIZING
        self.start_time = None
        self.last_health_check = None
        self.last_performance_optimization = None
        
        # Core components
        self.config_manager = None
        self.worker_manager = None
        self.task_manager = None
        self.task_scheduler = None
        self.task_executor = None
        
        # System metrics
        self.system_metrics = {
            "start_time": None,
            "uptime_seconds": 0,
            "total_tasks_processed": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "active_workers": 0,
            "total_workers": 0,
            "system_health_score": 1.0,
            "performance_score": 1.0,
            "last_updated": None
        }
        
        # Background tasks
        self.background_tasks = set()
        self.shutdown_event = asyncio.Event()
        
        self._setup_signal_handlers()
        logger.info("🚀 Automation Engine initialized")
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown")
            asyncio.create_task(self.shutdown())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def initialize(self):
        """Initialize the automation engine and all components"""
        try:
            logger.info("🔄 Initializing Automation Engine...")
            
            self.config_manager = ConfigManager(self.config_path)
            await self.config_manager.initialize()
            logger.info("✅ Configuration manager initialized")
            
            self.task_manager = TaskManager(self.config_manager)
            await self.task_manager.initialize()
            logger.info("✅ Task manager initialized")

            self.worker_manager = WorkerManager(self.config_manager, self.task_manager)
            await self.worker_manager.initialize()
            logger.info("✅ Worker manager initialized")

            # Initialize task scheduler and executor
            self.task_scheduler = TaskScheduler(self.task_manager)
            self.task_executor = TaskExecutor(self.task_manager, self.worker_manager)
            logger.info("✅ Task scheduler and executor initialized")
            
            self.state = SystemState.RUNNING
            self.start_time = datetime.now()
            self.system_metrics["start_time"] = self.start_time.isoformat()
            
            await self._start_background_tasks()
            
            logger.info("🎉 Automation Engine initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Automation Engine initialization failed: {e}", exc_info=True)
            self.state = SystemState.ERROR
            raise
    
    async def _start_background_tasks(self):
        """Start background monitoring and optimization tasks"""
        logger.info("🔄 Starting background tasks...")
        
        tasks_to_create = [
            self._health_monitoring_loop(),
            self._performance_optimization_loop(),
            self._metrics_collection_loop(),
            self._task_processing_loop(),
        ]
        
        for coro in tasks_to_create:
            task = asyncio.create_task(coro)
            self.background_tasks.add(task)
            task.add_done_callback(self.background_tasks.discard)
        
        logger.info("✅ Background tasks started successfully")
    
    async def _health_monitoring_loop(self):
        """Background health monitoring loop"""
        while not self.shutdown_event.is_set():
            try:
                await self._perform_health_check()
                await asyncio.sleep(self.config_manager.get("health_check_interval", 60))
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}", exc_info=True)
                await asyncio.sleep(10)
    
    async def _performance_optimization_loop(self):
        """Background performance optimization loop"""
        while not self.shutdown_event.is_set():
            try:
                await self._optimize_performance()
                await asyncio.sleep(self.config_manager.get("performance_optimization_interval", 300))
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in performance optimization loop: {e}", exc_info=True)
                await asyncio.sleep(60)
    
    async def _metrics_collection_loop(self):
        """Background metrics collection loop"""
        while not self.shutdown_event.is_set():
            try:
                await self._update_system_metrics()
                await asyncio.sleep(self.config_manager.get("metrics_collection_interval", 30))
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}", exc_info=True)
                await asyncio.sleep(30)
    
    async def _task_processing_loop(self):
        """Background task processing loop"""
        while not self.shutdown_event.is_set():
            try:
                if self.state == SystemState.RUNNING:
                    await self._process_pending_tasks()
                await asyncio.sleep(self.config_manager.get("task_processing_interval", 5))
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in task processing loop: {e}", exc_info=True)
                await asyncio.sleep(10)
    
    async def _perform_health_check(self):
        """Perform comprehensive system health check"""
        try:
            worker_health = await self.worker_manager.get_health_status()
            task_health = await self.task_manager.get_health_status()
            
            health_scores = [worker_health, task_health]
            overall_health = statistics.mean(health_scores) if health_scores else 1.0
            
            self.system_metrics["system_health_score"] = overall_health
            self.last_health_check = datetime.now()
            
            if overall_health < 0.5: self.state = SystemState.ERROR
            elif overall_health < 0.8: self.state = SystemState.MAINTENANCE
            else: self.state = SystemState.RUNNING
            
        except Exception as e:
            logger.error(f"Error during health check: {e}")
            self.state = SystemState.ERROR
    
    async def _optimize_performance(self):
        """Optimize system performance based on current metrics"""
        # Placeholder for future implementation
        pass
    
    async def _update_system_metrics(self):
        """Update system metrics with current data"""
        if self.start_time:
            self.system_metrics["uptime_seconds"] = int((datetime.now() - self.start_time).total_seconds())

        worker_stats = await self.worker_manager.get_statistics()
        task_stats = await self.task_manager.get_statistics()

        self.system_metrics.update({
            "active_workers": worker_stats.get("active_workers", 0),
            "total_workers": worker_stats.get("total_workers", 0),
            "total_tasks_processed": task_stats.get("total_processed", 0),
            "successful_tasks": task_stats.get("successful", 0),
            "failed_tasks": task_stats.get("failed", 0),
            "last_updated": datetime.now().isoformat()
        })
    
    async def _process_pending_tasks(self):
        """Process pending tasks using the TaskExecutor."""
        try:
            await self.task_executor.execute_pending_tasks()
        except Exception as e:
            logger.error(f"Error processing pending tasks: {e}", exc_info=True)

    async def schedule_task(self, title: str, description: str, task_type: TaskType,
                         priority: TaskPriority = TaskPriority.MEDIUM,
                         dependencies: Optional[List[str]] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Schedule a new task using the TaskScheduler."""
        if self.state not in [SystemState.RUNNING, SystemState.MAINTENANCE]:
            logger.error(f"Cannot schedule task in state {self.state.value}")
            return None

        try:
            task_id = await self.task_scheduler.schedule_task(
                title=title,
                description=description,
                task_type=task_type,
                priority=priority,
                dependencies=dependencies,
                metadata=metadata
            )
            return task_id
        except Exception as e:
            logger.error(f"Error scheduling task: {e}", exc_info=True)
            return None

    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "state": self.state.value,
            "metrics": self.system_metrics,
            "worker_status": await self.worker_manager.get_status() if self.worker_manager else None,
            "task_status": await self.task_manager.get_status() if self.task_manager else None,
        }
    
    async def shutdown(self):
        """Gracefully shutdown the automation engine"""
        logger.info("🔄 Initiating graceful shutdown...")
        self.state = SystemState.SHUTTING_DOWN
        self.shutdown_event.set()
        
        for task in self.background_tasks:
            task.cancel()
        
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        if self.worker_manager: await self.worker_manager.shutdown()
        if self.task_manager: await self.task_manager.shutdown()
        if self.config_manager: await self.config_manager.shutdown()
        
        logger.info("✅ Automation Engine shutdown completed")
    
    async def run(self):
        """Main run loop for the automation engine"""
        try:
            await self.initialize()
            await self.shutdown_event.wait()
        except asyncio.CancelledError:
            logger.info("Automation Engine run loop cancelled")
        except Exception as e:
            logger.error(f"Error in Automation Engine run loop: {e}", exc_info=True)
            self.state = SystemState.ERROR
        finally:
            if not self.shutdown_event.is_set():
                await self.shutdown()

async def main():
    """Main entry point for testing the automation engine"""
    engine = AutomationEngine()
    try:
        await engine.run()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    finally:
        await engine.shutdown()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    asyncio.run(main())
