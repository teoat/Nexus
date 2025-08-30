import asyncio
import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from automation.core.task_manager import Task

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BaseWorker(ABC):
    """
    Base worker class with common functionality for all specialized workers.
    This class is responsible for executing tasks, while the WorkerManager
    manages its lifecycle and state.
    """
    def __init__(self, name: str, worker_id: Optional[str] = None):
        self.worker_id = worker_id or str(uuid.uuid4())
        self.name = name
        self._current_task: Optional[asyncio.Task] = None

    async def start(self):
        """Initializes the worker."""
        logger.info(f"Worker {self.name} ({self.worker_id}) is ready.")
        # In a real scenario, this might involve setting up connections or resources.
        await asyncio.sleep(0.1)

    async def stop(self):
        """Cleans up worker resources."""
        logger.info(f"Worker {self.name} ({self.worker_id}) is stopping.")
        if self._current_task and not self._current_task.done():
            self._current_task.cancel()
        # In a real scenario, this might involve closing connections.
        await asyncio.sleep(0.1)
        logger.info(f"Worker {self.name} ({self.worker_id}) has stopped.")

    def heartbeat(self) -> Dict[str, Any]:
        """Provides a health check for the worker."""
        return {
            "worker_id": self.worker_id,
            "name": self.name,
            "is_busy": self._current_task is not None and not self._current_task.done(),
            "timestamp": time.time(),
        }

    async def run_task(self, task: Task) -> Any:
        """
        Executes a given task.
        """
        if self._current_task and not self._current_task.done():
            raise RuntimeError(f"Worker {self.name} ({self.worker_id}) is already busy.")

        logger.info(f"Worker {self.name} ({self.worker_id}) is starting task {task.id}.")
        self._current_task = asyncio.create_task(self._execute_task(task))
        try:
            result = await self._current_task
            logger.info(f"Worker {self.name} ({self.worker_id}) finished task {task.id}.")
            return result
        except asyncio.CancelledError:
            logger.warning(f"Task {task.id} was cancelled on worker {self.name} ({self.worker_id}).")
            raise
        finally:
            self._current_task = None

    @abstractmethod
    async def _execute_task(self, task: Task) -> Any:
        """
        The actual task execution logic, to be implemented by subclasses.
        """
        pass
