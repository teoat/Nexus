import asyncio
import logging
from .base_worker import BaseWorker
from automation.core.task_manager import Task
from typing import Any

logger = logging.getLogger(__name__)

class GeneralWorker(BaseWorker):
    """
    A general-purpose worker for executing miscellaneous tasks.
    """
    def __init__(self, worker_id: str = None):
        super().__init__(name="GeneralWorker", worker_id=worker_id)

    async def _execute_task(self, task: Task) -> Any:
        """
        Main logic for the general worker.
        """
        logger.info(f"GeneralWorker ({self.worker_id}) is executing task {task.id}.")
        await asyncio.sleep(1)
        logger.info(f"GeneralWorker ({self.worker_id}) finished task {task.id}.")
        return {"status": "success", "task_id": task.id}
