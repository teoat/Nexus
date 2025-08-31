#!/usr/bin/env python3
"""
TASK EXECUTOR
"""

import logging
from automation.core.task_manager import TaskManager
from automation.core.worker_manager import WorkerManager

logger = logging.getLogger(__name__)


class TaskExecutor:
    """
    Manages the lifecycle of task execution.
    """

    def __init__(self, task_manager: TaskManager, worker_manager: WorkerManager):
        self.task_manager = task_manager
        self.worker_manager = worker_manager
        logger.info("TaskExecutor initialized.")

    async def execute_pending_tasks(self):
        """
        Gets pending tasks and assigns them to available workers based on capabilities.
        """
        pending_tasks = await self.task_manager.get_pending_tasks()
        if not pending_tasks:
            return

        available_workers = await self.worker_manager.get_available_workers()
        if not available_workers:
            logger.debug("No available workers to execute tasks.")
            return

        # Create a map of task types to available workers
        worker_map = {}
        for worker in available_workers:
            for capability in worker.capabilities:
                for task_type in capability.supported_task_types:
                    if task_type not in worker_map:
                        worker_map[task_type] = []
                    worker_map[task_type].append(worker)

        for task in pending_tasks:
            task_type_str = task.task_type.value
            if task_type_str in worker_map and worker_map[task_type_str]:
                worker = worker_map[task_type_str].pop(0)

                assign_success = await self.worker_manager.assign_task(worker.id, task.id)
                if assign_success:
                    await self.task_manager.start_task(task.id, worker.id)
                    logger.info(f"Assigned task {task.id} ({task.title}) to worker {worker.id} ({worker.name})")
                else:
                    # if assignment fails, put it back
                    worker_map[task_type_str].append(worker)
            else:
                logger.debug(f"No available worker for task type {task_type_str}")
