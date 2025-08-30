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

# Import core components (will be implemented next)
from .worker_manager import WorkerManager
from .task_manager import TaskManager, TaskType, TaskPriority
from .config_manager import ConfigManager

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
    
    This class coordinates all automation activities including:
    - Worker management and scaling
    - Task scheduling and execution
    - System monitoring and health checks
    - Performance optimization
    - Error handling and recovery
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
        
        # Signal handlers
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
            
            # Initialize configuration manager
            self.config_manager = ConfigManager(self.config_path)
            await self.config_manager.initialize()
            logger.info("✅ Configuration manager initialized")
            
            # Initialize worker manager
            self.worker_manager = WorkerManager(self.config_manager)
            await self.worker_manager.initialize()
            logger.info("✅ Worker manager initialized")
            
            # Initialize task manager
            self.task_manager = TaskManager(self.config_manager)
            await self.task_manager.initialize()
            logger.info("✅ Task manager initialized")

            # Set task_manager in worker_manager
            self.worker_manager.set_task_manager(self.task_manager)
            
            # Set system state
            self.state = SystemState.RUNNING
            self.start_time = datetime.now()
            self.system_metrics["start_time"] = self.start_time.isoformat()
            
            # Start background tasks
            await self._start_background_tasks()
            
            logger.info("🎉 Automation Engine initialization completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Automation Engine initialization failed: {e}")
            self.state = SystemState.ERROR
            raise
    
    async def _start_background_tasks(self):
        """Start background monitoring and optimization tasks"""
        logger.info("🔄 Starting background tasks...")
        
        # Health monitoring task
        health_task = asyncio.create_task(self._health_monitoring_loop())
        self.background_tasks.add(health_task)
        health_task.add_done_callback(self.background_tasks.discard)
        
        # Performance optimization task
        perf_task = asyncio.create_task(self._performance_optimization_loop())
        self.background_tasks.add(perf_task)
        perf_task.add_done_callback(self.background_tasks.discard)
        
        # Metrics collection task
        metrics_task = asyncio.create_task(self._metrics_collection_loop())
        self.background_tasks.add(metrics_task)
        metrics_task.add_done_callback(self.background_tasks.discard)
        
        # Task processing task
        task_task = asyncio.create_task(self._task_processing_loop())
        self.background_tasks.add(task_task)
        task_task.add_done_callback(self.background_tasks.discard)
        
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
                logger.error(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(10)  # Wait before retrying
    
    async def _performance_optimization_loop(self):
        """Background performance optimization loop"""
        while not self.shutdown_event.is_set():
            try:
                await self._optimize_performance()
                await asyncio.sleep(self.config_manager.get("performance_optimization_interval", 300))
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in performance optimization loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _metrics_collection_loop(self):
        """Background metrics collection loop"""
        while not self.shutdown_event.is_set():
            try:
                await self._update_system_metrics()
                await asyncio.sleep(self.config_manager.get("metrics_collection_interval", 30))
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics collection loop: {e}")
                await asyncio.sleep(30)  # Wait before retrying
    
    async def _task_processing_loop(self):
        """Background task processing loop"""
        while not self.shutdown_event.is_set():
            try:
                await self._process_pending_tasks()
                await asyncio.sleep(self.config_manager.get("task_processing_interval", 5))
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in task processing loop: {e}")
                await asyncio.sleep(10)  # Wait before retrying
    
    async def _perform_health_check(self):
        """Perform comprehensive system health check"""
        try:
            logger.debug("🔍 Performing system health check...")
            
            # Check worker health
            worker_health = await self.worker_manager.get_health_status()
            
            # Check task manager health
            task_health = await self.task_manager.get_health_status()
            
            # Calculate overall system health
            health_scores = [worker_health, task_health]
            overall_health = statistics.mean(health_scores) if health_scores else 1.0
            
            self.system_metrics["system_health_score"] = overall_health
            self.last_health_check = datetime.now()
            
            # Update system state based on health
            if overall_health < 0.5:
                self.state = SystemState.ERROR
                logger.error(f"❌ System health critical: {overall_health}")
            elif overall_health < 0.8:
                self.state = SystemState.MAINTENANCE
                logger.warning(f"⚠️ System health degraded: {overall_health}")
            else:
                if self.state != SystemState.RUNNING:
                    self.state = SystemState.RUNNING
                    logger.info(f"✅ System health restored: {overall_health}")
            
            logger.debug(f"Health check completed. Score: {overall_health}")
            
        except Exception as e:
            logger.error(f"Error during health check: {e}")
            self.state = SystemState.ERROR
    
    async def _optimize_performance(self):
        """Optimize system performance based on current metrics"""
        try:
            logger.debug("🔄 Starting performance optimization...")
            
            # Get current performance metrics
            current_performance = self.system_metrics.get("performance_score", 1.0)
            current_health = self.system_metrics.get("system_health_score", 1.0)
            
            # Worker scaling optimization
            if current_health > 0.8 and current_performance < 0.9:
                await self.worker_manager.optimize_scaling()
            
            # Task scheduling optimization
            if current_performance < 0.9:
                await self.task_manager.optimize_scheduling()
            
            # Update performance score
            new_performance = await self._calculate_performance_score()
            self.system_metrics["performance_score"] = new_performance
            self.last_performance_optimization = datetime.now()
            
            logger.debug(f"Performance optimization completed. Score: {new_performance}")
            
        except Exception as e:
            logger.error(f"Error during performance optimization: {e}")
    
    async def _update_system_metrics(self):
        """Update system metrics with current data"""
        try:
            # Update uptime
            if self.start_time:
                uptime = (datetime.now() - self.start_time).total_seconds()
                self.system_metrics["uptime_seconds"] = int(uptime)
            
            # Update worker metrics
            worker_stats = await self.worker_manager.get_statistics()
            self.system_metrics["active_workers"] = worker_stats.get("active_workers", 0)
            self.system_metrics["total_workers"] = worker_stats.get("total_workers", 0)
            
            # Update task metrics
            task_stats = await self.task_manager.get_statistics()
            self.system_metrics["total_tasks_processed"] = task_stats.get("total_processed", 0)
            self.system_metrics["successful_tasks"] = task_stats.get("successful", 0)
            self.system_metrics["failed_tasks"] = task_stats.get("failed", 0)
            
            # Update timestamp
            self.system_metrics["last_updated"] = datetime.now().isoformat()
            
        except Exception as e:
            logger.error(f"Error updating system metrics: {e}")
    
    async def _process_pending_tasks(self):
        """Process pending tasks and assign them to available workers"""
        try:
            # Get pending tasks
            pending_tasks = await self.task_manager.get_pending_tasks()
            
            if not pending_tasks:
                return
            
            # Get available workers
            available_workers = await self.worker_manager.get_available_workers()
            
            if not available_workers:
                return
            
            # Assign tasks to workers
            for task in pending_tasks[:len(available_workers)]:
                worker = available_workers.pop(0)
                success = await self.worker_manager.assign_task(worker.id, task)
                
                if success:
                    await self.task_manager.start_task(task.id, worker.id)
                    logger.debug(f"Assigned task {task.id} to worker {worker.id}")
                else:
                    # Put worker back in available list
                    available_workers.append(worker)
            
        except Exception as e:
            logger.error(f"Error processing pending tasks: {e}")
    
    async def _calculate_performance_score(self) -> float:
        """Calculate overall system performance score"""
        try:
            # Get various performance indicators
            worker_utilization = await self.worker_manager.get_utilization_rate()
            task_throughput = await self.task_manager.get_throughput_rate()
            error_rate = await self.task_manager.get_error_rate()
            
            # Calculate weighted performance score
            performance_score = (
                worker_utilization * 0.4 +
                task_throughput * 0.4 +
                (1.0 - error_rate) * 0.2
            )
            
            return max(0.0, min(1.0, performance_score))
            
        except Exception as e:
            logger.error(f"Error calculating performance score: {e}")
            return 1.0
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "state": self.state.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "uptime_seconds": self.system_metrics["uptime_seconds"],
            "metrics": self.system_metrics.copy(),
            "worker_status": await self.worker_manager.get_status() if self.worker_manager else None,
            "task_status": await self.task_manager.get_status() if self.task_manager else None,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "last_performance_optimization": self.last_performance_optimization.isoformat() if self.last_performance_optimization else None
        }
    
    async def pause(self):
        """Pause the automation engine"""
        if self.state == SystemState.RUNNING:
            self.state = SystemState.PAUSED
            logger.info("⏸️ Automation Engine paused")
        else:
            logger.warning(f"Cannot pause engine in state: {self.state.value}")
    
    async def resume(self):
        """Resume the automation engine"""
        if self.state == SystemState.PAUSED:
            self.state = SystemState.RUNNING
            logger.info("▶️ Automation Engine resumed")
        else:
            logger.warning(f"Cannot resume engine in state: {self.state.value}")
    
    async def shutdown(self):
        """Gracefully shutdown the automation engine"""
        logger.info("🔄 Initiating graceful shutdown...")
        
        self.state = SystemState.SHUTTING_DOWN
        self.shutdown_event.set()
        
        # Cancel all background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Wait for background tasks to complete
        if self.background_tasks:
            await asyncio.gather(*self.background_tasks, return_exceptions=True)
        
        # Shutdown components
        if self.worker_manager:
            await self.worker_manager.shutdown()
        
        if self.task_manager:
            await self.task_manager.shutdown()
        
        if self.config_manager:
            await self.config_manager.shutdown()
        
        logger.info("✅ Automation Engine shutdown completed")
    
    async def run(self):
        """Main run loop for the automation engine"""
        try:
            # Initialize the engine
            await self.initialize()
            
            # Main run loop
            while not self.shutdown_event.is_set():
                if self.state == SystemState.RUNNING:
                    # Process any immediate tasks
                    await self._process_pending_tasks()
                
                # Wait before next iteration
                await asyncio.sleep(1)
                
        except asyncio.CancelledError:
            logger.info("Automation Engine run loop cancelled")
        except Exception as e:
            logger.error(f"Error in Automation Engine run loop: {e}")
            self.state = SystemState.ERROR
        finally:
            await self.shutdown()

# Main entry point for testing
async def main():
    """Main entry point for testing the automation engine"""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    engine = AutomationEngine()
    
    try:
        await engine.initialize()

        # Create a test task
        task_id = await engine.task_manager.create_task(
            title="Test Task from Engine",
            description="A test task created and executed via the automation engine.",
            task_type=TaskType.GENERAL,
            priority=TaskPriority.HIGH
        )
        logger.info(f"Created test task with ID: {task_id}")

        # Let the engine run for a bit to process the task
        logger.info("Engine running for 10 seconds to process task...")
        await asyncio.sleep(10)

        # Check the status of the task
        task_status = await engine.task_manager.get_task_status(task_id)
        logger.info(f"Final status of task {task_id}: {task_status['status']}")

        # Get final system status
        system_status = await engine.get_system_status()
        logger.info(f"Final system status: Uptime {system_status['uptime_seconds']}s, "
                    f"Tasks processed: {system_status['metrics']['total_tasks_processed']}")

    except Exception as e:
        logger.error(f"An error occurred during engine test: {e}", exc_info=True)
    finally:
        await engine.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
