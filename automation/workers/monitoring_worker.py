import asyncio
import logging
from .base_worker import BaseWorker
from automation.core.task_manager import Task
from typing import Any

logger = logging.getLogger(__name__)

class MonitoringWorker(BaseWorker):
    """
    A specialized worker for executing monitoring tasks.
    """
    def __init__(self, worker_id: str = None):
        super().__init__(name="MonitoringWorker", worker_id=worker_id)

    async def _execute_task(self, task: Task) -> Any:
        """
        Main logic for the monitoring worker.
        """
        logger.info(f"MonitoringWorker ({self.worker_id}) is executing task {task.id}.")
        # In a real implementation, this might involve collecting metrics or checking health.
        await asyncio.sleep(5)
        logger.info(f"MonitoringWorker ({self.worker_id}) finished task {task.id}.")
        return {"status": "success", "task_id": task.id}
