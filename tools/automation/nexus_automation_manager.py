#!/usr/bin/env python3
"""
🤖 Nexus Automation Manager
Central management system for all Nexus automation tools
"""

import os
import sys
import json
import time
import argparse
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import psutil
import signal

class AutomationTask:
    """Represents an automation task"""
    
    def __init__(self, task_id: str, name: str, command: str, 
                 schedule: str = None, dependencies: List[str] = None):
        self.task_id = task_id
        self.name = name
        self.command = command
        self.schedule = schedule
        self.dependencies = dependencies or []
        self.status = 'pending'
        self.start_time = None
        self.end_time = None
        self.result = None
        self.error = None
        self.pid = None
    
    def to_dict(self) -> Dict:
        """Convert task to dictionary"""
        return {
            'task_id': self.task_id,
            'name': self.name,
            'command': self.command,
            'schedule': self.schedule,
            'dependencies': self.dependencies,
            'status': self.status,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'result': self.result,
            'error': self.error,
            'pid': self.pid
        }

class AutomationManager:
    """Central automation manager for Nexus platform"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or 'nexus_automation_config.json'
        self.tasks: Dict[str, AutomationTask] = {}
        self.running_tasks: Dict[str, subprocess.Popen] = {}
        self.task_history: List[Dict] = []
        self.config = self._load_config()
        self.tools_dir = Path(__file__).parent.parent
        self.running = False
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _load_config(self) -> Dict:
        """Load automation configuration"""
        default_config = {
            'max_concurrent_tasks': 5,
            'task_timeout': 3600,  # 1 hour
            'retry_attempts': 3,
            'retry_delay': 60,  # 1 minute
            'log_level': 'INFO',
            'auto_start': False,
            'tasks': []
        }
        
        if Path(self.config_file).exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in loaded_config:
                            loaded_config[key] = value
                    return loaded_config
            except Exception as e:
                print(f"Error loading config: {e}")
        
        return default_config
    
    def _save_config(self):
        """Save automation configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\nReceived signal {signum}, shutting down...")
        self.stop_all_tasks()
        self.running = False
    
    def add_task(self, task: AutomationTask):
        """Add a new automation task"""
        self.tasks[task.task_id] = task
        
        # Update config
        task_configs = [t for t in self.config['tasks'] if t['task_id'] != task.task_id]
        task_configs.append(task.to_dict())
        self.config['tasks'] = task_configs
        self._save_config()
        
        print(f"Added task: {task.name} ({task.task_id})")
    
    def remove_task(self, task_id: str):
        """Remove an automation task"""
        if task_id in self.tasks:
            del self.tasks[task_id]
            
            # Update config
            self.config['tasks'] = [t for t in self.config['tasks'] if t['task_id'] != task_id]
            self._save_config()
            
            print(f"Removed task: {task_id}")
    
    def start_task(self, task_id: str, background: bool = False) -> bool:
        """Start an automation task"""
        if task_id not in self.tasks:
            print(f"Task not found: {task_id}")
            return False
        
        task = self.tasks[task_id]
        
        # Check dependencies
        for dep_id in task.dependencies:
            if dep_id in self.tasks and self.tasks[dep_id].status != 'completed':
                print(f"Task {task_id} has unmet dependency: {dep_id}")
                return False
        
        # Check max concurrent tasks
        running_count = sum(1 for t in self.tasks.values() if t.status == 'running')
        if running_count >= self.config['max_concurrent_tasks']:
            print(f"Maximum concurrent tasks reached ({self.config['max_concurrent_tasks']})")
            return False
        
        try:
            # Start task
            task.status = 'running'
            task.start_time = datetime.now().isoformat()
            
            # Execute command
            if background:
                process = subprocess.Popen(
                    task.command.split(),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                task.pid = process.pid
                self.running_tasks[task_id] = process
                
                # Start monitoring thread
                monitor_thread = threading.Thread(
                    target=self._monitor_task,
                    args=(task_id, process)
                )
                monitor_thread.daemon = True
                monitor_thread.start()
                
            else:
                # Run synchronously
                result = subprocess.run(
                    task.command.split(),
                    capture_output=True,
                    text=True,
                    timeout=self.config['task_timeout']
                )
                
                task.status = 'completed' if result.returncode == 0 else 'failed'
                task.end_time = datetime.now().isoformat()
                task.result = result.stdout
                task.error = result.stderr
            
            print(f"Started task: {task.name} ({task_id})")
            return True
            
        except Exception as e:
            task.status = 'failed'
            task.end_time = datetime.now().isoformat()
            task.error = str(e)
            print(f"Failed to start task {task_id}: {e}")
            return False
    
    def _monitor_task(self, task_id: str, process: subprocess.Popen):
        """Monitor a running task"""
        try:
            stdout, stderr = process.communicate(timeout=self.config['task_timeout'])
            
            task = self.tasks[task_id]
            task.status = 'completed' if process.returncode == 0 else 'failed'
            task.end_time = datetime.now().isoformat()
            task.result = stdout
            task.error = stderr
            
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
            
            print(f"Task completed: {task.name} ({task_id}) - Status: {task.status}")
            
        except subprocess.TimeoutExpired:
            task = self.tasks[task_id]
            task.status = 'timeout'
            task.end_time = datetime.now().isoformat()
            task.error = 'Task timed out'
            
            process.kill()
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
            
            print(f"Task timed out: {task.name} ({task_id})")
            
        except Exception as e:
            task = self.tasks[task_id]
            task.status = 'failed'
            task.end_time = datetime.now().isoformat()
            task.error = str(e)
            
            if task_id in self.running_tasks:
                del self.running_tasks[task_id]
            
            print(f"Task failed: {task.name} ({task_id}) - Error: {e}")
    
    def stop_task(self, task_id: str) -> bool:
        """Stop a running task"""
        if task_id in self.running_tasks:
            process = self.running_tasks[task_id]
            process.terminate()
            
            # Wait for graceful shutdown
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
            
            del self.running_tasks[task_id]
            
            task = self.tasks[task_id]
            task.status = 'stopped'
            task.end_time = datetime.now().isoformat()
            
            print(f"Stopped task: {task.name} ({task_id})")
            return True
        
        return False
    
    def stop_all_tasks(self):
        """Stop all running tasks"""
        for task_id in list(self.running_tasks.keys()):
            self.stop_task(task_id)
    
    def get_task_status(self, task_id: str) -> Dict:
        """Get status of a specific task"""
        if task_id in self.tasks:
            return self.tasks[task_id].to_dict()
        return {}
    
    def list_tasks(self, status: str = None) -> List[Dict]:
        """List all tasks, optionally filtered by status"""
        tasks = [task.to_dict() for task in self.tasks.values()]
        
        if status:
            tasks = [task for task in tasks if task['status'] == status]
        
        return tasks
    
    def get_system_status(self) -> Dict:
        """Get overall system status"""
        total_tasks = len(self.tasks)
        running_tasks = sum(1 for t in self.tasks.values() if t.status == 'running')
        completed_tasks = sum(1 for t in self.tasks.values() if t.status == 'completed')
        failed_tasks = sum(1 for t in self.tasks.values() if t.status == 'failed')
        
        # System resources
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_tasks': total_tasks,
            'running_tasks': running_tasks,
            'completed_tasks': completed_tasks,
            'failed_tasks': failed_tasks,
            'system_resources': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'available_memory': memory.available
            },
            'config': {
                'max_concurrent_tasks': self.config['max_concurrent_tasks'],
                'task_timeout': self.config['task_timeout']
            }
        }
    
    def run_optimization_suite(self) -> Dict:
        """Run the complete optimization suite"""
        print("🚀 Running Nexus Optimization Suite...")
        
        # Define optimization tasks
        optimization_tasks = [
            AutomationTask(
                'workspace_analysis',
                'Workspace Analysis',
                f'python {self.tools_dir}/optimization/workspace_optimizer.py . --analyze --output workspace_analysis.json'
            ),
            AutomationTask(
                'asset_compression',
                'Asset Compression',
                f'python {self.tools_dir}/compression/compression_manager.py NEXUS_app/frontend --optimize --recursive',
                dependencies=['workspace_analysis']
            ),
            AutomationTask(
                'code_minification',
                'Code Minification',
                f'python {self.tools_dir}/minification/python_minifier.py NEXUS_app --recursive --aggressive',
                dependencies=['workspace_analysis']
            ),
            AutomationTask(
                'cleanup_temp_files',
                'Cleanup Temporary Files',
                f'python {self.tools_dir}/optimization/workspace_optimizer.py . --cleanup'
            )
        ]
        
        # Add tasks
        for task in optimization_tasks:
            self.add_task(task)
        
        # Start tasks in order
        results = {}
        for task in optimization_tasks:
            print(f"Starting: {task.name}")
            success = self.start_task(task.task_id, background=False)
            results[task.task_id] = {
                'success': success,
                'status': self.tasks[task.task_id].status,
                'result': self.tasks[task.task_id].result,
                'error': self.tasks[task.task_id].error
            }
        
        return results

