#!/usr/bin/env python3
"""
MONITORING WORKER
"""

import asyncio
import logging
from typing import Any, Dict

from automation.workers.base_worker import BaseWorker
from automation.core.worker_defs import WorkerType

logger = logging.getLogger(__name__)


class MonitoringWorker(BaseWorker):
    """
    A specialized worker for executing monitoring tasks.
    """

    def __init__(self, worker_id: str, worker_name: str, worker_manager, task_manager):
        super().__init__(worker_id, worker_name, WorkerType.MONITORING, worker_manager, task_manager)
        logger.info(f"[{self.name}] MonitoringWorker initialized.")

    async def execute_task(self, task_id: str, task_metadata: Dict[str, Any] = None):
        """
        Executes a monitoring task.
        This is a placeholder implementation.
        """
        logger.info(f"[{self.name}] Starting monitoring task: {task_id}")
        # Simulate some work
        await asyncio.sleep(5)
        logger.info(f"[{self.name}] Completed monitoring task: {task_id}")
