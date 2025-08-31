#!/usr/bin/env python3
"""
DATA WORKER
"""

import asyncio
import logging
from typing import Any, Dict

from automation.workers.base_worker import BaseWorker
from automation.core.worker_defs import WorkerType

logger = logging.getLogger(__name__)


class DataWorker(BaseWorker):
    """
    A specialized worker for executing data processing tasks.
    """

    def __init__(self, worker_id: str, worker_name: str, worker_manager, task_manager):
        super().__init__(worker_id, worker_name, WorkerType.DATA, worker_manager, task_manager)
        logger.info(f"[{self.name}] DataWorker initialized.")

    async def execute_task(self, task_id: str, task_metadata: Dict[str, Any] = None):
        """
        Executes a data processing task.
        This is a placeholder implementation.
        """
        logger.info(f"[{self.name}] Starting data processing task: {task_id}")
        # Simulate some work
        await asyncio.sleep(20)
        logger.info(f"[{self.name}] Completed data processing task: {task_id}")
