#!/usr/bin/env python3
"""
🚀 Intelligent Auto-Scaler for Robust Parallel Worker System
Dynamic scaling based on system capabilities and task load
"""

import os
import sys
import json
import time
import psutil
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import subprocess
import signal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('intelligent_autoscaler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """System performance metrics"""
    cpu_percent: float
    memory_percent: float
    cpu_count: int
    memory_total_gb: float
    load_average: Tuple[float, float, float]
    timestamp: datetime

@dataclass
class ScalingDecision:
    """Auto-scaling decision"""
    action: str  # 'scale_up', 'scale_down', 'maintain'
    current_workers: int
    recommended_workers: int
    current_jobs: int
    recommended_jobs: int
    reason: str
    cpu_target: float
    memory_target: float
    confidence: float

class IntelligentAutoScaler:
    """Intelligent auto-scaler for dynamic resource management"""
    
    def __init__(self, project_root: str = "/Users/Arief/Desktop/Nexus"):
        self.project_root = Path(project_root)
        self.master_todo_file = self.project_root / "master_todo.md"
        self.status_file = self.project_root / "robust_parallel_worker_status.json"
        self.pid_file = self.project_root / "robust_parallel_system.pid"
        
        # Scaling configuration
        self.config = {
            "cpu_target_standard": 60.0,  # 60% CPU usage target
            "cpu_target_refinement": 70.0,  # 70% CPU usage for refinement
            "memory_target": 60.0,  # 60% memory usage target
            "min_workers": 1,
            "max_workers": 32,
            "base_jobs_per_worker": 2,
            "scaling_cooldown": 30,  # seconds between scaling decisions
            "graceful_down_threshold": 50,  # tasks pending for graceful downscale
            "metrics_window": 5,  # number of metrics to average
            "scale_up_threshold": 0.8,  # 80% of target triggers scale up
            "scale_down_threshold": 0.4,  # 40% of target triggers scale down
        }
        
        # State tracking
        self.current_workers = 12
        self.current_jobs = 24
        self.last_scaling_time = 0
        self.metrics_history = []
        self.scaling_history = []
        self.is_monitoring = False
        self.monitor_thread = None
        
        # PID tracking
        self.target_pid = None
        
        logger.info("Intelligent Auto-Scaler initialized")
    
    def get_system_metrics(self) -> SystemMetrics:
        """Get current system performance metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            cpu_count = psutil.cpu_count()
            memory_total_gb = memory.total / (1024**3)
            load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else (0.0, 0.0, 0.0)
            
            return SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                cpu_count=cpu_count,
                memory_total_gb=memory_total_gb,
                load_average=load_avg,
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return SystemMetrics(
                cpu_percent=0.0,
                memory_percent=0.0,
                cpu_count=1,
                memory_total_gb=1.0,
                load_average=(0.0, 0.0, 0.0),
                timestamp=datetime.now()
            )
    
    def get_task_metrics(self) -> Dict[str, int]:
        """Get current task metrics from master_todo.md"""
        try:
            if not self.master_todo_file.exists():
                return {"pending": 0, "completed": 0, "total": 0}
            
            with open(self.master_todo_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            pending_count = content.count('⏳')
            completed_count = content.count('✅')
            total_count = pending_count + completed_count
            
            return {
                "pending": pending_count,
                "completed": completed_count,
                "total": total_count
            }
        except Exception as e:
            logger.error(f"Error getting task metrics: {e}")
            return {"pending": 0, "completed": 0, "total": 0}
    
    def get_current_worker_config(self) -> Dict[str, int]:
        """Get current worker configuration from running process"""
        try:
            # Try to get from status file
            if self.status_file.exists():
                with open(self.status_file, 'r') as f:
                    status = json.load(f)
                    return {
                        "workers": status.get("workers", 12),
                        "jobs": status.get("jobs_processed", 24)
                    }
            
            # Try to get from running process
            if self.pid_file.exists():
                with open(self.pid_file, 'r') as f:
                    pid = int(f.read().strip())
                
                try:
                    process = psutil.Process(pid)
                    cmdline = ' '.join(process.cmdline())
                    
                    # Extract worker count from command line
                    import re
                    worker_match = re.search(r'--max-workers\s+(\d+)', cmdline)
                    if worker_match:
                        workers = int(worker_match.group(1))
                        return {"workers": workers, "jobs": workers * 2}
                except psutil.NoSuchProcess:
                    pass
            
            return {"workers": 12, "jobs": 24}
        except Exception as e:
            logger.error(f"Error getting worker config: {e}")
            return {"workers": 12, "jobs": 24}
    
    def calculate_optimal_scaling(self, metrics: SystemMetrics, task_metrics: Dict[str, int]) -> ScalingDecision:
        """Calculate optimal scaling based on system metrics and task load"""
        
        pending_tasks = task_metrics["pending"]
        completed_tasks = task_metrics["completed"]
        total_tasks = task_metrics["total"]
        
        # Determine scaling mode based on task load
        if pending_tasks < self.config["graceful_down_threshold"]:
            # Graceful downscale mode
            target_cpu = self.config["cpu_target_standard"] * 0.5  # Reduce to 30%
            target_memory = self.config["memory_target"] * 0.5  # Reduce to 30%
            mode = "graceful_down"
        elif pending_tasks > total_tasks * 0.8:
            # High load mode - use refinement targets
            target_cpu = self.config["cpu_target_refinement"]
            target_memory = self.config["memory_target"] * 1.1  # 66%
            mode = "refinement"
        else:
            # Standard mode
            target_cpu = self.config["cpu_target_standard"]
            target_memory = self.config["memory_target"]
            mode = "standard"
        
        # Calculate optimal worker count based on CPU and memory
        cpu_based_workers = int((metrics.cpu_count * target_cpu / 100) * (metrics.cpu_percent / target_cpu))
        memory_based_workers = int((metrics.memory_total_gb * target_memory / 100) / 0.5)  # Assume 0.5GB per worker
        
        # Use the more conservative estimate
        optimal_workers = min(cpu_based_workers, memory_based_workers)
        
        # Apply constraints
        optimal_workers = max(self.config["min_workers"], optimal_workers)
        optimal_workers = min(self.config["max_workers"], optimal_workers)
        
        # Calculate optimal jobs per worker
        if mode == "graceful_down":
            optimal_jobs_per_worker = 1
        elif mode == "refinement":
            optimal_jobs_per_worker = 3
        else:
            optimal_jobs_per_worker = self.config["base_jobs_per_worker"]
        
        optimal_jobs = optimal_workers * optimal_jobs_per_worker
        
        # Determine action
        current_config = self.get_current_worker_config()
        current_workers = current_config["workers"]
        
        if optimal_workers > current_workers * 1.2:
            action = "scale_up"
            reason = f"CPU: {metrics.cpu_percent:.1f}% < {target_cpu}%, Memory: {metrics.memory_percent:.1f}% < {target_memory}%, Mode: {mode}"
        elif optimal_workers < current_workers * 0.8:
            action = "scale_down"
            reason = f"CPU: {metrics.cpu_percent:.1f}%, Memory: {metrics.memory_percent:.1f}%, Mode: {mode}, Pending: {pending_tasks}"
        else:
            action = "maintain"
            reason = f"Optimal range, CPU: {metrics.cpu_percent:.1f}%, Memory: {metrics.memory_percent:.1f}%, Mode: {mode}"
        
        # Calculate confidence based on metrics consistency
        confidence = 0.8
        if len(self.metrics_history) > 3:
            recent_cpu = [m.cpu_percent for m in self.metrics_history[-3:]]
            cpu_variance = max(recent_cpu) - min(recent_cpu)
            if cpu_variance < 10:
                confidence += 0.1
            if cpu_variance > 30:
                confidence -= 0.2
        
        confidence = max(0.3, min(1.0, confidence))
        
        return ScalingDecision(
            action=action,
            current_workers=current_workers,
            recommended_workers=optimal_workers,
            current_jobs=current_config["jobs"],
            recommended_jobs=optimal_jobs,
            reason=reason,
            cpu_target=target_cpu,
            memory_target=target_memory,
            confidence=confidence
        )
    
    def apply_scaling_decision(self, decision: ScalingDecision) -> bool:
        """Apply the scaling decision to the running system"""
        try:
            if decision.action == "maintain":
                logger.info(f"Maintaining current configuration: {decision.current_workers} workers")
                return True
            
            # Check if we can scale (cooldown period)
            current_time = time.time()
            if current_time - self.last_scaling_time < self.config["scaling_cooldown"]:
                logger.info(f"Scaling cooldown active, skipping {decision.action}")
                return False
            
            # Get current PID
            if not self.pid_file.exists():
                logger.error("PID file not found, cannot scale")
                return False
            
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Stop current process
            logger.info(f"Stopping current process (PID: {pid}) for scaling")
            try:
                process = psutil.Process(pid)
                process.terminate()
                process.wait(timeout=10)
            except psutil.NoSuchProcess:
                logger.info("Process already stopped")
            except psutil.TimeoutExpired:
                logger.warning("Force killing process")
                process.kill()
            
            # Wait a moment for cleanup
            time.sleep(2)
            
            # Start with new configuration
            new_workers = decision.recommended_workers
            new_jobs = decision.recommended_jobs
            
            logger.info(f"Starting with new configuration: {new_workers} workers, {new_jobs} jobs")
            
            # Build command
            cmd = [
                "python", "robust_parallel_worker_system.py",
                "--cycles", "0",  # Continuous
                "--interval", "60",
                "--min-todos", str(new_jobs),
                "--max-todos", str(new_jobs * 2),
                "--max-workers", str(new_workers),
                "--max-retries", "5",
                "--parallel"
            ]
            
            # Start new process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=self.project_root
            )
            
            # Update PID file
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # Update current configuration
            self.current_workers = new_workers
            self.current_jobs = new_jobs
            self.last_scaling_time = current_time
            
            # Record scaling action
            self.scaling_history.append({
                "timestamp": datetime.now().isoformat(),
                "action": decision.action,
                "from_workers": decision.current_workers,
                "to_workers": new_workers,
                "from_jobs": decision.current_jobs,
                "to_jobs": new_jobs,
                "reason": decision.reason,
                "confidence": decision.confidence
            })
            
            logger.info(f"Successfully scaled {decision.action}: {decision.current_workers}→{new_workers} workers, {decision.current_jobs}→{new_jobs} jobs")
            return True
            
        except Exception as e:
            logger.error(f"Error applying scaling decision: {e}")
            return False
    
    def monitor_and_scale(self):
        """Main monitoring and scaling loop"""
        logger.info("Starting intelligent auto-scaling monitoring")
        
        while self.is_monitoring:
            try:
                # Get current metrics
                metrics = self.get_system_metrics()
                task_metrics = self.get_task_metrics()
                
                # Add to history
                self.metrics_history.append(metrics)
                if len(self.metrics_history) > self.config["metrics_window"]:
                    self.metrics_history.pop(0)
                
                # Calculate scaling decision
                decision = self.calculate_optimal_scaling(metrics, task_metrics)
                
                # Log current status
                logger.info(f"Metrics: CPU {metrics.cpu_percent:.1f}%, Memory {metrics.memory_percent:.1f}%, "
                           f"Pending {task_metrics['pending']}, Decision: {decision.action} "
                           f"({decision.current_workers}→{decision.recommended_workers} workers, "
                           f"confidence: {decision.confidence:.2f})")
                
                # Apply scaling if confidence is high enough
                if decision.confidence > 0.6:
                    if decision.action != "maintain":
                        success = self.apply_scaling_decision(decision)
                        if success:
                            # Wait longer after scaling to let system stabilize
                            time.sleep(self.config["scaling_cooldown"])
                        else:
                            time.sleep(10)
                    else:
                        time.sleep(30)
                else:
                    logger.info(f"Low confidence ({decision.confidence:.2f}), skipping scaling decision")
                    time.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)
        
        logger.info("Auto-scaling monitoring stopped")
    
    def start_monitoring(self):
        """Start the auto-scaling monitoring in a separate thread"""
        if self.is_monitoring:
            logger.warning("Monitoring already running")
            return
        
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_and_scale, daemon=True)
        self.monitor_thread.start()
        logger.info("Auto-scaling monitoring started")
    
    def stop_monitoring(self):
        """Stop the auto-scaling monitoring"""
        if not self.is_monitoring:
            return
        
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Auto-scaling monitoring stopped")
    
    def get_scaling_report(self) -> Dict[str, Any]:
        """Generate comprehensive scaling report"""
        if not self.metrics_history:
            return {"error": "No metrics data available"}
        
        recent_metrics = self.metrics_history[-5:] if len(self.metrics_history) >= 5 else self.metrics_history
        
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        
        task_metrics = self.get_task_metrics()
        current_config = self.get_current_worker_config()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "current_configuration": {
                "workers": current_config["workers"],
                "jobs": current_config["jobs"],
                "cpu_target_standard": self.config["cpu_target_standard"],
                "cpu_target_refinement": self.config["cpu_target_refinement"],
                "memory_target": self.config["memory_target"]
            },
            "system_metrics": {
                "average_cpu_percent": avg_cpu,
                "average_memory_percent": avg_memory,
                "cpu_count": recent_metrics[-1].cpu_count,
                "memory_total_gb": recent_metrics[-1].memory_total_gb
            },
            "task_metrics": task_metrics,
            "scaling_history": self.scaling_history[-10:],  # Last 10 scaling actions
            "monitoring_status": {
                "is_monitoring": self.is_monitoring,
                "metrics_collected": len(self.metrics_history),
                "scaling_actions": len(self.scaling_history)
            }
        }
    
    def save_config(self):
        """Save current configuration to file"""
        config_file = self.project_root / "autoscaler_config.json"
        try:
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Configuration saved to {config_file}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    def load_config(self):
        """Load configuration from file"""
        config_file = self.project_root / "autoscaler_config.json"
        try:
            if config_file.exists():
                with open(config_file, 'r') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
                logger.info(f"Configuration loaded from {config_file}")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Intelligent Auto-Scaler for Robust Parallel Worker System')
    parser.add_argument('--start', action='store_true', help='Start auto-scaling monitoring')
    parser.add_argument('--stop', action='store_true', help='Stop auto-scaling monitoring')
    parser.add_argument('--status', action='store_true', help='Show current status and scaling report')
    parser.add_argument('--test', action='store_true', help='Test scaling decision without applying')
    parser.add_argument('--config', action='store_true', help='Show current configuration')
    parser.add_argument('--project-root', type=str, default='/Users/Arief/Desktop/Nexus', help='Project root directory')
    
    args = parser.parse_args()
    
    autoscaler = IntelligentAutoScaler(args.project_root)
    autoscaler.load_config()
    
    if args.start:
        autoscaler.start_monitoring()
        try:
            # Keep running until interrupted
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            autoscaler.stop_monitoring()
            print("\nAuto-scaling stopped by user")
    
    elif args.stop:
        autoscaler.stop_monitoring()
        print("Auto-scaling monitoring stopped")
    
    elif args.status:
        report = autoscaler.get_scaling_report()
        print(json.dumps(report, indent=2))
    
    elif args.test:
        metrics = autoscaler.get_system_metrics()
        task_metrics = autoscaler.get_task_metrics()
        decision = autoscaler.calculate_optimal_scaling(metrics, task_metrics)
        
        print("=== SCALING DECISION TEST ===")
        print(f"System Metrics: CPU {metrics.cpu_percent:.1f}%, Memory {metrics.memory_percent:.1f}%")
        print(f"Task Metrics: {task_metrics}")
        print(f"Decision: {decision.action}")
        print(f"Workers: {decision.current_workers} → {decision.recommended_workers}")
        print(f"Jobs: {decision.current_jobs} → {decision.recommended_jobs}")
        print(f"Reason: {decision.reason}")
        print(f"Confidence: {decision.confidence:.2f}")
    
    elif args.config:
        print("=== AUTO-SCALER CONFIGURATION ===")
        print(json.dumps(autoscaler.config, indent=2))
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
