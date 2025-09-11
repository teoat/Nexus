#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
📝 Task Completion Updater
Updates master_todo.md file when tasks are completed
"""

import os
import sys
import re
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TaskCompletionUpdater:
    """Updates master_todo.md when tasks are completed"""
    
    def __init__(self, project_root: str = "/Users/Arief/Desktop/Nexus"):
        self.project_root = Path(project_root)
        self.master_todo_file = self.project_root / "master_todo.md"
        self.backup_dir = self.project_root / "backups" / "master_todo"
        self.completion_log = self.project_root / "task_completion_log.json"
        
        # Ensure backup directory exists
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def backup_master_todo(self) -> str:
        """Create a backup of master_todo.md before making changes"""
        if not self.master_todo_file.exists():
            return ""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"master_todo_backup_{timestamp}.md"
        
        try:
            with open(self.master_todo_file, 'r', encoding='utf-8') as src:
                content = src.read()
            
            with open(backup_file, 'w', encoding='utf-8') as dst:
                dst.write(content)
            
            logger.info(f"Backup created: {backup_file}")
            return str(backup_file)
        
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return ""
    
    def load_completion_log(self) -> Dict[str, Any]:
        """Load task completion log"""
        if not self.completion_log.exists():
            return {
                'completions': [],
                'last_updated': None,
                'total_completed': 0
            }
        
        try:
            with open(self.completion_log, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading completion log: {e}")
            return {
                'completions': [],
                'last_updated': None,
                'total_completed': 0
            }
    
    def save_completion_log(self, log_data: Dict[str, Any]):
        """Save task completion log"""
        try:
            log_data['last_updated'] = datetime.now().isoformat()
            with open(self.completion_log, 'w') as f:
                json.dump(log_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving completion log: {e}")
    
    def log_task_completion(self, task_title: str, task_line: int, completion_details: str = ""):
        """Log a task completion"""
        log_data = self.load_completion_log()
        
        completion_entry = {
            'task_title': task_title,
            'task_line': task_line,
            'completed_at': datetime.now().isoformat(),
            'completion_details': completion_details,
            'status': 'completed'
        }
        
        log_data['completions'].append(completion_entry)
        log_data['total_completed'] = len(log_data['completions'])
        
        self.save_completion_log(log_data)
        logger.info(f"Logged completion: {task_title} (line {task_line})")
    
    def update_task_status_in_file(self, line_number: int, new_status: str, completion_details: str = "") -> bool:
        """Update task status in master_todo.md file"""
        if not self.master_todo_file.exists():
            logger.error("Master todo file not found")
            return False
        
        try:
            # Create backup first
            backup_file = self.backup_master_todo()
            
            # Read the file
            with open(self.master_todo_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if line_number < 1 or line_number > len(lines):
                logger.error(f"Invalid line number: {line_number}")
                return False
            
            # Get the line to update
            line_index = line_number - 1
            original_line = lines[line_index]
            
            # Check if it's a pending task (including those starting with -)
            if not ('⏳' in original_line and not original_line.strip().startswith('###') and not original_line.strip().startswith('**') and 'tasks' not in original_line.lower()):
                logger.warning(f"Line {line_number} is not a pending task: {original_line.strip()}")
                return False
            
            # Update the status
            updated_line = original_line.replace('⏳', '✅', 1)
            
            # Add completion timestamp if there's room
            if len(updated_line.strip()) < 100:  # Only add timestamp if line isn't too long
                updated_line = updated_line.rstrip() + f" *(completed: {datetime.now().strftime('%Y-%m-%d %H:%M')})*"
            
            # Replace the line
            lines[line_index] = updated_line
            
            # Write back to file
            with open(self.master_todo_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            # Extract task title for logging
            task_title = self.extract_task_title(original_line)
            
            # Log the completion
            self.log_task_completion(task_title, line_number, completion_details)
            
            logger.info(f"Updated task status: {task_title} (line {line_number})")
            return True
        
        except Exception as e:
            logger.error(f"Error updating task status: {e}")
            return False
    
    def extract_task_title(self, line: str) -> str:
        """Extract task title from line"""
        # Remove prefixes and clean up
        clean_line = re.sub(r'^(⏳|✅)\s*', '', line)
        clean_line = re.sub(r'\(🔴 critical\)', '', clean_line)
        clean_line = re.sub(r'\(🟠 high\)', '', clean_line)
        clean_line = re.sub(r'\(🟡 medium\)', '', clean_line)
        clean_line = re.sub(r'\(🟢 low\)', '', clean_line)
        
        return clean_line.strip()[:100]  # Limit to 100 characters
    
    def update_multiple_tasks(self, task_updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Update multiple tasks at once"""
        results = {
            'successful': [],
            'failed': [],
            'total_updated': 0
        }
        
        for update in task_updates:
            line_number = update.get('line_number')
            completion_details = update.get('completion_details', '')
            
            if not line_number:
                results['failed'].append({'error': 'Missing line_number', 'update': update})
                continue
            
            success = self.update_task_status_in_file(line_number, 'completed', completion_details)
            
            if success:
                results['successful'].append(update)
                results['total_updated'] += 1
            else:
                results['failed'].append(update)
        
        logger.info(f"Updated {results['total_updated']} tasks successfully, {len(results['failed'])} failed")
        return results
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """Get current task statistics"""
        if not self.master_todo_file.exists():
            return {'error': 'Master todo file not found'}
        
        try:
            with open(self.master_todo_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            pending_count = 0
            completed_count = 0
            in_progress_count = 0
            blocked_count = 0
            
            for line in lines:
                line = line.strip()
                
                # Skip headers and metadata
                if (line.startswith('#') or 
                    line.startswith('##') or 
                    line.startswith('###') or
                    line.startswith('**') and 'tasks' in line.lower() or
                    line.startswith('*') and 'tasks' in line.lower() or
                    line.startswith('📊') or
                    line.startswith('📋') or
                    line.startswith('####') or
                    line.startswith('*Source*') or
                    line.startswith('*Details*') or
                    '... and' in line or
                    'real todos' in line.lower()):
                    continue
                
                # Check for task lines (including those starting with -)
                if ('⏳' in line and not line.startswith('###') and not line.startswith('**') and 'tasks' not in line.lower()):
                    pending_count += 1
                elif ('✅' in line and not line.startswith('###') and not line.startswith('**') and 'tasks' not in line.lower()):
                    completed_count += 1
                elif '[in-progress]' in line.lower():
                    in_progress_count += 1
                elif '[blocked]' in line.lower():
                    blocked_count += 1
            
            total_tasks = pending_count + completed_count + in_progress_count + blocked_count
            completion_rate = completed_count / total_tasks if total_tasks > 0 else 0
            
            # Load completion log for additional stats
            log_data = self.load_completion_log()
            
            return {
                'total_tasks': total_tasks,
                'pending_tasks': pending_count,
                'completed_tasks': completed_count,
                'in_progress_tasks': in_progress_count,
                'blocked_tasks': blocked_count,
                'completion_rate': completion_rate,
                'tasks_completed_today': len([c for c in log_data['completions'] 
                                            if c['completed_at'].startswith(datetime.now().strftime('%Y-%m-%d'))]),
                'total_completions_logged': log_data['total_completed'],
                'last_updated': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {'error': f'Error analyzing tasks: {e}'}
    
    def generate_completion_report(self) -> str:
        """Generate a completion report"""
        stats = self.get_task_statistics()
        log_data = self.load_completion_log()
        
        if 'error' in stats:
            return f"Error: {stats['error']}"
        
        report = f"""
📊 TASK COMPLETION REPORT
========================

Current Status:
- Total Tasks: {stats['total_tasks']}
- Pending: {stats['pending_tasks']}
- Completed: {stats['completed_tasks']}
- In Progress: {stats['in_progress_tasks']}
- Blocked: {stats['blocked_tasks']}
- Completion Rate: {stats['completion_rate']:.1%}

Today's Activity:
- Tasks Completed Today: {stats['tasks_completed_today']}
- Total Completions Logged: {stats['total_completions_logged']}

Recent Completions:
"""
        
        # Add recent completions
        recent_completions = log_data['completions'][-5:]  # Last 5 completions
        for i, completion in enumerate(recent_completions, 1):
            report += f"{i}. {completion['task_title']}\n"
            report += f"   Completed: {completion['completed_at']}\n"
            if completion.get('completion_details'):
                report += f"   Details: {completion['completion_details']}\n"
            report += "\n"
        
        return report

def main():
    """Main function for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Task Completion Updater')
    parser.add_argument('--update', type=int, help='Update task at line number')
    parser.add_argument('--details', type=str, help='Completion details')
    parser.add_argument('--stats', action='store_true', help='Show task statistics')
    parser.add_argument('--report', action='store_true', help='Generate completion report')
    
    args = parser.parse_args()
    
    updater = TaskCompletionUpdater()
    
    if args.update:
        success = updater.update_task_status_in_file(args.update, 'completed', args.details or '')
        if success:
            print(f"✅ Successfully updated task at line {args.update}")
        else:
            print(f"❌ Failed to update task at line {args.update}")
    
    elif args.stats:
        stats = updater.get_task_statistics()
        if 'error' in stats:
            print(f"Error: {stats['error']}")
        else:
            print("📊 TASK STATISTICS")
            print("=" * 50)
            for key, value in stats.items():
                if key != 'last_updated':
                    print(f"{key.replace('_', ' ').title()}: {value}")
    
    elif args.report:
        print(updater.generate_completion_report())
    
    else:
        print("Task Completion Updater - Use --help for options")

if __name__ == "__main__":
    main()
