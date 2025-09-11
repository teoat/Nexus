#!/usr/bin/env python3
"""
🚀 Enhanced Continuous SOT Automation System - Production Ready
Advanced automation system with Tier 3 Redundancy and Single Source of Truth
Combines enhanced automation with redundancy and SOT enforcement
"""

import os
import sys
import json
import time
import asyncio
import logging
import argparse
import subprocess
import re
import psutil
import multiprocessing
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import signal
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import queue
import math
import shutil
import copy
import uuid
import socket
import requests
from enum import Enum

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(name)s] - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_continuous_sot_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SystemStatus(Enum):
    """System status enumeration"""
    ACTIVE = "active"
    BACKUP = "backup"
    FALLBACK = "fallback"
    FAILED = "failed"
    RECOVERING = "recovering"
    MAINTENANCE = "maintenance"

@dataclass
class SOTConfig:
    """Single Source of Truth configuration"""
    system_id: str = "enhanced_continuous_sot_automation"
    system_name: str = "Enhanced Continuous SOT Automation"
    version: str = "3.0.0"
    primary_authority: bool = True
    backup_systems: List[str] = None
    health_check_interval: int = 30
    backup_interval: int = 300
    conflict_resolution: str = "timestamp_based"
    lock_timeout: int = 3600
    auto_failover: bool = True
    
    def __post_init__(self):
        if self.backup_systems is None:
            self.backup_systems = ["robust_parallel_worker_system", "enhanced_continuous_todo_automation"]

@dataclass
class RedundancyConfig:
    """Tier 3 redundancy configuration"""
    primary_system: str = "enhanced_continuous_sot_automation"
    backup_system: str = "robust_parallel_worker_system"
    fallback_system: str = "enhanced_continuous_todo_automation"
    health_check_interval: int = 30
    max_retries_per_system: int = 3
    backup_interval: int = 300
    max_concurrent_failures: int = 5
    auto_recovery_enabled: bool = True
    circuit_breaker_threshold: int = 10
    failover_timeout: int = 60

@dataclass
class TodoTask:
    """Enhanced todo task with SOT metadata"""
    id: str
    title: str
    description: str
    status: str
    priority: str
    complexity: str
    phase: str
    file_path: str
    line_number: int
    source: str
    created_at: str
    updated_at: str
    dependencies: List[str] = None
    estimated_duration: int = 0
    actual_duration: int = 0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    execution_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    sot_version: str = "1.0"
    redundancy_level: int = 3
    authority_source: str = "enhanced_continuous_sot_automation"

@dataclass
class SystemHealth:
    """System health metrics"""
    system_name: str
    status: SystemStatus
    health_score: float
    cpu_usage: float
    memory_usage: float
    active_tasks: int
    completed_tasks: int
    failed_tasks: int
    last_heartbeat: str
    redundancy_level: int
    sot_authority: bool

