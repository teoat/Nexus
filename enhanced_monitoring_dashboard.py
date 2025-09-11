#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
📊 Enhanced Monitoring Dashboard for Real Continuous Todo Automation
Shows detailed metrics: workers, jobs completed, work status, remaining jobs
"""

import os
import sys
import json
import time
import psutil
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedMonitoringDashboard:
    """Enhanced monitoring dashboard with detailed metrics"""
    
    def __init__(self, project_root: str = "/Users/Arief/Desktop/Nexus"):
        self.project_root = Path(project_root)
        self.status_file = self.project_root / "real_automation_status.json"
        self.config_file = self.project_root / "real_automation_config.json"
        self.log_file = self.project_root / "real_automation.log"
        self.pid_file = self.project_root / "real_automation.pid"
        self.master_todo_file = self.project_root / "master_todo.md"
        
        # Task tracking
        self.task_history = []
        self.completion_history = []
        
    def get_system_resources(self) -> Dict[str, Any]:
        """Get current system resource usage"""
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        disk = psutil.disk_usage('/')
        
        return {
            'timestamp': datetime.now().isoformat(),
            'cpu': {
                'usage_percent': cpu_percent,
                'count': psutil.cpu_count(),
                'freq': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            },
            'memory': {
                'total_gb': memory.total / (1024**3),
                'available_gb': memory.available / (1024**3),
                'used_percent': memory.percent,
                'used_gb': memory.used / (1024**3)
            },
            'disk': {
                'total_gb': disk.total / (1024**3),
                'used_gb': disk.used / (1024**3),
                'free_gb': disk.free / (1024**3),
                'usage_percent': (disk.used / disk.total) * 100
            }
        }
    
    def is_automation_running(self) -> bool:
        """Check if automation system is running"""
        if not self.pid_file.exists():
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            return psutil.pid_exists(pid)
        except (ValueError, FileNotFoundError):
            return False
    
    def get_automation_process_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the automation process"""
        if not self.is_automation_running():
            return None
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            process = psutil.Process(pid)
            
            return {
                'pid': pid,
                'name': process.name(),
                'cmdline': ' '.join(process.cmdline()),
                'cpu_percent': process.cpu_percent(),
                'memory_percent': process.memory_percent(),
                'memory_mb': process.memory_info().rss / (1024**2),
                'create_time': datetime.fromtimestamp(process.create_time()).isoformat(),
                'status': process.status(),
                'num_threads': process.num_threads()
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied, ValueError):
            return None
    
    def get_automation_status(self) -> Optional[Dict[str, Any]]:
        """Get automation system status"""
        if not self.status_file.exists():
            return None
        
        try:
            with open(self.status_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return None
    
    def analyze_master_todo(self) -> Dict[str, Any]:
        """Analyze master todo file for current task status"""
        if not self.master_todo_file.exists():
            return {'error': 'Master todo file not found'}
        
        try:
            with open(self.master_todo_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Count different types of tasks
            pending_tasks = []
            completed_tasks = []
            in_progress_tasks = []
            blocked_tasks = []
            
            for line_num, line in enumerate(lines, 1):
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
                
                # Categorize tasks (including those starting with -)
                if ('⏳' in line and not line.startswith('###') and not line.startswith('**') and 'tasks' not in line.lower()):
                    pending_tasks.append({
                        'line': line_num,
                        'content': line,
                        'title': self.extract_task_title(line)
                    })
                elif ('✅' in line and not line.startswith('###') and not line.startswith('**') and 'tasks' not in line.lower()):
                    completed_tasks.append({
                        'line': line_num,
                        'content': line,
                        'title': self.extract_task_title(line)
                    })
                elif '[in-progress]' in line.lower() or '[doing]' in line.lower():
                    in_progress_tasks.append({
                        'line': line_num,
                        'content': line,
                        'title': self.extract_task_title(line)
                    })
                elif '[blocked]' in line.lower():
                    blocked_tasks.append({
                        'line': line_num,
                        'content': line,
                        'title': self.extract_task_title(line)
                    })
            
            return {
                'total_lines': len(lines),
                'pending_tasks': len(pending_tasks),
                'completed_tasks': len(completed_tasks),
                'in_progress_tasks': len(in_progress_tasks),
                'blocked_tasks': len(blocked_tasks),
                'total_real_tasks': len(pending_tasks) + len(completed_tasks) + len(in_progress_tasks) + len(blocked_tasks),
                'completion_rate': len(completed_tasks) / (len(pending_tasks) + len(completed_tasks) + len(in_progress_tasks) + len(blocked_tasks)) if (len(pending_tasks) + len(completed_tasks) + len(in_progress_tasks) + len(blocked_tasks)) > 0 else 0,
                'pending_task_list': pending_tasks[:10],  # Show first 10 pending tasks
                'completed_task_list': completed_tasks[-5:],  # Show last 5 completed tasks
                'last_updated': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {'error': f'Error analyzing master todo: {e}'}
    
    def extract_task_title(self, line: str) -> str:
        """Extract task title from line"""
        # Remove prefixes and clean up
        clean_line = re.sub(r'^(⏳|✅)\s*', '', line)
        clean_line = re.sub(r'\(🔴 critical\)', '', clean_line)
        clean_line = re.sub(r'\(🟠 high\)', '', clean_line)
        clean_line = re.sub(r'\(🟡 medium\)', '', clean_line)
        clean_line = re.sub(r'\(🟢 low\)', '', clean_line)
        
        return clean_line.strip()[:80]  # Limit to 80 characters
    
    def get_worker_metrics(self, status_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract worker metrics from status data"""
        if not status_data or 'cycle' not in status_data:
            return {'total_workers': 0, 'active_workers': 0, 'phase_workers': {}}
        
        cycle = status_data['cycle']
        total_workers = 0
        active_workers = 0
        phase_workers = {}
        
        if 'phases' in cycle:
            for phase_result in cycle['phases']:
                phase_name = phase_result.get('phase', 'unknown')
                workers_used = phase_result.get('workers_used', 0)
                total_workers += workers_used
                active_workers += workers_used
                phase_workers[phase_name] = {
                    'workers_used': workers_used,
                    'tasks_completed': phase_result.get('completed', 0),
                    'tasks_failed': phase_result.get('failed', 0),
                    'execution_time': phase_result.get('execution_time', 0),
                    'success_rate': phase_result.get('success_rate', 0)
                }
        
        return {
            'total_workers': total_workers,
            'active_workers': active_workers,
            'phase_workers': phase_workers,
            'worker_efficiency': active_workers / max(total_workers, 1) if total_workers > 0 else 0
        }
    
    def get_job_metrics(self, status_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract job completion metrics"""
        if not status_data or 'cycle' not in status_data:
            return {
                'jobs_completed': 0,
                'jobs_failed': 0,
                'jobs_total': 0,
                'success_rate': 0,
                'cycle_time': 0,
                'jobs_per_minute': 0
            }
        
        cycle = status_data['cycle']
        
        return {
            'jobs_completed': cycle.get('completed', 0),
            'jobs_failed': cycle.get('failed', 0),
            'jobs_total': cycle.get('total_tasks', 0),
            'success_rate': cycle.get('success_rate', 0),
            'cycle_time': cycle.get('cycle_time', 0),
            'jobs_per_minute': (cycle.get('completed', 0) / max(cycle.get('cycle_time', 1) / 60, 0.1)) if cycle.get('cycle_time', 0) > 0 else 0
        }
    
    def get_recent_work_completed(self, status_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get list of recently completed work"""
        if not status_data or 'cycle' not in status_data or 'phases' not in status_data['cycle']:
            return []
        
        recent_work = []
        cycle = status_data['cycle']
        
        for phase_result in cycle['phases']:
            if 'task_results' in phase_result:
                for task, result in phase_result['task_results']:
                    if hasattr(result, 'success') and result.success:
                        recent_work.append({
                            'task_title': task.title,
                            'phase': phase_result.get('phase', 'unknown'),
                            'execution_time': result.execution_time,
                            'output': result.output,
                            'timestamp': datetime.now().isoformat()
                        })
        
        return recent_work[-10:]  # Return last 10 completed tasks
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive monitoring report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'system_resources': self.get_system_resources(),
            'automation_status': {
                'running': self.is_automation_running(),
                'process_info': self.get_automation_process_info(),
                'status_data': self.get_automation_status()
            },
            'master_todo_analysis': self.analyze_master_todo(),
            'worker_metrics': {},
            'job_metrics': {},
            'recent_work_completed': [],
            'summary': {}
        }
        
        # Calculate detailed metrics
        status_data = report['automation_status']['status_data']
        if status_data:
            report['worker_metrics'] = self.get_worker_metrics(status_data)
            report['job_metrics'] = self.get_job_metrics(status_data)
            report['recent_work_completed'] = self.get_recent_work_completed(status_data)
        
        # Generate summary
        report['summary'] = self.generate_summary(report)
        
        return report
    
    def generate_summary(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary"""
        automation_running = report['automation_status']['running']
        todo_analysis = report['master_todo_analysis']
        worker_metrics = report['worker_metrics']
        job_metrics = report['job_metrics']
        
        summary = {
            'status': 'RUNNING' if automation_running else 'STOPPED',
            'total_pending_jobs': todo_analysis.get('pending_tasks', 0),
            'total_completed_jobs': todo_analysis.get('completed_tasks', 0),
            'completion_rate': f"{todo_analysis.get('completion_rate', 0):.1%}",
            'active_workers': worker_metrics.get('active_workers', 0),
            'jobs_completed_this_cycle': job_metrics.get('jobs_completed', 0),
            'success_rate': f"{job_metrics.get('success_rate', 0):.1%}",
            'jobs_per_minute': f"{job_metrics.get('jobs_per_minute', 0):.1f}",
            'estimated_time_to_completion': self.calculate_estimated_completion(todo_analysis, job_metrics)
        }
        
        return summary
    
    def calculate_estimated_completion(self, todo_analysis: Dict[str, Any], job_metrics: Dict[str, Any]) -> str:
        """Calculate estimated time to complete all pending jobs"""
        pending_jobs = todo_analysis.get('pending_tasks', 0)
        jobs_per_minute = job_metrics.get('jobs_per_minute', 0)
        
        if pending_jobs == 0:
            return "All tasks completed!"
        
        if jobs_per_minute == 0:
            return "Cannot estimate (no job completion rate)"
        
        estimated_minutes = pending_jobs / jobs_per_minute
        
        if estimated_minutes < 60:
            return f"{estimated_minutes:.1f} minutes"
        elif estimated_minutes < 1440:  # Less than 24 hours
            return f"{estimated_minutes / 60:.1f} hours"
        else:
            return f"{estimated_minutes / 1440:.1f} days"
    
    def print_enhanced_dashboard(self):
        """Print enhanced monitoring dashboard"""
        report = self.generate_comprehensive_report()
        
        print("=" * 100)
        print("📊 ENHANCED CONTINUOUS TODO AUTOMATION DASHBOARD")
        print("=" * 100)
        print(f"Timestamp: {report['timestamp']}")
        print()
        
        # System Status
        automation = report['automation_status']
        print("🚀 AUTOMATION SYSTEM STATUS")
        print("-" * 50)
        
        if automation['running']:
            print("✅ Status: RUNNING")
            if automation['process_info']:
                proc = automation['process_info']
                print(f"   PID: {proc['pid']}")
                print(f"   CPU: {proc['cpu_percent']:.1f}%")
                print(f"   Memory: {proc['memory_mb']:.1f}MB ({proc['memory_percent']:.1f}%)")
                print(f"   Threads: {proc['num_threads']}")
                print(f"   Started: {proc['create_time']}")
        else:
            print("❌ Status: NOT RUNNING")
        
        print()
        
        # Worker Metrics
        worker_metrics = report['worker_metrics']
        print("👥 WORKER METRICS")
        print("-" * 50)
        print(f"Total Workers Used: {worker_metrics.get('total_workers', 0)}")
        print(f"Active Workers: {worker_metrics.get('active_workers', 0)}")
        print(f"Worker Efficiency: {worker_metrics.get('worker_efficiency', 0):.1%}")
        
        if worker_metrics.get('phase_workers'):
            print("\n📋 Phase-wise Worker Allocation:")
            for phase, metrics in worker_metrics['phase_workers'].items():
                print(f"  {phase.upper()}:")
                print(f"    Workers: {metrics['workers_used']}")
                print(f"    Completed: {metrics['tasks_completed']}")
                print(f"    Failed: {metrics['tasks_failed']}")
                print(f"    Success Rate: {metrics['success_rate']:.1%}")
                print(f"    Execution Time: {metrics['execution_time']:.2f}s")
        
        print()
        
        # Job Metrics
        job_metrics = report['job_metrics']
        print("📈 JOB COMPLETION METRICS")
        print("-" * 50)
        print(f"Jobs Completed This Cycle: {job_metrics.get('jobs_completed', 0)}")
        print(f"Jobs Failed This Cycle: {job_metrics.get('jobs_failed', 0)}")
        print(f"Total Jobs Processed: {job_metrics.get('jobs_total', 0)}")
        print(f"Success Rate: {job_metrics.get('success_rate', 0):.1%}")
        print(f"Cycle Time: {job_metrics.get('cycle_time', 0):.2f}s")
        print(f"Jobs Per Minute: {job_metrics.get('jobs_per_minute', 0):.1f}")
        
        print()
        
        # Master Todo Analysis
        todo_analysis = report['master_todo_analysis']
        print("📋 MASTER TODO ANALYSIS")
        print("-" * 50)
        print(f"Total Real Tasks: {todo_analysis.get('total_real_tasks', 0)}")
        print(f"Pending Jobs: {todo_analysis.get('pending_tasks', 0)}")
        print(f"Completed Jobs: {todo_analysis.get('completed_tasks', 0)}")
        print(f"In Progress: {todo_analysis.get('in_progress_tasks', 0)}")
        print(f"Blocked: {todo_analysis.get('blocked_tasks', 0)}")
        print(f"Completion Rate: {todo_analysis.get('completion_rate', 0):.1%}")
        
        # Show pending tasks
        if todo_analysis.get('pending_task_list'):
            print("\n⏳ Next Pending Tasks:")
            for i, task in enumerate(todo_analysis['pending_task_list'][:5], 1):
                print(f"  {i}. {task['title']}")
        
        # Show recently completed tasks
        if todo_analysis.get('completed_task_list'):
            print("\n✅ Recently Completed Tasks:")
            for i, task in enumerate(todo_analysis['completed_task_list'], 1):
                print(f"  {i}. {task['title']}")
        
        print()
        
        # Recent Work Completed
        recent_work = report['recent_work_completed']
        if recent_work:
            print("🔄 RECENT WORK COMPLETED")
            print("-" * 50)
            for i, work in enumerate(recent_work[-5:], 1):  # Show last 5
                print(f"  {i}. {work['task_title']}")
                print(f"     Phase: {work['phase']}")
                print(f"     Time: {work['execution_time']:.2f}s")
                print(f"     Output: {work['output'][:60]}...")
                print()
        
        # Executive Summary
        summary = report['summary']
        print("📊 EXECUTIVE SUMMARY")
        print("-" * 50)
        print(f"System Status: {summary['status']}")
        print(f"Pending Jobs: {summary['total_pending_jobs']}")
        print(f"Completed Jobs: {summary['total_completed_jobs']}")
        print(f"Overall Completion: {summary['completion_rate']}")
        print(f"Active Workers: {summary['active_workers']}")
        print(f"Jobs/Minute: {summary['jobs_per_minute']}")
        print(f"Estimated Time to Completion: {summary['estimated_time_to_completion']}")
        
        print()
        print("=" * 100)
    
    def save_detailed_report(self, filename: Optional[str] = None):
        """Save detailed report to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"enhanced_monitoring_report_{timestamp}.json"
        
        report = self.generate_comprehensive_report()
        
        report_file = self.project_root / filename
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Detailed report saved to: {report_file}")
        return report_file
    
    def monitor_continuously(self, interval: int = 30):
        """Monitor system continuously with enhanced dashboard"""
        print(f"🔍 Starting enhanced continuous monitoring (interval: {interval}s)")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                # Clear screen
                os.system('clear' if os.name == 'posix' else 'cls')
                
                # Print enhanced dashboard
                self.print_enhanced_dashboard()
                
                # Wait for next check
                time.sleep(interval)
        
        except KeyboardInterrupt:
            print("\n👋 Enhanced monitoring stopped")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Enhanced Monitoring Dashboard')
    parser.add_argument('--dashboard', '-d', action='store_true', help='Show enhanced dashboard')
    parser.add_argument('--monitor', '-m', action='store_true', help='Start continuous monitoring')
    parser.add_argument('--interval', '-i', type=int, default=30, help='Monitoring interval in seconds')
    parser.add_argument('--report', '-r', action='store_true', help='Generate and print dashboard report')
    parser.add_argument('--save', '-s', action='store_true', help='Save detailed report to file')
    parser.add_argument('--output', '-o', type=str, help='Output filename for saved report')
    
    args = parser.parse_args()
    
    dashboard = EnhancedMonitoringDashboard()
    
    if args.monitor:
        dashboard.monitor_continuously(args.interval)
    elif args.dashboard or args.report:
        dashboard.print_enhanced_dashboard()
    elif args.save:
        dashboard.save_detailed_report(args.output)
    else:
        # Default: show enhanced dashboard
        dashboard.print_enhanced_dashboard()

if __name__ == "__main__":
    main()
