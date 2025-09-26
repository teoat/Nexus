"""
Todo Scanner for the NexusX automation system.

This module scans for pending todo items in the project and
converts them to tasks for the MasterExecutor to process.
"""

import json
import os
import logging
import re
import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger("TodoScanner")

class TodoItem:
    """Represents a todo item from the project todo list"""
    def __init__(self, id: str, content: str, status: str):
        self.id = id
        self.content = content
        self.status = status  # pending, in_progress, completed, cancelled
        
    def __str__(self):
        return f"TodoItem({self.id}, {self.status}): {self.content}"
        
    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "status": self.status
        }


class TodoScanner:
    """
    Scans the NexusX project for todo items and converts them to executable tasks
    """
    
    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.getcwd()
        self.todos_cache: Dict[str, TodoItem] = {}
        self.last_scan_time = 0
        
    async def scan_files(self) -> List[TodoItem]:
        """
        Scan files for todo markers and extract todo items
        """
        todos = []
        try:
            # Find JSON todos first
            todos = await self._scan_json_todos()
            
            # If no JSON todos, try to extract from markdown files
            if not todos:
                todos = await self._scan_markdown_todos()
                
            # Cache results
            for todo in todos:
                self.todos_cache[todo.id] = todo
                
            logger.info(f"Found {len(todos)} todo items")
            return todos
            
        except Exception as e:
            logger.error(f"Error scanning for todos: {e}")
            return []
            
    async def _scan_json_todos(self) -> List[TodoItem]:
        """
        Scan for JSON todo files (.todos.json)
        """
        todo_files = [
            Path(self.project_root) / ".todos.json",
            Path(self.project_root) / "todos.json",
        ]
        
        for path in todo_files:
            if path.exists():
                logger.info(f"Found todo file: {path}")
                try:
                    with open(path, "r") as f:
                        data = json.load(f)
                    
                    # Parse todo items from JSON
                    items = []
                    if isinstance(data, list):
                        for item in data:
                            if "id" in item and "content" in item and "status" in item:
                                items.append(TodoItem(
                                    id=item["id"],
                                    content=item["content"],
                                    status=item["status"]
                                ))
                    return items
                    
                except Exception as e:
                    logger.error(f"Error parsing todo file {path}: {e}")
                    
        return []
    
    async def _scan_markdown_todos(self) -> List[TodoItem]:
        """
        Scan markdown files for todo lists
        """
        md_files = [
            Path(self.project_root) / "TODO.md",
            Path(self.project_root) / "ROADMAP.md"
        ]
        
        todos = []
        for path in md_files:
            if path.exists():
                logger.info(f"Found markdown file with potential todos: {path}")
                try:
                    with open(path, "r") as f:
                        content = f.read()
                        
                    # Extract todo items using regex
                    # Look for markdown task list items: - [ ] Task description
                    todo_pattern = r"[-*]\s+\[([ xX])\]\s+(.+)$"
                    matches = re.findall(todo_pattern, content, re.MULTILINE)
                    
                    for i, match in enumerate(matches):
                        status_marker = match[0].strip().lower()
                        task_content = match[1].strip()
                        
                        # Generate a stable ID based on content
                        task_id = f"md-todo-{i+1}"
                        
                        # Map status markers to our statuses
                        status = "completed" if status_marker in ["x", "X"] else "pending"
                        
                        todos.append(TodoItem(
                            id=task_id,
                            content=task_content,
                            status=status
                        ))
                        
                except Exception as e:
                    logger.error(f"Error parsing markdown file {path}: {e}")
        
        return todos
    
    async def find_pending_todos(self) -> List[TodoItem]:
        """
        Find all pending todo items in the project
        """
        all_todos = await self.scan_files()
        return [todo for todo in all_todos if todo.status == "pending"]
    
    def extract_task_type(self, todo_content: str) -> str:
        """
        Extract task type from todo content
        """
        content = todo_content.lower()
        if "python" in content or "environment" in content:
            return "python-environment"
        elif "health" in content or "check" in content:
            return "health-checks"
        elif "docker" in content:
            return "docker-setup"
        elif "error" in content or "logging" in content:
            return "error-handling"
        elif "frontend" in content or "html" in content or "css" in content:
            return "frontend"
        elif "database" in content or "postgresql" in content or "neo4j" in content:
            return "database-setup"
        elif "api" in content:
            return "api"
        else:
            return "generic"
        
    def create_task_from_todo(self, todo: TodoItem, task_type_mapping: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create a task from a todo item
        """
        task_type = self.extract_task_type(todo.content)
        
        # Get task info from mapping
        task_info = task_type_mapping.get(task_type, {
            "command": "nexus:generic_task",
            "skills": ["process"]
        })
        
        # Create the task
        task = {
            "id": f"nexus-{todo.id}",
            "task": task_info.get("command", "nexus:generic_task"),
            "params": {
                "todo_id": todo.id,
                "description": todo.content,
                "require_skill": task_info.get("skills", ["process"])[0]
            }
        }
        
        # Add subtasks for multi-step tasks
        if task_type == "health-checks":
            task["subtasks"] = self._create_health_check_subtasks()
        elif task_type == "docker-setup":
            task["subtasks"] = self._create_docker_setup_subtasks()
        
        return task
    
    def _create_health_check_subtasks(self) -> List[Dict[str, Any]]:
        """
        Create subtasks for health check implementation
        """
        services = ["api-gateway", "ai-engine", "fraud-detection", "forensic-analysis", "frenly-ai"]
        subtasks = []
        
        for service in services:
            subtasks.append({
                "task": "nexus:implement_health_check",
                "params": {
                    "service": service,
                    "require_skill": "health"
                }
            })
            
        return subtasks
    
    def _create_docker_setup_subtasks(self) -> List[Dict[str, Any]]:
        """
        Create subtasks for Docker setup
        """
        services = ["api-gateway", "ai-engine", "fraud-detection", "forensic-analysis", "frenly-ai"]
        subtasks = []
        
        for service in services:
            subtasks.append({
                "task": "nexus:create_docker_service",
                "params": {
                    "service": service,
                    "require_skill": "docker"
                }
            })
            
        return subtasks
