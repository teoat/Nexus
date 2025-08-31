#!/usr/bin/env python3
"""
TASK SCHEDULER
"""

import logging
from typing import Any, Dict, List, Optional

from automation.core.task_manager import TaskManager, TaskPriority, TaskType

logger = logging.getLogger(__name__)


class TaskScheduler:
    """
    Handles intelligent task scheduling.
    """

    def __init__(self, task_manager: TaskManager):
        self.task_manager = task_manager
        logger.info("TaskScheduler initialized.")

    async def schedule_task(
        self,
        title: str,
        description: str,
        task_type: TaskType,
        priority: TaskPriority = TaskPriority.MEDIUM,
        dependencies: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Schedules a new task by creating it in the TaskManager.

        In a more advanced system, this could involve more complex logic,
        like checking resource availability, estimating task duration, etc.
        """
        logger.info(f"Scheduling task: {title}")
        task_id = await self.task_manager.create_task(
            title=title,
            description=description,
            task_type=task_type,
            priority=priority,
            dependencies=dependencies,
            metadata=metadata,
        )
        logger.info(f"Task {title} scheduled with ID: {task_id}")
        return task_id
