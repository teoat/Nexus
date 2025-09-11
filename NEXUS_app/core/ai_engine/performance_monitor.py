#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
📊 Frenly AI Performance Monitor
Comprehensive performance monitoring and metrics collection
"""

import asyncio
import logging
import time
import json
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import redis
from backend.config import get_config

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Metric type enumeration"""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"

class AlertLevel(Enum):
    """Alert level enumeration"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class Metric:
    """Metric definition"""
    name: str
    value: float
    metric_type: MetricType
    timestamp: str
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Alert:
    """Alert definition"""
    id: str
    name: str
    level: AlertLevel
    message: str
    timestamp: str
    metric_name: str
    threshold: float
    current_value: float
    resolved: bool = False
    resolved_at: Optional[str] = None

@dataclass
class PerformanceStats:
    """Performance statistics"""
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    disk_usage: float = 0.0
    network_io: Dict[str, float] = field(default_factory=dict)
    request_count: int = 0
    response_time_avg: float = 0.0
    error_rate: float = 0.0
    active_connections: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class PerformanceMonitor:
    """Comprehensive performance monitoring system"""
    
    def __init__(self):
        """
          Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        self.config = get_config()
        self.redis_client = redis.Redis.from_url(self.config.redis_url)
        self.metrics: List[Metric] = []
        self.alerts: List[Alert] = []
        self.performance_stats = PerformanceStats()
        self.running = False
        
        # Monitoring configuration
        self.monitoring_interval = 10  # seconds
        self.metrics_retention = 3600  # 1 hour
        self.alert_thresholds = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "disk_usage": 90.0,
            "response_time": 5.0,
            "error_rate": 0.1
        }
        
        # Performance counters
        self.counters = {
            "requests_total": 0,
            "requests_successful": 0,
            "requests_failed": 0,
            "responses_generated": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "sessions_created": 0,
            "sessions_terminated": 0
        }
        
        # Response time tracking
        self.response_times = []
        self.max_response_times = 1000
        
        logger.info("✅ Performance Monitor initialized")
    
    async def start(self):
        """Start the performance monitor"""
        self.running = True
        logger.info("🚀 Starting Performance Monitor...")
        
        # Start monitoring tasks
        asyncio.create_task(self._monitor_system_metrics())
        asyncio.create_task(self._monitor_application_metrics())
        asyncio.create_task(self._check_alerts())
        asyncio.create_task(self._cleanup_old_metrics())
        asyncio.create_task(self._sync_metrics_to_redis())
        
        logger.info("✅ Performance Monitor started")
    
    async def stop(self):
        """Stop the performance monitor"""
        self.running = False
        logger.info("🛑 Stopping Performance Monitor...")
        
        # Save final metrics
        await self._save_metrics_to_redis()
        
        logger.info("✅ Performance Monitor stopped")
    
    async def record_request(self, success: bool, response_time: float, 
                           agent_type: Optional[str] = None):
        """Record request metrics"""
        try:
            # Update counters
            self.counters["requests_total"] += 1
            if success:
                self.counters["requests_successful"] += 1
            else:
                self.counters["requests_failed"] += 1
            
            # Record response time
            self.response_times.append(response_time)
            if len(self.response_times) > self.max_response_times:
                self.response_times = self.response_times[-self.max_response_times:]
            
            # Create metrics
            await self._record_metric("requests_total", 1, MetricType.COUNTER, {"success": str(success)})
            await self._record_metric("response_time", response_time, MetricType.TIMER, {"agent_type": agent_type or "unknown"})
            
            if success:
                await self._record_metric("requests_successful", 1, MetricType.COUNTER, {"agent_type": agent_type or "unknown"})
            else:
                await self._record_metric("requests_failed", 1, MetricType.COUNTER, {"agent_type": agent_type or "unknown"})
            
        except Exception as e:
            logger.error(f"❌ Error recording request metrics: {e}")
    
    async def record_cache_operation(self, hit: bool, cache_type: str):
        """Record cache operation metrics"""
        try:
            if hit:
                self.counters["cache_hits"] += 1
                await self._record_metric("cache_hits", 1, MetricType.COUNTER, {"cache_type": cache_type})
            else:
                self.counters["cache_misses"] += 1
                await self._record_metric("cache_misses", 1, MetricType.COUNTER, {"cache_type": cache_type})
            
        except Exception as e:
            logger.error(f"❌ Error recording cache metrics: {e}")
    
    async def record_session_operation(self, operation: str):
        """Record session operation metrics"""
        try:
            if operation == "created":
                self.counters["sessions_created"] += 1
                await self._record_metric("sessions_created", 1, MetricType.COUNTER)
            elif operation == "terminated":
                self.counters["sessions_terminated"] += 1
                await self._record_metric("sessions_terminated", 1, MetricType.COUNTER)
            
        except Exception as e:
            logger.error(f"❌ Error recording session metrics: {e}")
    
    async def _record_metric(self, name: str, value: float, metric_type: MetricType, 
                           tags: Optional[Dict[str, str]] = None):
        """Record a metric"""
        try:
            metric = Metric(
                name=name,
                value=value,
                metric_type=metric_type,
                timestamp=datetime.now().isoformat(),
                tags=tags or {}
            )
            
            self.metrics.append(metric)
            
            # Keep only recent metrics
            cutoff_time = datetime.now() - timedelta(seconds=self.metrics_retention)
            self.metrics = [
                m for m in self.metrics 
                if datetime.fromisoformat(m.timestamp) > cutoff_time
            ]
            
        except Exception as e:
            logger.error(f"❌ Error recording metric {name}: {e}")
    
    async def _monitor_system_metrics(self):
        """Monitor system metrics"""
        while self.running:
            try:
                # CPU usage
                cpu_usage = psutil.cpu_percent(interval=1)
                await self._record_metric("cpu_usage", cpu_usage, MetricType.GAUGE)
                
                # Memory usage
                memory = psutil.virtual_memory()
                memory_usage = memory.percent
                await self._record_metric("memory_usage", memory_usage, MetricType.GAUGE)
                
                # Disk usage
                disk = psutil.disk_usage('/')
                disk_usage = (disk.used / disk.total) * 100
                await self._record_metric("disk_usage", disk_usage, MetricType.GAUGE)
                
                # Network I/O
                network = psutil.net_io_counters()
                await self._record_metric("network_bytes_sent", network.bytes_sent, MetricType.COUNTER)
                await self._record_metric("network_bytes_recv", network.bytes_recv, MetricType.COUNTER)
                
                # Update performance stats
                self.performance_stats.cpu_usage = cpu_usage
                self.performance_stats.memory_usage = memory_usage
                self.performance_stats.disk_usage = disk_usage
                self.performance_stats.network_io = {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv
                }
                self.performance_stats.timestamp = datetime.now().isoformat()
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"❌ Error monitoring system metrics: {e}")
                await asyncio.sleep(60)
    
    async def _monitor_application_metrics(self):
        """Monitor application metrics"""
        while self.running:
            try:
                # Calculate derived metrics
                total_requests = self.counters["requests_total"]
                successful_requests = self.counters["requests_successful"]
                failed_requests = self.counters["requests_failed"]
                
                # Error rate
                error_rate = 0.0
                if total_requests > 0:
                    error_rate = failed_requests / total_requests
                
                await self._record_metric("error_rate", error_rate, MetricType.GAUGE)
                
                # Average response time
                avg_response_time = 0.0
                if self.response_times:
                    avg_response_time = sum(self.response_times) / len(self.response_times)
                
                await self._record_metric("response_time_avg", avg_response_time, MetricType.GAUGE)
                
                # Cache hit rate
                cache_hits = self.counters["cache_hits"]
                cache_misses = self.counters["cache_misses"]
                cache_hit_rate = 0.0
                if cache_hits + cache_misses > 0:
                    cache_hit_rate = cache_hits / (cache_hits + cache_misses)
                
                await self._record_metric("cache_hit_rate", cache_hit_rate, MetricType.GAUGE)
                
                # Update performance stats
                self.performance_stats.request_count = total_requests
                self.performance_stats.response_time_avg = avg_response_time
                self.performance_stats.error_rate = error_rate
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error(f"❌ Error monitoring application metrics: {e}")
                await asyncio.sleep(60)
    
    async def _check_alerts(self):
        """Check for alert conditions"""
        while self.running:
            try:
                # Check CPU usage
                if self.performance_stats.cpu_usage > self.alert_thresholds["cpu_usage"]:
                    await self._create_alert(
                        "high_cpu_usage",
                        AlertLevel.WARNING,
                        f"High CPU usage: {self.performance_stats.cpu_usage:.1f}%",
                        "cpu_usage",
                        self.alert_thresholds["cpu_usage"],
                        self.performance_stats.cpu_usage
                    )
                
                # Check memory usage
                if self.performance_stats.memory_usage > self.alert_thresholds["memory_usage"]:
                    await self._create_alert(
                        "high_memory_usage",
                        AlertLevel.WARNING,
                        f"High memory usage: {self.performance_stats.memory_usage:.1f}%",
                        "memory_usage",
                        self.alert_thresholds["memory_usage"],
                        self.performance_stats.memory_usage
                    )
                
                # Check disk usage
                if self.performance_stats.disk_usage > self.alert_thresholds["disk_usage"]:
                    await self._create_alert(
                        "high_disk_usage",
                        AlertLevel.ERROR,
                        f"High disk usage: {self.performance_stats.disk_usage:.1f}%",
                        "disk_usage",
                        self.alert_thresholds["disk_usage"],
                        self.performance_stats.disk_usage
                    )
                
                # Check response time
                if self.performance_stats.response_time_avg > self.alert_thresholds["response_time"]:
                    await self._create_alert(
                        "high_response_time",
                        AlertLevel.WARNING,
                        f"High response time: {self.performance_stats.response_time_avg:.2f}s",
                        "response_time",
                        self.alert_thresholds["response_time"],
                        self.performance_stats.response_time_avg
                    )
                
                # Check error rate
                if self.performance_stats.error_rate > self.alert_thresholds["error_rate"]:
                    await self._create_alert(
                        "high_error_rate",
                        AlertLevel.ERROR,
                        f"High error rate: {self.performance_stats.error_rate:.2%}",
                        "error_rate",
                        self.alert_thresholds["error_rate"],
                        self.performance_stats.error_rate
                    )
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Error checking alerts: {e}")
                await asyncio.sleep(60)
    
    async def _create_alert(self, alert_name: str, level: AlertLevel, message: str,
                          metric_name: str, threshold: float, current_value: float):
        """Create an alert"""
        try:
            # Check if alert already exists and is unresolved
            existing_alert = None
            for alert in self.alerts:
                if (alert.name == alert_name and not alert.resolved and
                    datetime.now() - datetime.fromisoformat(alert.timestamp) < timedelta(minutes=5)):
                    existing_alert = alert
                    break
            
            if existing_alert:
                return  # Alert already exists
            
            alert = Alert(
                id=f"{alert_name}_{int(time.time())}",
                name=alert_name,
                level=level,
                message=message,
                timestamp=datetime.now().isoformat(),
                metric_name=metric_name,
                threshold=threshold,
                current_value=current_value
            )
            
            self.alerts.append(alert)
            
            # Log alert
            logger.warning(f"🚨 {level.value.upper()}: {message}")
            
            # Save to Redis
            await self._save_alert_to_redis(alert)
            
        except Exception as e:
            logger.error(f"❌ Error creating alert {alert_name}: {e}")
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        try:
            for alert in self.alerts:
                if alert.id == alert_id and not alert.resolved:
                    alert.resolved = True
                    alert.resolved_at = datetime.now().isoformat()
                    
                    logger.info(f"✅ Alert resolved: {alert.name}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error resolving alert {alert_id}: {e}")
            return False
    
    async def get_metrics(self, metric_name: Optional[str] = None, 
                         start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None) -> List[Metric]:
        """Get metrics with optional filtering"""
        try:
            filtered_metrics = self.metrics
            
            if metric_name:
                filtered_metrics = [m for m in filtered_metrics if m.name == metric_name]
            
            if start_time:
                filtered_metrics = [
                    m for m in filtered_metrics 
                    if datetime.fromisoformat(m.timestamp) >= start_time
                ]
            
            if end_time:
                filtered_metrics = [
                    m for m in filtered_metrics 
                    if datetime.fromisoformat(m.timestamp) <= end_time
                ]
            
            return filtered_metrics
            
        except Exception as e:
            logger.error(f"❌ Error getting metrics: {e}")
            return []
    
    async def get_performance_stats(self) -> PerformanceStats:
        """Get current performance statistics"""
        return self.performance_stats
    
    async def get_alerts(self, unresolved_only: bool = True) -> List[Alert]:
        """Get alerts"""
        try:
            if unresolved_only:
                return [alert for alert in self.alerts if not alert.resolved]
            else:
                return self.alerts
                
        except Exception as e:
            logger.error(f"❌ Error getting alerts: {e}")
            return []
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data"""
        try:
            # Get recent metrics (last hour)
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=1)
            recent_metrics = await self.get_metrics(start_time=start_time, end_time=end_time)
            
            # Calculate averages
            cpu_metrics = [m for m in recent_metrics if m.name == "cpu_usage"]
            memory_metrics = [m for m in recent_metrics if m.name == "memory_usage"]
            response_time_metrics = [m for m in recent_metrics if m.name == "response_time_avg"]
            
            avg_cpu = sum(m.value for m in cpu_metrics) / len(cpu_metrics) if cpu_metrics else 0
            avg_memory = sum(m.value for m in memory_metrics) / len(memory_metrics) if memory_metrics else 0
            avg_response_time = sum(m.value for m in response_time_metrics) / len(response_time_metrics) if response_time_metrics else 0
            
            # Get active alerts
            active_alerts = await self.get_alerts(unresolved_only=True)
            
            return {
                "performance_stats": {
                    "cpu_usage": self.performance_stats.cpu_usage,
                    "memory_usage": self.performance_stats.memory_usage,
                    "disk_usage": self.performance_stats.disk_usage,
                    "request_count": self.performance_stats.request_count,
                    "response_time_avg": self.performance_stats.response_time_avg,
                    "error_rate": self.performance_stats.error_rate
                },
                "averages": {
                    "cpu_usage": avg_cpu,
                    "memory_usage": avg_memory,
                    "response_time": avg_response_time
                },
                "counters": self.counters,
                "active_alerts": len(active_alerts),
                "alerts": [
                    {
                        "id": alert.id,
                        "name": alert.name,
                        "level": alert.level.value,
                        "message": alert.message,
                        "timestamp": alert.timestamp
                    }
                    for alert in active_alerts
                ],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting dashboard data: {e}")
            return {}
    
    async def _cleanup_old_metrics(self):
        """Clean up old metrics"""
        while self.running:
            try:
                cutoff_time = datetime.now() - timedelta(seconds=self.metrics_retention)
                old_count = len(self.metrics)
                
                self.metrics = [
                    m for m in self.metrics 
                    if datetime.fromisoformat(m.timestamp) > cutoff_time
                ]
                
                removed_count = old_count - len(self.metrics)
                if removed_count > 0:
                    logger.info(f"Cleaned up {removed_count} old metrics")
                
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Error cleaning up metrics: {e}")
                await asyncio.sleep(60)
    
    async def _sync_metrics_to_redis(self):
        """Sync metrics to Redis"""
        while self.running:
            try:
                await self._save_metrics_to_redis()
                await asyncio.sleep(60)  # Sync every minute
                
            except Exception as e:
                logger.error(f"❌ Error syncing metrics to Redis: {e}")
                await asyncio.sleep(60)
    
    async def _save_metrics_to_redis(self):
        """Save metrics to Redis"""
        try:
            if not self.redis_client:
                return
            
            # Save recent metrics
            recent_metrics = self.metrics[-1000:]  # Last 1000 metrics
            metrics_data = [
                {
                    "name": m.name,
                    "value": m.value,
                    "metric_type": m.metric_type.value,
                    "timestamp": m.timestamp,
                    "tags": m.tags,
                    "metadata": m.metadata
                }
                for m in recent_metrics
            ]
            
            self.redis_client.setex(
                "frenly_metrics",
                3600,  # 1 hour TTL
                json.dumps(metrics_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"❌ Error saving metrics to Redis: {e}")
    
    async def _save_alert_to_redis(self, alert: Alert):
        """Save alert to Redis"""
        try:
            if not self.redis_client:
                return
            
            alert_data = {
                "id": alert.id,
                "name": alert.name,
                "level": alert.level.value,
                "message": alert.message,
                "timestamp": alert.timestamp,
                "metric_name": alert.metric_name,
                "threshold": alert.threshold,
                "current_value": alert.current_value,
                "resolved": alert.resolved,
                "resolved_at": alert.resolved_at
            }
            
            self.redis_client.setex(
                f"frenly_alert:{alert.id}",
                86400,  # 24 hours TTL
                json.dumps(alert_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"❌ Error saving alert to Redis: {e}")

# Global performance monitor instance
performance_monitor = PerformanceMonitor()
