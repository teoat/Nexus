#!/usr/bin/env python3
"""
🤖 BASE WORKER - ABSTRACT BASE CLASS FOR ALL WORKERS 🤖

This module defines the abstract base class for all specialized workers in the
consolidated automation system. It provides common functionality for worker
lifecycle, health monitoring, and task execution.

Version: 1.0.0
Status: Development
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

# Assuming a way to interact with the WorkerManager, this would likely be an RPC client
# or a message queue interface in a real distributed system. For now, we'll
# assume a direct object reference for simplicity.
# from automation.core.worker_manager import WorkerManager
from automation.core.worker_defs import WorkerState, WorkerType

logger = logging.getLogger(__name__)


class BaseWorker(ABC):
    """
    Abstract base class for all workers in the automation system.
    """

    def __init__(
        self,
        worker_id: str,
        worker_name: str,
        worker_type: WorkerType,
        worker_manager,  # This would be a client/stub in a real system
        task_manager,
    ):
        self.worker_id = worker_id
        self.name = worker_name
        self.worker_type = worker_type
        self.worker_manager = worker_manager
        self.task_manager = task_manager
        self.state = WorkerState.INITIALIZING
        self.current_task_id: Optional[str] = None
        self._shutdown = asyncio.Event()
        self._main_task: Optional[asyncio.Task] = None
        self.last_heartbeat: Optional[datetime] = None

        logger.info(f"[{self.name}] Worker initialized with ID: {self.worker_id}")

    async def start(self):
        """Starts the worker's main loop."""
        if self.state not in [WorkerState.INITIALIZING, WorkerState.OFFLINE]:
            logger.warning(f"[{self.name}] Worker is already running or paused.")
            return

        logger.info(f"[{self.name}] Starting worker...")
        self.state = WorkerState.IDLE
        self._shutdown.clear()
        self._main_task = asyncio.create_task(self.run())

    async def stop(self):
        """Stops the worker gracefully."""
        logger.info(f"[{self.name}] Stopping worker...")
        self.state = WorkerState.SHUTTING_DOWN
        self._shutdown.set()
        if self._main_task:
            try:
                await asyncio.wait_for(self._main_task, timeout=10.0)
            except asyncio.TimeoutError:
                logger.warning(f"[{self.name}] Main task did not finish in time. Forcing cancellation.")
                self._main_task.cancel()
        self.state = WorkerState.OFFLINE
        logger.info(f"[{self.name}] Worker stopped.")

    async def run(self):
        """The main execution loop for the worker."""
        logger.info(f"[{self.name}] Worker run loop started.")
        while not self._shutdown.is_set():
            try:
                if self.state == WorkerState.IDLE:
                    # In a real system, this would be a long poll or listen on a message queue
                    # For now, we simulate polling for a task
                    await asyncio.sleep(2)
                    # The AutomationEngine will assign a task, changing the state.
                    # This is a simplification. A real worker would get a task from a queue.

                elif self.state == WorkerState.WORKING:
                    if self.current_task_id:
                        await self.execute_task_wrapper(self.current_task_id)
                    else:
                        logger.warning(f"[{self.name}] In WORKING state but no current_task_id.")
                        self.state = WorkerState.IDLE
                        await self.worker_manager.complete_task(self.worker_id, self.current_task_id, success=False)


                await self._send_heartbeat()
                await asyncio.sleep(5)  # Main loop sleep

            except asyncio.CancelledError:
                logger.info(f"[{self.name}] Run loop cancelled.")
                break
            except Exception as e:
                logger.error(f"[{self.name}] Error in run loop: {e}", exc_info=True)
                self.state = WorkerState.ERROR
                # Try to recover
                await asyncio.sleep(10)
                self.state = WorkerState.IDLE

        logger.info(f"[{self.name}] Worker run loop finished.")

    async def execute_task_wrapper(self, task_id: str):
        """A wrapper around the abstract execute_task method to handle common logic."""
        success = False
        error_message = None
        try:
            logger.info(f"[{self.name}] Executing task {task_id}...")
            # This is where the specialized worker logic is called
            await self.execute_task(task_id)
            logger.info(f"[{self.name}] Task {task_id} executed successfully.")
            success = True
        except Exception as e:
            logger.error(f"[{self.name}] Failed to execute task {task_id}: {e}", exc_info=True)
            error_message = str(e)
            success = False
        finally:
            # Notify the manager that the task is complete
            await self.worker_manager.complete_task(self.worker_id, task_id, success=success, error_message=error_message)
            await self.task_manager.complete_task(task_id, success=success, error_message=error_message)
            self.current_task_id = None
            self.state = WorkerState.IDLE


    @abstractmethod
    async def execute_task(self, task_id: str, task_metadata: Dict[str, Any] = None):
        """
        Execute a specific task. This method must be implemented by subclasses.
        """
        pass

    async def _send_heartbeat(self):
        """Sends a heartbeat to the WorkerManager to indicate health."""
        # In a real system, this would be an update to a shared resource (e.g., Redis)
        # or an RPC call.
        self.last_heartbeat = datetime.now()
        # This is a simplification. The worker manager will check this.
        # In a real system the worker would push its heartbeat.
        if hasattr(self.worker_manager, 'receive_heartbeat'):
             await self.worker_manager.receive_heartbeat(self.worker_id, self.state)
        logger.debug(f"[{self.name}] Heartbeat sent.")

    def assign_task(self, task_id: str):
        """Assigns a task to this worker."""
        if self.state == WorkerState.IDLE:
            self.current_task_id = task_id
            self.state = WorkerState.WORKING
            logger.info(f"[{self.name}] Assigned task {task_id}.")
            return True
        else:
            logger.warning(f"[{self.name}] Cannot assign task, worker is not IDLE (state: {self.state}).")
            return False
