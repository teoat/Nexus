#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
System Health Monitor
====================

Comprehensive health monitoring for all system components:
- CPU, Memory, Disk usage
- Task processing rates
- Error rates and types
- Worker efficiency
- File system health
"""

import os
import sys
import json
import time
import psutil
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import threading
import queue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemHealthMonitor:
    def __init__(self, workspace_root: str = "/Users/Arief/Desktop/Nexus"):
        self.workspace_root = Path(workspace_root)
        self.metrics = {}
        self.alerts = []
        self.alert_queue = queue.Queue()
        self.monitoring = False
        self.monitor_thread = None
        
        # Health thresholds
        self.thresholds = {
            'cpu_percent': 90.0,
            'memory_percent': 90.0,
            'disk_percent': 90.0,
            'error_rate': 0.1,
            'worker_efficiency': 0.1,
            'task_processing_rate': 0.1
        }
        
        # Alert channels
        self.alert_channels = ['console', 'log', 'file']
        
        # Historical data
        self.historical_data = []
        self.max_history = 1000
    
    def check_system_health(self) -> Dict[str, Any]:
        """Check comprehensive system health"""
        health = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0],
            'process_count': len(psutil.pids()),
            'python_processes': 0,
            'network_io': psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {},
            'disk_io': psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {}
        }
        
        # Count Python processes
        for proc in psutil.process_iter(['name']):
            try:
                if 'python' in proc.info['name'].lower():
                    health['python_processes'] += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Calculate derived metrics
        health['cpu_available'] = 100 - health['cpu_percent']
        health['memory_available'] = 100 - health['memory_percent']
        health['disk_available'] = 100 - health['disk_percent']
        
        return health
    
    def check_task_processing_health(self) -> Dict[str, Any]:
        """Check task processing health"""
        master_todo_file = self.workspace_root / "master_todo.md"
        
        if not master_todo_file.exists():
            return {'error': 'Master todo file not found'}
        
        try:
            with open(master_todo_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            total_tasks = 0
            pending_tasks = 0
            completed_tasks = 0
            in_progress_tasks = 0
            
            for line in lines:
                line = line.strip()
                if line.startswith('-') and ('⏳' in line or '✅' in line):
                    total_tasks += 1
                    if '⏳' in line and '✅' not in line:
                        if 'in progress' in line.lower():
                            in_progress_tasks += 1
                        else:
                            pending_tasks += 1
                    elif '✅' in line:
                        completed_tasks += 1
            
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            progress_rate = (in_progress_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            return {
                'total_tasks': total_tasks,
                'pending_tasks': pending_tasks,
                'completed_tasks': completed_tasks,
                'in_progress_tasks': in_progress_tasks,
                'completion_rate': completion_rate,
                'progress_rate': progress_rate,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': f'Error reading master todo: {e}'}
    
    def check_file_system_health(self) -> Dict[str, Any]:
        """Check file system health"""
        critical_files = [
            'master_todo.md',
            'nexus_comprehensive_sot.json',
            'nexus_events.json',
            'nexus_sot_config.json'
        ]
        
        file_health = {
            'critical_files': {},
            'workspace_size': 0,
            'file_count': 0,
            'directory_count': 0
        }
        
        # Check critical files
        for file_name in critical_files:
            file_path = self.workspace_root / file_name
            file_health['critical_files'][file_name] = {
                'exists': file_path.exists(),
                'size': file_path.stat().st_size if file_path.exists() else 0,
                'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat() if file_path.exists() else None
            }
        
        # Calculate workspace size and file count
        try:
            for root, dirs, files in os.walk(self.workspace_root):
                file_health['directory_count'] += len(dirs)
                for file in files:
                    file_path = Path(root) / file
                    try:
                        file_health['workspace_size'] += file_path.stat().st_size
                        file_health['file_count'] += 1
                    except (OSError, FileNotFoundError):
                        continue
        except Exception as e:
            file_health['error'] = str(e)
        
        return file_health
    
    def check_process_health(self) -> Dict[str, Any]:
        """Check process health"""
        nexus_processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent', 'create_time']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if 'nexus' in cmdline.lower() or 'robust_parallel' in cmdline.lower():
                        nexus_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cmdline': cmdline,
                            'cpu_percent': proc.info['cpu_percent'],
                            'memory_percent': proc.info['memory_percent'],
                            'create_time': datetime.fromtimestamp(proc.info['create_time']).isoformat(),
                            'uptime': time.time() - proc.info['create_time']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            logger.error(f"Error checking processes: {e}")
        
        return {
            'nexus_processes': nexus_processes,
            'total_nexus_processes': len(nexus_processes),
            'system_processes': len(psutil.pids())
        }
    
    def generate_alerts(self, health_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate alerts based on health data"""
        alerts = []
        
        # CPU alerts
        if health_data['cpu_percent'] > self.thresholds['cpu_percent']:
            alerts.append({
                'severity': 'high',
                'type': 'cpu_usage',
                'message': f"High CPU usage detected: {health_data['cpu_percent']:.1f}%",
                'value': health_data['cpu_percent'],
                'threshold': self.thresholds['cpu_percent']
            })
        
        # Memory alerts
        if health_data['memory_percent'] > self.thresholds['memory_percent']:
            alerts.append({
                'severity': 'high',
                'type': 'memory_usage',
                'message': f"High memory usage detected: {health_data['memory_percent']:.1f}%",
                'value': health_data['memory_percent'],
                'threshold': self.thresholds['memory_percent']
            })
        
        # Disk alerts
        if health_data['disk_percent'] > self.thresholds['disk_percent']:
            alerts.append({
                'severity': 'high',
                'type': 'disk_usage',
                'message': f"High disk usage detected: {health_data['disk_percent']:.1f}%",
                'value': health_data['disk_percent'],
                'threshold': self.thresholds['disk_percent']
            })
        
        # Process alerts
        if health_data['python_processes'] == 0:
            alerts.append({
                'severity': 'medium',
                'type': 'no_python_processes',
                'message': "No Python processes detected",
                'value': health_data['python_processes'],
                'threshold': 1
            })
        
        return alerts
    
    def send_alert(self, alert: Dict[str, Any]):
        """Send alert to configured channels"""
        alert['timestamp'] = datetime.now().isoformat()
        
        for channel in self.alert_channels:
            try:
                if channel == 'console':
                    severity_emoji = {
                        'high': '🚨',
                        'medium': '⚠️',
                        'low': 'ℹ️'
                    }.get(alert['severity'], '❓')
                    
                    print(f"{severity_emoji} ALERT: {alert['message']}")
                
                elif channel == 'log':
                    logger.warning(f"ALERT: {alert['message']}")
                
                elif channel == 'file':
                    alert_file = self.workspace_root / "system_alerts.json"
                    alerts = []
                    
                    if alert_file.exists():
                        with open(alert_file, 'r') as f:
                            alerts = json.load(f)
                    
                    alerts.append(alert)
                    
                    # Keep only last 100 alerts
                    if len(alerts) > 100:
                        alerts = alerts[-100:]
                    
                    with open(alert_file, 'w') as f:
                        json.dump(alerts, f, indent=2)
                
            except Exception as e:
                logger.error(f"Error sending alert to {channel}: {e}")
    
    def calculate_health_score(self, health_data: Dict[str, Any]) -> float:
        """Calculate overall health score (0-100)"""
        scores = []
        
        # CPU score (inverted - lower usage is better)
        cpu_score = max(0, 100 - health_data['cpu_percent'])
        scores.append(cpu_score)
        
        # Memory score (inverted - lower usage is better)
        memory_score = max(0, 100 - health_data['memory_percent'])
        scores.append(memory_score)
        
        # Disk score (inverted - lower usage is better)
        disk_score = max(0, 100 - health_data['disk_percent'])
        scores.append(disk_score)
        
        # Process score (higher is better)
        process_score = min(100, health_data['python_processes'] * 20)  # 20 points per process
        scores.append(process_score)
        
        # Calculate weighted average
        weights = [0.3, 0.3, 0.2, 0.2]  # CPU, Memory, Disk, Processes
        health_score = sum(score * weight for score, weight in zip(scores, weights))
        
        return round(health_score, 1)
    
    def get_comprehensive_health(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        system_health = self.check_system_health()
        task_health = self.check_task_processing_health()
        file_health = self.check_file_system_health()
        process_health = self.check_process_health()
        
        # Generate alerts
        alerts = self.generate_alerts(system_health)
        
        # Calculate health score
        health_score = self.calculate_health_score(system_health)
        
        comprehensive_health = {
            'timestamp': datetime.now().isoformat(),
            'health_score': health_score,
            'system_health': system_health,
            'task_health': task_health,
            'file_health': file_health,
            'process_health': process_health,
            'alerts': alerts,
            'alert_count': len(alerts),
            'status': 'healthy' if health_score > 80 else 'warning' if health_score > 60 else 'critical'
        }
        
        # Store in historical data
        self.historical_data.append(comprehensive_health)
        if len(self.historical_data) > self.max_history:
            self.historical_data = self.historical_data[-self.max_history:]
        
        return comprehensive_health
    
    def start_monitoring(self, interval: int = 30):
        """Start continuous monitoring"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        logger.info(f"Health monitoring started with {interval}s interval")
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("Health monitoring stopped")
    
    def _monitor_loop(self, interval: int):
        """Monitoring loop"""
        while self.monitoring:
            try:
                health_data = self.get_comprehensive_health()
                
                # Send alerts
                for alert in health_data['alerts']:
                    self.send_alert(alert)
                
                # Log health status
                logger.info(f"Health Score: {health_data['health_score']}/100, "
                          f"Status: {health_data['status']}, "
                          f"Alerts: {health_data['alert_count']}")
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
            
            time.sleep(interval)
    
    def save_health_report(self, filename: str = "system_health_report.json"):
        """Save comprehensive health report"""
        health_data = self.get_comprehensive_health()
        report_file = self.workspace_root / filename
        
        with open(report_file, 'w') as f:
            json.dump(health_data, f, indent=2)
        
        logger.info(f"Health report saved to: {report_file}")
        return report_file

def main():
    """Main function"""
    monitor = SystemHealthMonitor()
    
    print("🏥 System Health Monitor")
    print("=" * 40)
    
    # Get comprehensive health
    health_data = monitor.get_comprehensive_health()
    
    print(f"📊 Health Score: {health_data['health_score']}/100")
    print(f"📈 Status: {health_data['status'].upper()}")
    print(f"🚨 Alerts: {health_data['alert_count']}")
    
    print(f"\n💻 System Resources:")
    print(f"  CPU: {health_data['system_health']['cpu_percent']:.1f}%")
    print(f"  Memory: {health_data['system_health']['memory_percent']:.1f}%")
    print(f"  Disk: {health_data['system_health']['disk_percent']:.1f}%")
    print(f"  Python Processes: {health_data['system_health']['python_processes']}")
    
    print(f"\n📋 Task Health:")
    if 'error' not in health_data['task_health']:
        print(f"  Total Tasks: {health_data['task_health']['total_tasks']}")
        print(f"  Pending: {health_data['task_health']['pending_tasks']}")
        print(f"  Completed: {health_data['task_health']['completed_tasks']}")
        print(f"  Completion Rate: {health_data['task_health']['completion_rate']:.1f}%")
    else:
        print(f"  Error: {health_data['task_health']['error']}")
    
    print(f"\n🔄 Process Health:")
    print(f"  Nexus Processes: {health_data['process_health']['total_nexus_processes']}")
    print(f"  System Processes: {health_data['process_health']['system_processes']}")
    
    if health_data['alerts']:
        print(f"\n🚨 Active Alerts:")
        for alert in health_data['alerts']:
            severity_emoji = {
                'high': '🚨',
                'medium': '⚠️',
                'low': 'ℹ️'
            }.get(alert['severity'], '❓')
            print(f"  {severity_emoji} {alert['message']}")
    
    # Save health report
    report_file = monitor.save_health_report()
    print(f"\n📄 Health report saved: {report_file}")

if __name__ == "__main__":
    main()