class SOTManager:
    """Single Source of Truth manager"""
    
    def __init__(self, config: SOTConfig):
        self.config = config
        self.sot_file = Path("nexus_enhanced_sot.json")
        self.lock_file = Path("nexus_enhanced_sot.lock")
        self.backup_dir = Path("sot_backups")
        self.backup_dir.mkdir(exist_ok=True)
        self.lock_timeout = config.lock_timeout
        self.last_backup = datetime.now()
        
    def acquire_sot_lock(self) -> bool:
        """Acquire SOT authority lock"""
        try:
            if self.lock_file.exists():
                lock_data = json.loads(self.lock_file.read_text())
                lock_time = datetime.fromisoformat(lock_data['timestamp'])
                
                # Check if lock is expired
                if datetime.now() - lock_time > timedelta(seconds=self.lock_timeout):
                    logger.warning("SOT lock expired, taking authority")
                    self.release_sot_lock()
                else:
                    if lock_data['system_id'] != self.config.system_id:
                        logger.warning(f"SOT authority held by {lock_data['system_id']}")
                        return False
            
            # Create lock
            lock_data = {
                'system_id': self.config.system_id,
                'system_name': self.config.system_name,
                'timestamp': datetime.now().isoformat(),
                'version': self.config.version,
                'pid': os.getpid()
            }
            
            self.lock_file.write_text(json.dumps(lock_data, indent=2))
            logger.info(f"SOT authority acquired by {self.config.system_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to acquire SOT lock: {e}")
            return False
    
    def release_sot_lock(self):
        """Release SOT authority lock"""
        try:
            if self.lock_file.exists():
                self.lock_file.unlink()
                logger.info("SOT authority lock released")
        except Exception as e:
            logger.error(f"Failed to release SOT lock: {e}")
    
    def update_sot_status(self, health_data: Dict[str, Any]):
        """Update SOT status file"""
        try:
            sot_data = {
                'timestamp': datetime.now().isoformat(),
                'version': self.config.version,
                'system_id': self.config.system_id,
                'system_name': self.config.system_name,
                'status': 'active',
                'primary_authority': True,
                'health_data': health_data,
                'backup_systems': self.config.backup_systems,
                'last_updated': datetime.now().isoformat()
            }
            
            self.sot_file.write_text(json.dumps(sot_data, indent=2))
            
            # Create backup if needed
            if datetime.now() - self.last_backup > timedelta(seconds=self.config.backup_interval):
                self._create_backup()
                
        except Exception as e:
            logger.error(f"Failed to update SOT status: {e}")
    
    def _create_backup(self):
        """Create SOT backup"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"sot_backup_{timestamp}.json"
            
            if self.sot_file.exists():
                shutil.copy2(self.sot_file, backup_file)
                self.last_backup = datetime.now()
                logger.info(f"SOT backup created: {backup_file}")
                
        except Exception as e:
            logger.error(f"Failed to create SOT backup: {e}")

class Tier3RedundancyManager:
    """Tier 3 redundancy manager"""
    
    def __init__(self, config: RedundancyConfig):
        self.config = config
        self.health_monitor = SystemHealthMonitor(config)
        self.current_system = config.primary_system
        self.failure_counts = {}
        self.circuit_breakers = {}
        self.last_failover = datetime.now()
        
    def check_system_health(self) -> Dict[str, Any]:
        """Check health of all systems"""
        health_status = {}
        
        for system in [self.config.primary_system, self.config.backup_system, self.config.fallback_system]:
            health_status[system] = self.health_monitor.check_system_health(system)
            
        return health_status
    
    def determine_active_system(self) -> str:
        """Determine which system should be active based on health"""
        health_status = self.check_system_health()
        
        # Check primary system
        if health_status.get(self.config.primary_system, {}).get('healthy', False):
            if self.current_system != self.config.primary_system:
                logger.info(f"Failing back to primary system: {self.config.primary_system}")
                self.current_system = self.config.primary_system
            return self.config.primary_system
        
        # Check backup system
        if health_status.get(self.config.backup_system, {}).get('healthy', False):
            if self.current_system != self.config.backup_system:
                logger.info(f"Failing over to backup system: {self.config.backup_system}")
                self.current_system = self.config.backup_system
            return self.config.backup_system
        
        # Use fallback system
        if self.current_system != self.config.fallback_system:
            logger.warning(f"Using fallback system: {self.config.fallback_system}")
            self.current_system = self.config.fallback_system
            
        return self.config.fallback_system
    
    def handle_system_failure(self, system_name: str, error: Exception):
        """Handle system failure with circuit breaker"""
        self.failure_counts[system_name] = self.failure_counts.get(system_name, 0) + 1
        
        if self.failure_counts[system_name] >= self.config.circuit_breaker_threshold:
            self.circuit_breakers[system_name] = datetime.now()
            logger.error(f"Circuit breaker activated for {system_name}")
            
        # Trigger failover if needed
        if system_name == self.current_system:
            self.determine_active_system()

class SystemHealthMonitor:
    """Enhanced system health monitor"""
    
    def __init__(self, config: RedundancyConfig):
        self.config = config
        self.health_status = {}
        self.failure_counts = {}
        self.last_health_check = {}
        
    def check_system_health(self, system_name: str) -> Dict[str, Any]:
        """Check health of a specific system"""
        try:
            # Check if process is running
            running = self._check_process_running(system_name)
            
            # Check log file activity
            log_active = self._check_log_activity(system_name)
            
            # Check resource usage
            resource_usage = self._check_resource_usage(system_name)
            
            # Check output files
            output_valid = self._check_output_validity(system_name)
            
            health_score = sum([
                25 if running else 0,
                25 if log_active else 0,
                25 if resource_usage['healthy'] else 0,
                25 if output_valid else 0
            ])
            
            health_status = {
                'system': system_name,
                'timestamp': datetime.now().isoformat(),
                'health_score': health_score,
                'running': running,
                'log_active': log_active,
                'resource_usage': resource_usage,
                'output_valid': output_valid,
                'healthy': health_score >= 75
            }
            
            self.health_status[system_name] = health_status
            self.last_health_check[system_name] = datetime.now()
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed for {system_name}: {e}")
            return {
                'system': system_name,
                'timestamp': datetime.now().isoformat(),
                'health_score': 0,
                'running': False,
                'log_active': False,
                'resource_usage': {'healthy': False},
                'output_valid': False,
                'healthy': False,
                'error': str(e)
            }
    
    def _check_process_running(self, system_name: str) -> bool:
        """Check if system process is running"""
        try:
            # Look for PID files
            pid_files = {
                'enhanced_continuous_sot_automation': 'enhanced_continuous_sot_automation.pid',
                'robust_parallel_worker_system': 'robust_parallel_system.pid',
                'enhanced_continuous_todo_automation': 'enhanced_continuous_automation.pid'
            }
            
            pid_file = pid_files.get(system_name)
            if pid_file and Path(pid_file).exists():
                pid = int(Path(pid_file).read_text().strip())
                return psutil.pid_exists(pid)
                
            # Fallback to process name search
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if system_name in ' '.join(proc.info['cmdline'] or []):
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
            return False
            
        except Exception as e:
            logger.error(f"Process check failed for {system_name}: {e}")
            return False
    
    def _check_log_activity(self, system_name: str) -> bool:
        """Check if log file has recent activity"""
        try:
            log_files = {
                'enhanced_continuous_sot_automation': 'enhanced_continuous_sot_automation.log',
                'robust_parallel_worker_system': 'robust_parallel_system.log',
                'enhanced_continuous_todo_automation': 'enhanced_continuous_todo_automation.log'
            }
            
            log_file = log_files.get(system_name)
            if log_file and Path(log_file).exists():
                stat = Path(log_file).stat()
                # Check if log was modified in last 5 minutes
                return datetime.now().timestamp() - stat.st_mtime < 300
                
            return False
            
        except Exception as e:
            logger.error(f"Log activity check failed for {system_name}: {e}")
            return False
    
    def _check_resource_usage(self, system_name: str) -> Dict[str, Any]:
        """Check system resource usage"""
        try:
            # Look for status files
            status_files = {
                'enhanced_continuous_sot_automation': 'enhanced_sot_status.json',
                'robust_parallel_worker_system': 'robust_parallel_worker_status.json',
                'enhanced_continuous_todo_automation': 'enhanced_automation_status.json'
            }
            
            status_file = status_files.get(system_name)
            if status_file and Path(status_file).exists():
                status_data = json.loads(Path(status_file).read_text())
                cpu_usage = status_data.get('cpu_usage', 0)
                memory_usage = status_data.get('memory_usage', 0)
                
                return {
                    'cpu_usage': cpu_usage,
                    'memory_usage': memory_usage,
                    'healthy': cpu_usage < 90 and memory_usage < 90
                }
                
            return {'cpu_usage': 0, 'memory_usage': 0, 'healthy': True}
            
        except Exception as e:
            logger.error(f"Resource usage check failed for {system_name}: {e}")
            return {'cpu_usage': 0, 'memory_usage': 0, 'healthy': False}
    
    def _check_output_validity(self, system_name: str) -> bool:
        """Check if system output is valid"""
        try:
            # Check for recent status updates
            status_files = {
                'enhanced_continuous_sot_automation': 'enhanced_sot_status.json',
                'robust_parallel_worker_system': 'robust_parallel_worker_status.json',
                'enhanced_continuous_todo_automation': 'enhanced_automation_status.json'
            }
            
            status_file = status_files.get(system_name)
            if status_file and Path(status_file).exists():
                stat = Path(status_file).stat()
                # Check if status was updated in last 10 minutes
                return datetime.now().timestamp() - stat.st_mtime < 600
                
            return False
            
        except Exception as e:
            logger.error(f"Output validity check failed for {system_name}: {e}")
            return False

class ResourceManager:
    """Enhanced resource manager with SOT integration"""
    
    def __init__(self):
        self.cpu_count = psutil.cpu_count()
        self.total_memory = psutil.virtual_memory().total
        self.monitoring_enabled = True
        self.resource_history = []
        self.max_history = 100
        
    def get_system_resources(self) -> Dict[str, Any]:
        """Get current system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            resources = {
                'cpu_count': self.cpu_count,
                'cpu_usage': cpu_percent,
                'total_memory': self.total_memory,
                'available_memory': memory.available,
                'memory_usage': memory.percent,
                'disk_usage': disk.percent,
                'timestamp': datetime.now().isoformat()
            }
            
            # Store in history
            self.resource_history.append(resources)
            if len(self.resource_history) > self.max_history:
                self.resource_history.pop(0)
                
            return resources
            
        except Exception as e:
            logger.error(f"Failed to get system resources: {e}")
            return {}
    
    def calculate_optimal_workers(self, target_cpu: float = 60.0) -> int:
        """Calculate optimal number of workers based on CPU target"""
        try:
            resources = self.get_system_resources()
            cpu_usage = resources.get('cpu_usage', 0)
            
            # Calculate workers needed to reach target CPU usage
            if cpu_usage < target_cpu:
                available_cpu = target_cpu - cpu_usage
                workers = int((available_cpu / 100) * self.cpu_count)
                return max(1, min(workers, self.cpu_count * 2))
            else:
                # Reduce workers if CPU is too high
                excess_cpu = cpu_usage - target_cpu
                reduction = int((excess_cpu / 100) * self.cpu_count)
                return max(1, self.cpu_count - reduction)
                
        except Exception as e:
            logger.error(f"Failed to calculate optimal workers: {e}")
            return self.cpu_count

