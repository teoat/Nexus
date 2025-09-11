#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
📊 Performance Monitoring System for Nexus Platform
Comprehensive performance tracking, metrics collection, and alerting
"""

import time
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import psutil
import redis
import json
from fastapi import Request, Response
from fastapi.responses import PlainTextResponse
import uvicorn
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('nexus_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('nexus_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
ACTIVE_CONNECTIONS = Gauge('nexus_active_connections', 'Active connections')
DATABASE_CONNECTIONS = Gauge('nexus_database_connections', 'Database connections')
MEMORY_USAGE = Gauge('nexus_memory_usage_bytes', 'Memory usage in bytes')
CPU_USAGE = Gauge('nexus_cpu_usage_percent', 'CPU usage percentage')
DISK_USAGE = Gauge('nexus_disk_usage_bytes', 'Disk usage in bytes')

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    timestamp: datetime
    request_count: int
    avg_response_time: float
    error_rate: float
    memory_usage: float
    cpu_usage: float
    disk_usage: float
    active_connections: int
    database_connections: int
    cache_hit_rate: float
    queue_size: int

class PerformanceMonitor:
    """Comprehensive performance monitoring system"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.metrics_history: List[PerformanceMetrics] = []
        self.request_times: Dict[str, List[float]] = {}
        self.error_counts: Dict[str, int] = {}
        self.cache_stats = {"hits": 0, "misses": 0}
        self.start_time = datetime.now()
        
        # Performance thresholds
        self.thresholds = {
            "max_response_time": 2.0,  # seconds
            "max_error_rate": 0.05,    # 5%
            "max_memory_usage": 0.8,   # 80%
            "max_cpu_usage": 0.8,      # 80%
            "max_disk_usage": 0.9,     # 90%
            "max_queue_size": 1000
        }
        
        # Start background monitoring
        self._start_background_monitoring()
    
    def _start_background_monitoring(self):
        """Start background monitoring tasks"""
        asyncio.create_task(self._collect_system_metrics())
        asyncio.create_task(self._cleanup_old_metrics())
        asyncio.create_task(self._check_performance_thresholds())
    
    async def record_request(self, method: str, endpoint: str, duration: float, status_code: int):
        """Record request metrics"""
        # Update Prometheus metrics
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status_code).inc()
        REQUEST_DURATION.labels(method=method, endpoint=endpoint).observe(duration)
        
        # Store in Redis for analysis
        if self.redis_client:
            try:
                request_data = {
                    "timestamp": datetime.now().isoformat(),
                    "method": method,
                    "endpoint": endpoint,
                    "duration": duration,
                    "status_code": status_code
                }
                key = f"request_metrics:{datetime.now().strftime('%Y%m%d%H%M%S')}"
                self.redis_client.setex(key, 3600, json.dumps(request_data))  # Keep for 1 hour
            except redis.RedisError as e:
                logger.error(f"Failed to store request metrics: {e}")
        
        # Update internal tracking
        endpoint_key = f"{method}:{endpoint}"
        if endpoint_key not in self.request_times:
            self.request_times[endpoint_key] = []
        
        self.request_times[endpoint_key].append(duration)
        
        # Keep only last 1000 requests per endpoint
        if len(self.request_times[endpoint_key]) > 1000:
            self.request_times[endpoint_key] = self.request_times[endpoint_key][-1000:]
        
        # Track errors
        if status_code >= 400:
            self.error_counts[endpoint_key] = self.error_counts.get(endpoint_key, 0) + 1
    
    async def record_cache_hit(self, cache_key: str):
        """Record cache hit"""
        self.cache_stats["hits"] += 1
        
        if self.redis_client:
            try:
                self.redis_client.hincrby("cache_stats", "hits", 1)
            except redis.RedisError as e:
                logger.error(f"Failed to record cache hit: {e}")
    
    async def record_cache_miss(self, cache_key: str):
        """Record cache miss"""
        self.cache_stats["misses"] += 1
        
        if self.redis_client:
            try:
                self.redis_client.hincrby("cache_stats", "misses", 1)
            except redis.RedisError as e:
                logger.error(f"Failed to record cache miss: {e}")
    
    async def _collect_system_metrics(self):
        """Collect system metrics periodically"""
        while True:
            try:
                # Memory usage
                memory = psutil.virtual_memory()
                MEMORY_USAGE.set(memory.used)
                
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                CPU_USAGE.set(cpu_percent)
                
                # Disk usage
                disk = psutil.disk_usage('/')
                DISK_USAGE.set(disk.used)
                
                # Active connections (approximate)
                connections = len(psutil.net_connections())
                ACTIVE_CONNECTIONS.set(connections)
                
                # Database connections (if we can determine them)
                db_connections = await self._get_database_connections()
                DATABASE_CONNECTIONS.set(db_connections)
                
                # Create performance metrics
                metrics = PerformanceMetrics(
                    timestamp=datetime.now(),
                    request_count=self._get_total_requests(),
                    avg_response_time=self._get_avg_response_time(),
                    error_rate=self._get_error_rate(),
                    memory_usage=memory.percent / 100,
                    cpu_usage=cpu_percent / 100,
                    disk_usage=disk.percent / 100,
                    active_connections=connections,
                    database_connections=db_connections,
                    cache_hit_rate=self._get_cache_hit_rate(),
                    queue_size=await self._get_queue_size()
                )
                
                # Store metrics
                self.metrics_history.append(metrics)
                
                # Keep only last 24 hours of metrics
                cutoff_time = datetime.now() - timedelta(hours=24)
                self.metrics_history = [
                    m for m in self.metrics_history 
                    if m.timestamp > cutoff_time
                ]
                
                # Store in Redis
                if self.redis_client:
                    try:
                        key = f"performance_metrics:{datetime.now().strftime('%Y%m%d%H%M%S')}"
                        self.redis_client.setex(key, 86400, json.dumps(asdict(metrics), default=str))
                    except redis.RedisError as e:
                        logger.error(f"Failed to store performance metrics: {e}")
                
                logger.debug(f"Collected system metrics: CPU={cpu_percent}%, Memory={memory.percent}%")
                
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
            
            await asyncio.sleep(30)  # Collect every 30 seconds
    
    async def _cleanup_old_metrics(self):
        """Clean up old metrics data"""
        while True:
            try:
                # Clean up old request times
                for endpoint in list(self.request_times.keys()):
                    if len(self.request_times[endpoint]) > 1000:
                        self.request_times[endpoint] = self.request_times[endpoint][-1000:]
                
                # Clean up old error counts (reset daily)
                if datetime.now().hour == 0 and datetime.now().minute == 0:
                    self.error_counts.clear()
                
                # Clean up Redis old data
                if self.redis_client:
                    try:
                        # Remove old request metrics (older than 1 hour)
                        pattern = "request_metrics:*"
                        keys = self.redis_client.keys(pattern)
                        for key in keys:
                            ttl = self.redis_client.ttl(key)
                            if ttl == -1:  # No expiration set
                                self.redis_client.delete(key)
                    except redis.RedisError as e:
                        logger.error(f"Failed to cleanup old metrics: {e}")
                
            except Exception as e:
                logger.error(f"Error cleaning up metrics: {e}")
            
            await asyncio.sleep(300)  # Cleanup every 5 minutes
    
    async def _check_performance_thresholds(self):
        """Check performance thresholds and trigger alerts"""
        while True:
            try:
                if not self.metrics_history:
                    await asyncio.sleep(60)
                    continue
                
                alerts = []
                
                # Check response time
                
                # Check error rate
                
                # Check memory usage
                
                # Check CPU usage
                
                # Check disk usage
                
                # Check queue size
                
                # Send alerts
                if alerts:
                
            except Exception as e:
                logger.error(f"Error checking performance thresholds: {e}")
            
            await asyncio.sleep(60)  # Check every minute
    
    async def _send_performance_alerts(self, alerts: List[str], metrics: PerformanceMetrics):
        """Send performance alerts"""
        alert_data = {
            "timestamp": metrics.timestamp.isoformat(),
            "alerts": alerts,
            "metrics": asdict(metrics)
        }
        
        logger.warning(f"Performance alerts: {json.dumps(alert_data)}")
        
        # Store in Redis for alerting system
        if self.redis_client:
            try:
                key = f"performance_alert:{datetime.now().strftime('%Y%m%d%H%M%S')}"
                self.redis_client.setex(key, 3600, json.dumps(alert_data, default=str))
            except redis.RedisError as e:
                logger.error(f"Failed to store performance alert: {e}")
    
    def _get_total_requests(self) -> int:
        """Get total request count"""
        return sum(len(times) for times in self.request_times.values())
    
    def _get_avg_response_time(self) -> float:
        """Get average response time"""
        all_times = []
        for times in self.request_times.values():
            all_times.extend(times)
        
        if not all_times:
            return 0.0
        
        return sum(all_times) / len(all_times)
    
    def _get_error_rate(self) -> float:
        """Get error rate"""
        total_requests = self._get_total_requests()
        if total_requests == 0:
            return 0.0
        
        total_errors = sum(self.error_counts.values())
        return total_errors / total_requests
    
    def _get_cache_hit_rate(self) -> float:
        """Get cache hit rate"""
        total_cache_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        if total_cache_requests == 0:
            return 0.0
        
        return self.cache_stats["hits"] / total_cache_requests
    
    async def _get_database_connections(self) -> int:
        """Get database connection count"""
        # This would need to be implemented based on your database setup
        return 0
    
    async def _get_queue_size(self) -> int:
        """Get queue size"""
        if self.redis_client:
            try:
                return self.redis_client.llen("task_queue")
            except redis.RedisError:
                return 0
        return 0
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.metrics_history:
            return {"message": "No metrics available"}
        
        
        return {
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
    
    def _is_healthy(self, metrics: PerformanceMetrics) -> bool:
        """Check if system is healthy"""
        return (
            metrics.avg_response_time <= self.thresholds["max_response_time"] and
            metrics.error_rate <= self.thresholds["max_error_rate"] and
            metrics.memory_usage <= self.thresholds["max_memory_usage"] and
            metrics.cpu_usage <= self.thresholds["max_cpu_usage"] and
            metrics.disk_usage <= self.thresholds["max_disk_usage"] and
            metrics.queue_size <= self.thresholds["max_queue_size"]
        )
    
    def get_prometheus_metrics(self) -> str:
        """Get Prometheus metrics"""

# Performance monitoring middleware
class PerformanceMonitoringMiddleware:
    """Middleware for performance monitoring"""
    
    def __init__(self, monitor: PerformanceMonitor):
        self.monitor = monitor
    
    async def __call__(self, request: Request, call_next):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Record metrics
        await self.monitor.record_request(
            method=request.method,
            endpoint=request.url.path,
            duration=duration,
            status_code=response.status_code
        )
        
        return response

# Health check endpoint
async def health_check(monitor: PerformanceMonitor) -> Dict[str, Any]:
    """Health check endpoint"""
    summary = monitor.get_performance_summary()
    
    if summary.get("status") == "healthy":
        return {"status": "healthy", "details": summary}
    else:
        return {"status": "unhealthy", "details": summary}

# Metrics endpoint
async def metrics_endpoint(monitor: PerformanceMonitor) -> Response:
    """Prometheus metrics endpoint"""
    metrics = monitor.get_prometheus_metrics()

# Performance dashboard data
async def get_performance_dashboard(monitor: PerformanceMonitor) -> Dict[str, Any]:
    """Get performance dashboard data"""
    if not monitor.metrics_history:
        return {"message": "No metrics available"}
    
    # Get last 24 hours of metrics
    cutoff_time = datetime.now() - timedelta(hours=24)
    recent_metrics = [
        m for m in monitor.metrics_history 
        if m.timestamp > cutoff_time
    ]
    
    if not recent_metrics:
        return {"message": "No recent metrics available"}
    
    # Calculate trends
    response_times = [m.avg_response_time for m in recent_metrics]
    error_rates = [m.error_rate for m in recent_metrics]
    memory_usage = [m.memory_usage for m in recent_metrics]
    cpu_usage = [m.cpu_usage for m in recent_metrics]
    
    return {
        "summary": monitor.get_performance_summary(),
        "trends": {
            "response_times": response_times,
            "error_rates": error_rates,
            "memory_usage": memory_usage,
            "cpu_usage": cpu_usage
        },
        "timestamps": [m.timestamp.isoformat() for m in recent_metrics],
        "thresholds": monitor.thresholds
    }
