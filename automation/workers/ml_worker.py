#!/usr/bin/env python3
"""
ML WORKER
"""

import asyncio
import logging
from typing import Any, Dict

from automation.workers.base_worker import BaseWorker
from automation.core.worker_defs import WorkerType

logger = logging.getLogger(__name__)


class MLWorker(BaseWorker):
    """
    A specialized worker for executing machine learning tasks.
    """

    def __init__(self, worker_id: str, worker_name: str, worker_manager, task_manager):
        super().__init__(worker_id, worker_name, WorkerType.ML, worker_manager, task_manager)
        logger.info(f"[{self.name}] MLWorker initialized.")

    async def execute_task(self, task_id: str, task_metadata: Dict[str, Any] = None):
        """
        Executes an ML task.
        This is a placeholder implementation.
        """
        logger.info(f"[{self.name}] Starting ML task: {task_id}")
        # Simulate some work
        await asyncio.sleep(15)
        logger.info(f"[{self.name}] Completed ML task: {task_id}")
