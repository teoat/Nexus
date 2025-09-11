#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
Todo Orchestrator for Nexus Platform
Manages and processes todos across the system.
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class TodoPriority(Enum):
    """Todo priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class TodoStatus(Enum):
    """Todo status levels"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass
class Todo:
    """Todo item structure"""
    id: str
    title: str
    description: str
    priority: TodoPriority
    status: TodoStatus
    tags: List[str]
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        """
          Post Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        if self.metadata is None:
            self.metadata = {}

class TodoOrchestrator:
    """Manages and processes todos across the system"""
    
    def __init__(self, workspace_path: str):
        """
          Init  
        
        
        Args:
            workspace_path: Description of workspace_path
    
        Example:
            TBD: Add usage example
        """
        self.workspace_path = Path(workspace_path)
        self.todos: Dict[str, Todo] = {}
        self.data_file = self.workspace_path / ".nexus" / "todos.json"
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing todos
        self.load_todos()
    
    def load_todos(self):
        """Load todos from storage"""
        try:
            if self.data_file.exists():
                import json
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    for todo_id, todo_data in data.items():
                        # Convert string enums back to enum objects
                        todo_data['priority'] = TodoPriority(todo_data['priority'])
                        todo_data['status'] = TodoStatus(todo_data['status'])
                        self.todos[todo_id] = Todo(**todo_data)
                logger.info(f"Loaded {len(self.todos)} todos")
        except Exception as e:
            logger.error(f"Error loading todos: {e}")
    
    def save_todos(self):
        """Save todos to storage"""
        try:
            import json
            data = {}
            for todo_id, todo in self.todos.items():
                todo_dict = asdict(todo)
                # Convert enums to their values for JSON serialization
                todo_dict['priority'] = todo.priority.value
                todo_dict['status'] = todo.status.value
                data[todo_id] = todo_dict
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving todos: {e}")
    
    def add_todo(self, title: str, description: str = "", priority: TodoPriority = TodoPriority.MEDIUM, 
                 tags: List[str] = None) -> str:
        """Add a new todo"""
        if tags is None:
            tags = []
        
        todo_id = f"todo_{int(time.time() * 1000)}"
        now = datetime.now().isoformat()
        
        todo = Todo(
            id=todo_id,
            title=title,
            description=description,
            priority=priority,
            status=TodoStatus.PENDING,
            tags=tags,
            created_at=now,
            updated_at=now
        )
        
        self.todos[todo_id] = todo
        self.save_todos()
        
        logger.info(f"Added todo: {title}")
        return todo_id
    
    def update_todo(self, todo_id: str, updates: Dict[str, Any]) -> bool:
        """Update a todo"""
        if todo_id not in self.todos:
            return False
        
        todo = self.todos[todo_id]
        
        # Update fields
        for key, value in updates.items():
            if hasattr(todo, key):
                if key == 'priority' and isinstance(value, int):
                    setattr(todo, key, TodoPriority(value))
                elif key == 'status' and isinstance(value, str):
                    setattr(todo, key, TodoStatus(value))
                else:
                    setattr(todo, key, value)
        
        todo.updated_at = datetime.now().isoformat()
        
        # Set completed_at if status is completed
        if todo.status == TodoStatus.COMPLETED and not todo.completed_at:
            todo.completed_at = todo.updated_at
        
        self.save_todos()
        logger.info(f"Updated todo: {todo_id}")
        return True
    
    def delete_todo(self, todo_id: str) -> bool:
        """Delete a todo"""
        if todo_id not in self.todos:
            return False
        
        del self.todos[todo_id]
        self.save_todos()
        logger.info(f"Deleted todo: {todo_id}")
        return True
    
    def get_todo(self, todo_id: str) -> Optional[Todo]:
        """
        Retrieve todo
        
        
        Args:
            todo_id: Description of todo_id
    
        Returns:
            Unknown: Description of return value
    
        Example:
            TBD: Add usage example
        """
        return self.todos.get(todo_id)
    
    def get_todos(self, status: Optional[TodoStatus] = None, 
                  priority: Optional[TodoPriority] = None,
                  tags: Optional[List[str]] = None) -> List[Todo]:
        """Get todos with optional filtering"""
        filtered_todos = []
        
        for todo in self.todos.values():
            # Filter by status
            if status and todo.status != status:
                continue
            
            # Filter by priority
            if priority and todo.priority != priority:
                continue
            
            # Filter by tags
            if tags and not any(tag in todo.tags for tag in tags):
                continue
            
            filtered_todos.append(todo)
        
        # Sort by priority (highest first) and creation time
        filtered_todos.sort(key=lambda t: (-t.priority.value, t.created_at))
        return filtered_todos
    
    def get_todo_stats(self) -> Dict[str, Any]:
        """Get todo statistics"""
        total = len(self.todos)
        pending = len([t for t in self.todos.values() if t.status == TodoStatus.PENDING])
        in_progress = len([t for t in self.todos.values() if t.status == TodoStatus.IN_PROGRESS])
        completed = len([t for t in self.todos.values() if t.status == TodoStatus.COMPLETED])
        cancelled = len([t for t in self.todos.values() if t.status == TodoStatus.CANCELLED])
        
        return {
            "total": total,
            "pending": pending,
            "in_progress": in_progress,
            "completed": completed,
            "cancelled": cancelled,
            "completion_rate": (completed / total * 100) if total > 0 else 0
        }
    
    def run_once(self) -> Dict[str, Any]:
        """Process todos once (for automation)"""
        try:
            # Get pending todos
            pending_todos = self.get_todos(status=TodoStatus.PENDING)
            
            # Process high priority todos first
            high_priority = [t for t in pending_todos if t.priority == TodoPriority.CRITICAL]
            
            processed = 0
            for todo in high_priority[:5]:  # Process up to 5 todos
                self.update_todo(todo.id, {"status": TodoStatus.IN_PROGRESS})
                processed += 1
            
            return {
                "processed": processed,
                "total_pending": len(pending_todos),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing todos: {e}")
            return {"error": str(e)}
    
    def get_todos_by_priority(self) -> Dict[str, List[Todo]]:
        """Get todos grouped by priority"""
        grouped = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }
        
        for todo in self.todos.values():
            if todo.priority == TodoPriority.CRITICAL:
                grouped["critical"].append(todo)
            elif todo.priority == TodoPriority.HIGH:
                grouped["high"].append(todo)
            elif todo.priority == TodoPriority.MEDIUM:
                grouped["medium"].append(todo)
            else:
                grouped["low"].append(todo)
        
        return grouped
    
    def cleanup_completed_todos(self, days_old: int = 30) -> int:
        """Clean up old completed todos"""
        cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        todos_to_delete = []
        
        for todo_id, todo in self.todos.items():
            if (todo.status == TodoStatus.COMPLETED and 
                todo.completed_at and 
                datetime.fromisoformat(todo.completed_at).timestamp() < cutoff_date):
                todos_to_delete.append(todo_id)
        
        for todo_id in todos_to_delete:
            del self.todos[todo_id]
        
        if todos_to_delete:
            self.save_todos()
            logger.info(f"Cleaned up {len(todos_to_delete)} old completed todos")
        
        return len(todos_to_delete)
