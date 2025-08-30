#!/usr/bin/env python3
"""
GENERAL WORKER
"""

import asyncio
import logging
from typing import Any, Dict

from automation.workers.base_worker import BaseWorker
from automation.core.worker_defs import WorkerType

logger = logging.getLogger(__name__)


class GeneralWorker(BaseWorker):
    """
    A general-purpose worker for executing various automation tasks.
    """

    def __init__(self, worker_id: str, worker_name: str, worker_manager, task_manager):
        super().__init__(worker_id, worker_name, WorkerType.GENERAL, worker_manager, task_manager)
        logger.info(f"[{self.name}] GeneralWorker initialized.")

    async def execute_task(self, task_id: str, task_metadata: Dict[str, Any] = None):
        """
        Executes a general task.
        This is a placeholder implementation.
        """
        logger.info(f"[{self.name}] Starting general task: {task_id}")
        await asyncio.sleep(5)
        logger.info(f"[{self.name}] Completed general task: {task_id}")
