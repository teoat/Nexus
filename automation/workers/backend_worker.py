#!/usr/bin/env python3
"""
BACKEND WORKER
"""

import asyncio
import logging
from typing import Any, Dict

from automation.workers.base_worker import BaseWorker
from automation.core.worker_defs import WorkerType

logger = logging.getLogger(__name__)


class BackendWorker(BaseWorker):
    """
    A specialized worker for executing backend automation tasks.
    """

    def __init__(self, worker_id: str, worker_name: str, worker_manager, task_manager):
        super().__init__(worker_id, worker_name, WorkerType.BACKEND, worker_manager, task_manager)
        logger.info(f"[{self.name}] BackendWorker initialized.")

    async def execute_task(self, task_id: str, task_metadata: Dict[str, Any] = None):
        """
        Executes a backend task.
        This is a placeholder implementation.
        """
        logger.info(f"[{self.name}] Starting backend task: {task_id}")
        # Simulate some work
        await asyncio.sleep(12)
        logger.info(f"[{self.name}] Completed backend task: {task_id}")