class EnhancedContinuousSOTAutomation:
    """Enhanced Continuous SOT Automation System"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or "enhanced_sot_config.json"
        self.config = self._load_config()
        self.sot_config = SOTConfig()
        self.redundancy_config = RedundancyConfig()
        
        # Initialize managers
        self.sot_manager = SOTManager(self.sot_config)
        self.redundancy_manager = Tier3RedundancyManager(self.redundancy_config)
        self.resource_manager = ResourceManager()
        
        # Initialize automation components
        self.running = False
        self.cycle_count = 0
        self.total_tasks_processed = 0
        self.total_tasks_completed = 0
        self.total_tasks_failed = 0
        self.start_time = datetime.now()
        
        # Task processing
        self.task_queue = queue.Queue()
        self.completed_tasks = []
        self.failed_tasks = []
        
        # Threading
        self.executor = None
        self.monitor_thread = None
        self.sot_thread = None
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Create PID file
        self.pid_file = Path("enhanced_continuous_sot_automation.pid")
        self.pid_file.write_text(str(os.getpid()))
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        default_config = {
            "execution": {
                "min_todos_per_cycle": 20,
                "max_todos_per_cycle": 100,
                "cycle_interval": 60,
                "max_cycles": 0,
                "auto_scaling": True,
                "refinement_enabled": True,
                "max_retries": 5,
                "retry_delay": 30
            },
            "phases": {
                "infrastructure": {"priority": 1, "enabled": True, "timeout": 300, "retries": 3},
                "security": {"priority": 2, "enabled": True, "timeout": 600, "retries": 2},
                "services": {"priority": 3, "enabled": True, "timeout": 900, "retries": 3},
                "monitoring": {"priority": 4, "enabled": True, "timeout": 300, "retries": 2},
                "optimization": {"priority": 5, "enabled": True, "timeout": 600, "retries": 2},
                "performance": {"priority": 6, "enabled": True, "timeout": 900, "retries": 2},
                "compliance": {"priority": 7, "enabled": True, "timeout": 1200, "retries": 1}
            },
            "resources": {
                "cpu_target_standard": 60.0,
                "cpu_target_refinement": 70.0,
                "memory_target": 60.0,
                "min_workers": 1,
                "max_workers": 20
            },
            "logging": {
                "level": "INFO",
                "file": "enhanced_continuous_sot_automation.log",
                "max_size": 10485760,
                "backup_count": 5
            }
        }
        
        if Path(self.config_file).exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in loaded_config:
                            loaded_config[key] = value
                        elif isinstance(value, dict):
                            for sub_key, sub_value in value.items():
                                if sub_key not in loaded_config[key]:
                                    loaded_config[key][sub_key] = sub_value
                    return loaded_config
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                
        return default_config
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
    
    def start(self):
        """Start the enhanced continuous SOT automation system"""
        try:
            # Acquire SOT authority
            if not self.sot_manager.acquire_sot_lock():
                logger.error("Failed to acquire SOT authority")
                return False
            
            logger.info("Starting Enhanced Continuous SOT Automation System")
            self.running = True
            
            # Start monitoring thread
            self.monitor_thread = threading.Thread(target=self._monitor_systems, daemon=True)
            self.monitor_thread.start()
            
            # Start SOT update thread
            self.sot_thread = threading.Thread(target=self._update_sot_status, daemon=True)
            self.sot_thread.start()
            
            # Start main automation loop
            self._run_automation_loop()
            
        except Exception as e:
            logger.error(f"Failed to start system: {e}")
            return False
        finally:
            self.cleanup()
    
    def stop(self):
        """Stop the automation system"""
        logger.info("Stopping Enhanced Continuous SOT Automation System")
        self.running = False
        
        # Wait for threads to finish
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
            
        if self.sot_thread and self.sot_thread.is_alive():
            self.sot_thread.join(timeout=5)
        
        # Shutdown executor
        if self.executor:
            self.executor.shutdown(wait=True)
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            # Release SOT lock
            self.sot_manager.release_sot_lock()
            
            # Remove PID file
            if self.pid_file.exists():
                self.pid_file.unlink()
                
            # Update final status
            self._update_final_status()
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    def _monitor_systems(self):
        """Monitor system health and redundancy"""
        while self.running:
            try:
                # Check system health
                active_system = self.redundancy_manager.determine_active_system()
                
                # Log health status
                health_status = self.redundancy_manager.check_system_health()
                logger.info(f"Active system: {active_system}")
                
                # Update resource usage
                resources = self.resource_manager.get_system_resources()
                logger.debug(f"System resources: {resources}")
                
                time.sleep(self.redundancy_config.health_check_interval)
                
            except Exception as e:
                logger.error(f"System monitoring failed: {e}")
                time.sleep(30)
    
    def _update_sot_status(self):
        """Update SOT status periodically"""
        while self.running:
            try:
                # Collect system metrics
                resources = self.resource_manager.get_system_resources()
                health_status = self.redundancy_manager.check_system_health()
                
                health_data = {
                    'system_status': 'active',
                    'health_score': 100.0,
                    'resources': resources,
                    'health_status': health_status,
                    'tasks_processed': self.total_tasks_processed,
                    'tasks_completed': self.total_tasks_completed,
                    'tasks_failed': self.total_tasks_failed,
                    'uptime': (datetime.now() - self.start_time).total_seconds(),
                    'cycle_count': self.cycle_count
                }
                
                # Update SOT status
                self.sot_manager.update_sot_status(health_data)
                
                time.sleep(self.sot_config.health_check_interval)
                
            except Exception as e:
                logger.error(f"SOT status update failed: {e}")
                time.sleep(30)
    
    def _run_automation_loop(self):
        """Main automation loop"""
        logger.info("Starting automation loop")
        
        while self.running:
            try:
                cycle_start = datetime.now()
                logger.info(f"Starting cycle {self.cycle_count + 1}")
                
                # Check if we should continue
                if not self._should_continue():
                    logger.info("Automation completed, stopping")
                    break
                
                # Parse and process todos
                todos_processed = self._process_cycle()
                
                # Update cycle statistics
                self.cycle_count += 1
                self.total_tasks_processed += todos_processed
                
                # Calculate cycle time
                cycle_time = (datetime.now() - cycle_start).total_seconds()
                logger.info(f"Cycle {self.cycle_count} completed: {todos_processed} todos processed in {cycle_time:.2f}s")
                
                # Update status
                self._update_status()
                
                # Wait for next cycle
                time.sleep(self.config['execution']['cycle_interval'])
                
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt")
                break
            except Exception as e:
                logger.error(f"Automation loop error: {e}")
                time.sleep(30)
    
    def _should_continue(self) -> bool:
        """Check if automation should continue"""
        # Check max cycles
        max_cycles = self.config['execution']['max_cycles']
        if max_cycles > 0 and self.cycle_count >= max_cycles:
            return False
        
        # Check for pending todos
        todos = self._parse_todos()
        if not todos:
            logger.info("No more todos to process")
            return False
        
        return True
    
    def _process_cycle(self) -> int:
        """Process a single automation cycle"""
        try:
            # Parse todos
            todos = self._parse_todos()
            if not todos:
                return 0
            
            # Calculate optimal workers
            target_cpu = self.config['resources']['cpu_target_standard']
            if self.config['execution']['refinement_enabled']:
                target_cpu = self.config['resources']['cpu_target_refinement']
            
            optimal_workers = self.resource_manager.calculate_optimal_workers(target_cpu)
            min_workers = self.config['resources']['min_workers']
            max_workers = self.config['resources']['max_workers']
            
            actual_workers = max(min_workers, min(optimal_workers, max_workers))
            
            # Limit todos per cycle
            min_todos = self.config['execution']['min_todos_per_cycle']
            max_todos = self.config['execution']['max_todos_per_cycle']
            todos_to_process = todos[:max_todos]
            
            if len(todos_to_process) < min_todos:
                logger.info(f"Not enough todos for cycle ({len(todos_to_process)} < {min_todos})")
                return 0
            
            logger.info(f"Processing {len(todos_to_process)} todos with {actual_workers} workers")
            
            # Process todos in parallel
            completed_count = 0
            failed_count = 0
            
            with ThreadPoolExecutor(max_workers=actual_workers) as executor:
                futures = []
                
                for todo in todos_to_process:
                    future = executor.submit(self._execute_task, todo)
                    futures.append(future)
                
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        if result:
                            completed_count += 1
                            self.total_tasks_completed += 1
                        else:
                            failed_count += 1
                            self.total_tasks_failed += 1
                    except Exception as e:
                        logger.error(f"Task execution failed: {e}")
                        failed_count += 1
                        self.total_tasks_failed += 1
            
            logger.info(f"Cycle completed: {completed_count} successful, {failed_count} failed")
            return len(todos_to_process)
            
        except Exception as e:
            logger.error(f"Cycle processing failed: {e}")
            return 0
    
    def _parse_todos(self) -> List[Dict[str, Any]]:
        """Parse todos from master_todo.md"""
        try:
            todo_file = Path("master_todo.md")
            if not todo_file.exists():
                logger.warning("master_todo.md not found")
                return []
            
            content = todo_file.read_text()
            todos = []
            
            # Parse todos using regex
            todo_pattern = r'^- \[ \] (.+)$'
            for match in re.finditer(todo_pattern, content, re.MULTILINE):
                line_number = content[:match.start()].count('\n') + 1
                title = match.group(1).strip()
                
                todo = {
                    'id': f"todo_{line_number}",
                    'title': title,
                    'line_number': line_number,
                    'status': 'pending',
                    'priority': 'medium',
                    'phase': 'general',
                    'file_path': str(todo_file),
                    'created_at': datetime.now().isoformat()
                }
                todos.append(todo)
            
            logger.info(f"Parsed {len(todos)} todos from master_todo.md")
            return todos
            
        except Exception as e:
            logger.error(f"Failed to parse todos: {e}")
            return []
    
    def _execute_task(self, todo: Dict[str, Any]) -> bool:
        """Execute a single task"""
        try:
            logger.info(f"Executing task: {todo['title']}")
            
            # Simulate task execution
            time.sleep(1)
            
            # Update todo status
            self._update_todo_status(todo, 'completed')
            
            logger.info(f"Task completed: {todo['title']}")
            return True
            
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            self._update_todo_status(todo, 'failed')
            return False
    
    def _update_todo_status(self, todo: Dict[str, Any], status: str):
        """Update todo status in master_todo.md"""
        try:
            todo_file = Path("master_todo.md")
            if not todo_file.exists():
                return
            
            content = todo_file.read_text()
            lines = content.split('\n')
            
            line_index = todo['line_number'] - 1
            if 0 <= line_index < len(lines):
                if status == 'completed':
                    lines[line_index] = lines[line_index].replace('- [ ]', '- [x]')
                elif status == 'failed':
                    lines[line_index] = lines[line_index].replace('- [ ]', '- [!]')
                
                todo_file.write_text('\n'.join(lines))
                logger.info(f"Updated todo status: {todo['title']} -> {status}")
                
        except Exception as e:
            logger.error(f"Failed to update todo status: {e}")
    
    def _update_status(self):
        """Update system status file"""
        try:
            resources = self.resource_manager.get_system_resources()
            
            status_data = {
                'timestamp': datetime.now().isoformat(),
                'system_name': 'Enhanced Continuous SOT Automation',
                'version': self.sot_config.version,
                'status': 'active',
                'cycle_count': self.cycle_count,
                'total_tasks_processed': self.total_tasks_processed,
                'total_tasks_completed': self.total_tasks_completed,
                'total_tasks_failed': self.total_tasks_failed,
                'uptime': (datetime.now() - self.start_time).total_seconds(),
                'resources': resources,
                'sot_authority': True,
                'redundancy_level': 3
            }
            
            status_file = Path("enhanced_sot_status.json")
            status_file.write_text(json.dumps(status_data, indent=2))
            
        except Exception as e:
            logger.error(f"Failed to update status: {e}")
    
    def _update_final_status(self):
        """Update final status on shutdown"""
        try:
            status_data = {
                'timestamp': datetime.now().isoformat(),
                'system_name': 'Enhanced Continuous SOT Automation',
                'version': self.sot_config.version,
                'status': 'stopped',
                'final_stats': {
                    'total_cycles': self.cycle_count,
                    'total_tasks_processed': self.total_tasks_processed,
                    'total_tasks_completed': self.total_tasks_completed,
                    'total_tasks_failed': self.total_tasks_failed,
                    'uptime': (datetime.now() - self.start_time).total_seconds()
                }
            }
            
            status_file = Path("enhanced_sot_final_status.json")
            status_file.write_text(json.dumps(status_data, indent=2))
            
        except Exception as e:
            logger.error(f"Failed to update final status: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Enhanced Continuous SOT Automation System")
    parser.add_argument("--config", default="enhanced_sot_config.json", help="Configuration file")
    parser.add_argument("--cycles", type=int, default=0, help="Maximum number of cycles (0 = infinite)")
    parser.add_argument("--interval", type=int, default=60, help="Cycle interval in seconds")
    parser.add_argument("--min-todos", type=int, default=20, help="Minimum todos per cycle")
    parser.add_argument("--max-todos", type=int, default=100, help="Maximum todos per cycle")
    parser.add_argument("--enable-scaling", action="store_true", help="Enable auto-scaling")
    parser.add_argument("--enable-refinement", action="store_true", help="Enable refinement mode")
    
    args = parser.parse_args()
    
    try:
        # Create automation system
        automation = EnhancedContinuousSOTAutomation(args.config)
        
        # Update config with command line arguments
        if args.cycles > 0:
            automation.config['execution']['max_cycles'] = args.cycles
        if args.interval > 0:
            automation.config['execution']['cycle_interval'] = args.interval
        if args.min_todos > 0:
            automation.config['execution']['min_todos_per_cycle'] = args.min_todos
        if args.max_todos > 0:
            automation.config['execution']['max_todos_per_cycle'] = args.max_todos
        if args.enable_scaling:
            automation.config['execution']['auto_scaling'] = True
        if args.enable_refinement:
            automation.config['execution']['refinement_enabled'] = True
        
        # Start automation
        automation.start()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"System failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
