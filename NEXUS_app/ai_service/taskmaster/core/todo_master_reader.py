#!/usr/bin/env python3
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class TodoMasterReader:
    def __init__(self):
        current_dir = Path(__file__).parent
        self.todo_master_path = (
            current_dir.parent.parent.parent.parent / "TODO_MASTER.md"
        )

    def get_all_todos(self):
        return []

    def get_pending_todos(self):
        return []
