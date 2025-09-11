#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
📊 Comprehensive Monitoring & Observability System
Advanced monitoring, logging, and observability for Nexus Platform
"""

import asyncio
import time
import logging
import json
import traceback
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager
import psutil
import requests
import structlog
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
import uuid

logger = logging.getLogger(__name__)

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'endpoint'])
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Number of active connections')
MEMORY_USAGE = Gauge('memory_usage_bytes', 'Memory usage in bytes')
CPU_USAGE = Gauge('cpu_usage_percent', 'CPU usage percentage')
DATABASE_CONNECTIONS = Gauge('database_connections', 'Number of database connections')
CACHE_HITS = Counter('cache_hits_total', 'Total cache hits', ['cache_type'])
CACHE_MISSES = Counter('cache_misses_total', 'Total cache misses', ['cache_type'])

@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: datetime
    level: str
    message: str
    service: str
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class HealthCheck:
    """Health check result"""
    service: str
    status: str
    timestamp: datetime
    response_time: float
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@dataclass
class Alert:
    """Alert definition"""
    id: str
    name: str
    condition: str
    severity: str
    threshold: float
    current_value: float
    triggered: bool
    timestamp: datetime
    description: str

class StructuredLogger:
    """Enhanced structured logging system"""
    
    def __init__(self, service_name: str = "nexus-platform"):
        """
          Init  
        
        
        Args:
            service_name: Description of service_name
    
        Example:
            TBD: Add usage example
        """
        self.service_name = service_name
        self.logger = structlog.get_logger()
        self._setup_structlog()
    
    def _setup_structlog(self):
        """Setup structured logging configuration"""
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    
    def log(self, level: str, message: str, **kwargs):
        """Log structured message"""
        log_entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            message=message,
            service=self.service_name,
            trace_id=kwargs.get('trace_id'),
            span_id=kwargs.get('span_id'),
            user_id=kwargs.get('user_id'),
            request_id=kwargs.get('request_id'),
            metadata=kwargs.get('metadata')
        )
        
        # Log to structured logger
        getattr(self.logger, level.lower())(message, **kwargs)
        
        # Also log to standard logger for compatibility
        getattr(logging, level.upper())(f"[{self.service_name}] {message}")
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.log("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.log("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.log("ERROR", message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self.log("CRITICAL", message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.log("DEBUG", message, **kwargs)

class DistributedTracing:
    """Distributed tracing with OpenTelemetry"""
    
    def __init__(self, service_name: str = "nexus-platform", jaeger_endpoint: str = "http://localhost:14268/api/traces"):
        """
          Init  
        
        
        Args:
            service_name: Description of service_name
            jaeger_endpoint: Description of jaeger_endpoint
    
        Example:
            TBD: Add usage example
        """
        self.service_name = service_name
        self.jaeger_endpoint = jaeger_endpoint
        self.tracer = None
        self._setup_tracing()
    
    def _setup_tracing(self):
        """Setup distributed tracing"""
        try:
            # Create resource
            resource = Resource.create({
                "service.name": self.service_name,
                "service.version": "2.0.0"
            })
            
            # Create tracer provider
            trace.set_tracer_provider(TracerProvider(resource=resource))
            self.tracer = trace.get_tracer(__name__)
            
            # Create Jaeger exporter
            jaeger_exporter = JaegerExporter(
                agent_host_name="localhost",
                agent_port=6831,
            )
            
            # Create span processor
            span_processor = BatchSpanProcessor(jaeger_exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)
            
            logger.info("Distributed tracing initialized")
        except Exception as e:
            logger.error(f"Failed to initialize distributed tracing: {e}")
    
    def get_tracer(self):
        """Get tracer instance"""
        return self.tracer
    
    def create_span(self, name: str, **attributes):
        """Create a new span"""
        if self.tracer:
            return self.tracer.start_span(name, attributes=attributes)
        return None

class HealthChecker:
    """Comprehensive health checking system"""
    
    def __init__(self):
        """
          Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        self.checks: Dict[str, callable] = {}
        self.results: Dict[str, HealthCheck] = {}
    
    def register_check(self, name: str, check_func: callable):
        """Register a health check"""
        self.checks[name] = check_func
    
    async def run_check(self, name: str) -> HealthCheck:
        if name not in self.checks:
            return HealthCheck(
                service=name,
                status="unknown",
                timestamp=datetime.now(),
                response_time=0.0,
                error=f"Check '{name}' not registered"
            )
        
        start_time = time.time()
        try:
            result = await self.checks[name]()
            response_time = time.time() - start_time
            
            health_check = HealthCheck(
                service=name,
                status="healthy" if result else "unhealthy",
                timestamp=datetime.now(),
                response_time=response_time,
                details=result if isinstance(result, dict) else None
            )
        except Exception as e:
            response_time = time.time() - start_time
            health_check = HealthCheck(
                service=name,
                status="unhealthy",
                timestamp=datetime.now(),
                response_time=response_time,
                error=str(e)
            )
        
        self.results[name] = health_check
        return health_check
    
    async def run_all_checks(self) -> Dict[str, HealthCheck]:
        """Run all registered health checks"""
        tasks = [self.run_check(name) for name in self.checks.keys()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            name: result for name, result in zip(self.checks.keys(), results)
            if isinstance(result, HealthCheck)
        }
    
    def get_overall_status(self) -> str:
        """Get overall system health status"""
        if not self.results:
            return "unknown"
        
        unhealthy_count = sum(1 for check in self.results.values() if check.status != "healthy")
        if unhealthy_count == 0:
            return "healthy"
        elif unhealthy_count < len(self.results) / 2:
            return "degraded"
        else:
            return "unhealthy"

