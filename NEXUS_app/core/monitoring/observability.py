#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
Observability and monitoring utilities for Nexus Platform
"""

import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collects application metrics"""
    
    def __init__(self):
        """
          Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        self.metrics = {}
        self.start_time = time.time()
    
    def increment_counter(self, name: str, value: int = 1, tags: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        key = f"{name}:{tags}" if tags else name
        self.metrics[key] = self.metrics.get(key, 0) + value
    
    def set_gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Set a gauge metric"""
        key = f"{name}:{tags}" if tags else name
        self.metrics[key] = value
    
    def record_timing(self, name: str, duration: float, tags: Optional[Dict[str, str]] = None):
        """Record a timing metric"""
        key = f"{name}:{tags}" if tags else name
        if key not in self.metrics:
            self.metrics[key] = []
        self.metrics[key].append(duration)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get all metrics"""
        uptime = time.time() - self.start_time
        return {
            "uptime": uptime,
            "metrics": self.metrics,
            "timestamp": datetime.now().isoformat()
        }

class HealthChecker:
    """Health check utilities"""
    
    def __init__(self):
        """
          Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        self.checks = {}
    
    def add_check(self, name: str, check_func):
        """Add a health check"""
        self.checks[name] = check_func
    
    def run_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        results = {}
        overall_healthy = True
        
        for name, check_func in self.checks.items():
            try:
                result = check_func()
                results[name] = {
                    "status": "healthy" if result else "unhealthy",
                    "result": result
                }
                if not result:
                    overall_healthy = False
            except Exception as e:
                results[name] = {
                    "status": "error",
                    "error": str(e)
                }
                overall_healthy = False
        
        return {
            "overall": "healthy" if overall_healthy else "unhealthy",
            "checks": results,
            "timestamp": datetime.now().isoformat()
        }

# Global instances
metrics_collector = MetricsCollector()
health_checker = HealthChecker()

def setup_monitoring():
    """Setup monitoring and observability"""
    logger.info("Setting up monitoring and observability")
    
    # Add basic health checks
    
    logger.info("Monitoring setup complete")

def get_health_status() -> Dict[str, Any]:
    """Get current health status"""
    return health_checker.run_checks()

def get_metrics() -> Dict[str, Any]:
    """Get current metrics"""
    return metrics_collector.get_metrics()
