#!/usr/bin/env python3
"""
TESTING WORKER
"""

import asyncio
import logging
from typing import Any, Dict

from automation.workers.base_worker import BaseWorker
from automation.core.worker_defs import WorkerType

logger = logging.getLogger(__name__)


class TestingWorker(BaseWorker):
    """
    A specialized worker for executing testing automation tasks.
    """

    def __init__(self, worker_id: str, worker_name: str, worker_manager, task_manager):
        super().__init__(worker_id, worker_name, WorkerType.TESTING, worker_manager, task_manager)
        logger.info(f"[{self.name}] TestingWorker initialized.")

    async def execute_task(self, task_id: str, task_metadata: Dict[str, Any] = None):
        """
        Executes a testing task.
        This is a placeholder implementation.
        """
        logger.info(f"[{self.name}] Starting testing task: {task_id}")
        # Simulate some work
        await asyncio.sleep(15)
        logger.info(f"[{self.name}] Completed testing task: {task_id}")