class MetricsCollector:
    """System metrics collection"""
    
    def __init__(self):
        """
          Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        self.start_time = time.time()
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            CPU_USAGE.set(cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            MEMORY_USAGE.set(memory.used)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Network I/O
            network = psutil.net_io_counters()
            
            return {
                "cpu": {
                    "usage_percent": cpu_percent,
                    "count": psutil.cpu_count(),
                    "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "used": memory.used,
                    "usage_percent": memory.percent
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "usage_percent": (disk.used / disk.total) * 100
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                },
                "uptime": time.time() - self.start_time
            }
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return {}
    
    def collect_application_metrics(self) -> Dict[str, Any]:
        """
        Collect Application Metrics
        
        
        Args:
    
        Returns:
            Unknown: Description of return value
    
        Example:
            TBD: Add usage example
        """
        return {
            "requests": {
                "total": REQUEST_COUNT._value.sum(),
                "duration_avg": REQUEST_DURATION._sum / max(REQUEST_DURATION._count, 1)
            },
            "cache": {
                "hits": CACHE_HITS._value.sum(),
                "misses": CACHE_MISSES._value.sum()
            },
            "connections": {
                "active": ACTIVE_CONNECTIONS._value,
                "database": DATABASE_CONNECTIONS._value
            }
        }

class AlertManager:
    """Alert management system"""
    
    def __init__(self):
        """
          Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        self.alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.thresholds = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "response_time": 2.0,
            "error_rate": 5.0,
            "disk_usage": 90.0
        }
    
    def check_thresholds(self, metrics: Dict[str, Any]) -> List[Alert]:
        """Check metrics against thresholds and generate alerts"""
        new_alerts = []
        
        # CPU usage alert
        cpu_usage = metrics.get("cpu", {}).get("usage_percent", 0)
        if cpu_usage > self.thresholds["cpu_usage"]:
            alert = Alert(
                id=str(uuid.uuid4()),
                name="High CPU Usage",
                condition="cpu_usage > 80%",
                severity="warning",
                threshold=self.thresholds["cpu_usage"],
                current_value=cpu_usage,
                triggered=True,
                timestamp=datetime.now(),
                description=f"CPU usage is {cpu_usage:.1f}%, above threshold of {self.thresholds['cpu_usage']}%"
            )
            new_alerts.append(alert)
        
        # Memory usage alert
        memory_usage = metrics.get("memory", {}).get("usage_percent", 0)
        if memory_usage > self.thresholds["memory_usage"]:
            alert = Alert(
                id=str(uuid.uuid4()),
                name="High Memory Usage",
                condition="memory_usage > 85%",
                severity="warning",
                threshold=self.thresholds["memory_usage"],
                current_value=memory_usage,
                triggered=True,
                timestamp=datetime.now(),
                description=f"Memory usage is {memory_usage:.1f}%, above threshold of {self.thresholds['memory_usage']}%"
            )
            new_alerts.append(alert)
        
        # Response time alert
        response_time = metrics.get("requests", {}).get("duration_avg", 0)
        if response_time > self.thresholds["response_time"]:
            alert = Alert(
                id=str(uuid.uuid4()),
                name="High Response Time",
                condition="response_time > 2s",
                severity="warning",
                threshold=self.thresholds["response_time"],
                current_value=response_time,
                triggered=True,
                timestamp=datetime.now(),
                description=f"Average response time is {response_time:.2f}s, above threshold of {self.thresholds['response_time']}s"
            )
            new_alerts.append(alert)
        
        # Store alerts
        for alert in new_alerts:
            self.alerts[alert.id] = alert
            self.alert_history.append(alert)
        
        return new_alerts
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return [alert for alert in self.alerts.values() if alert.triggered]
    
    def resolve_alert(self, alert_id: str):
        """Resolve an alert"""
        if alert_id in self.alerts:
            self.alerts[alert_id].triggered = False