def main():
    parser = argparse.ArgumentParser(description='Nexus Automation Manager')
    parser.add_argument('--config', default='nexus_automation_config.json', 
                       help='Configuration file')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add task command
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('--id', required=True, help='Task ID')
    add_parser.add_argument('--name', required=True, help='Task name')
    add_parser.add_argument('--command', required=True, help='Command to execute')
    add_parser.add_argument('--schedule', help='Schedule (cron format)')
    add_parser.add_argument('--dependencies', nargs='*', help='Task dependencies')
    
    # Remove task command
    remove_parser = subparsers.add_parser('remove', help='Remove a task')
    remove_parser.add_argument('--id', required=True, help='Task ID')
    
    # Start task command
    start_parser = subparsers.add_parser('start', help='Start a task')
    start_parser.add_argument('--id', required=True, help='Task ID')
    start_parser.add_argument('--background', action='store_true', help='Run in background')
    
    # Stop task command
    stop_parser = subparsers.add_parser('stop', help='Stop a task')
    stop_parser.add_argument('--id', required=True, help='Task ID')
    
    # List tasks command
    list_parser = subparsers.add_parser('list', help='List tasks')
    list_parser.add_argument('--status', help='Filter by status')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show system status')
    
    # Optimization suite command
    optimize_parser = subparsers.add_parser('optimize', help='Run optimization suite')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = AutomationManager(args.config)
    
    if args.command == 'add':
        task = AutomationTask(
            args.id, args.name, args.command, 
            args.schedule, args.dependencies
        )
        manager.add_task(task)
    
    elif args.command == 'remove':
        manager.remove_task(args.id)
    
    elif args.command == 'start':
        manager.start_task(args.id, args.background)
    
    elif args.command == 'stop':
        manager.stop_task(args.id)
    
    elif args.command == 'list':
        tasks = manager.list_tasks(args.status)
        print(f"\nTasks ({len(tasks)}):")
        for task in tasks:
            print(f"  {task['task_id']}: {task['name']} [{task['status']}]")
    
    elif args.command == 'status':
        status = manager.get_system_status()
        print(f"\nSystem Status:")
        print(f"  Total tasks: {status['total_tasks']}")
        print(f"  Running: {status['running_tasks']}")
        print(f"  Completed: {status['completed_tasks']}")
        print(f"  Failed: {status['failed_tasks']}")
        print(f"  CPU: {status['system_resources']['cpu_percent']:.1f}%")
        print(f"  Memory: {status['system_resources']['memory_percent']:.1f}%")
    
    elif args.command == 'optimize':
        results = manager.run_optimization_suite()
        print(f"\nOptimization Results:")
        for task_id, result in results.items():
            status = "✅" if result['success'] else "❌"
            print(f"  {status} {task_id}: {result['status']}")
            if result['error']:
                print(f"    Error: {result['error']}")

if __name__ == '__main__':
    main()