class ObservabilitySystem:
    """Main observability system"""
    
    def __init__(self, service_name: str = "nexus-platform"):
        """
          Init  
        
        
        Args:
            service_name: Description of service_name
    
        Example:
            TBD: Add usage example
        """
        self.service_name = service_name
        self.logger = StructuredLogger(service_name)
        self.tracing = DistributedTracing(service_name)
        self.health_checker = HealthChecker()
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
        self._setup_health_checks()
    
    def _setup_health_checks(self):
        """Setup default health checks"""
        self.health_checker.register_check("database", self._check_database)
        self.health_checker.register_check("redis", self._check_redis)
        self.health_checker.register_check("external_api", self._check_external_api)
    
    async def _check_database(self) -> bool:
        """Check database connectivity"""
        try:
            # This would be a real database check
            return True
        except Exception as e:
            self.logger.error(f"Database health check failed: {e}")
            return False
    
    async def _check_redis(self) -> bool:
        """Check Redis connectivity"""
        try:
            # This would be a real Redis check
            return True
        except Exception as e:
            self.logger.error(f"Redis health check failed: {e}")
            return False
    
    async def _check_external_api(self) -> bool:
        """Check external API connectivity"""
        try:
            # This would be a real external API check
            return True
        except Exception as e:
            self.logger.error(f"External API health check failed: {e}")
            return False
    
    async def collect_all_metrics(self) -> Dict[str, Any]:
        """Collect all metrics"""
        system_metrics = self.metrics_collector.collect_system_metrics()
        app_metrics = self.metrics_collector.collect_application_metrics()
        
        all_metrics = {
            "system": system_metrics,
            "application": app_metrics,
            "timestamp": datetime.now().isoformat()
        }
        
        # Check for alerts
        alerts = self.alert_manager.check_thresholds(all_metrics)
        if alerts:
            all_metrics["alerts"] = [asdict(alert) for alert in alerts]
        
        return all_metrics
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        health_checks = await self.health_checker.run_all_checks()
        overall_status = self.health_checker.get_overall_status()
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "checks": {name: asdict(check) for name, check in health_checks.items()},
            "uptime": time.time() - self.metrics_collector.start_time
        }
    
    def get_prometheus_metrics(self) -> str:
        """Get Prometheus metrics in text format"""
    
    def start_prometheus_server(self, port: int = 8001):
        """Start Prometheus metrics server"""
        start_http_server(port)
        self.logger.info(f"Prometheus metrics server started on port {port}")
    
    def instrument_fastapi(self, app):
        """Instrument FastAPI application for observability"""
        try:
            FastAPIInstrumentor.instrument_app(app)
            RequestsInstrumentor().instrument()
            Psycopg2Instrumentor().instrument()
            self.logger.info("FastAPI application instrumented for observability")
        except Exception as e:
            self.logger.error(f"Failed to instrument FastAPI app: {e}")

# Global observability system instance
observability = ObservabilitySystem()

# Convenience functions
def get_observability_system() -> ObservabilitySystem:
    """Get global observability system instance"""
    return observability

async def collect_metrics() -> Dict[str, Any]:
    """Collect all metrics"""
    return await observability.collect_all_metrics()

async def get_health_status() -> Dict[str, Any]:
    """Get health status"""
    return await observability.get_health_status()

def get_prometheus_metrics() -> str:
    """Get Prometheus metrics"""
    return observability.get_prometheus_metrics()

def start_monitoring(port: int = 8001):
    """Start monitoring services"""
    observability.start_prometheus_server(port)

def instrument_app(app):
    """Instrument FastAPI app for observability"""
    observability.instrument_fastapi(app)
