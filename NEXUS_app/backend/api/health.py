#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🏥 Health Check and Monitoring API for Nexus Platform
Comprehensive health monitoring, metrics, and system status endpoints
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
import psutil
import redis
import asyncpg
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database.config import get_db_session
from monitoring.performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)

# Create router
health_router = APIRouter(prefix="/health", tags=["Health & Monitoring"])

# Global performance monitor instance
performance_monitor: Optional[PerformanceMonitor] = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get performance monitor instance"""
    global performance_monitor
    if performance_monitor is None:
        performance_monitor = PerformanceMonitor()
    return performance_monitor

@health_router.get("/")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "nexus-platform",
        "version": "1.0.0"
    }

@health_router.get("/detailed")
async def detailed_health_check(
    request: Request,
    monitor: PerformanceMonitor = Depends(get_performance_monitor)
):
    """Detailed health check with system metrics"""
    try:
        # Get system metrics
        system_metrics = await get_system_metrics()
        
        # Get application metrics
        app_metrics = monitor.get_performance_summary()
        
        # Check database connectivity
        db_status = await check_database_health()
        
        # Check Redis connectivity
        redis_status = await check_redis_health()
        
        # Determine overall health
        overall_health = determine_overall_health(system_metrics, app_metrics, db_status, redis_status)
        
        return {
            "status": overall_health["status"],
            "timestamp": datetime.now().isoformat(),
            "service": "nexus-platform",
            "version": "1.0.0",
            "checks": {
                "system": system_metrics,
                "application": app_metrics,
                "database": db_status,
                "redis": redis_status
            },
            "summary": overall_health["summary"]
        }
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )

@health_router.get("/metrics")
async def get_metrics(monitor: PerformanceMonitor = Depends(get_performance_monitor)):
    """Get Prometheus metrics"""
    try:
        metrics = monitor.get_prometheus_metrics()
        return JSONResponse(
            content=metrics,
            media_type="text/plain; version=0.0.4; charset=utf-8"
        )
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve metrics")

@health_router.get("/dashboard")
async def get_dashboard(monitor: PerformanceMonitor = Depends(get_performance_monitor)):
    """Get performance dashboard data"""
    try:
        from monitoring.performance_monitor import get_performance_dashboard
        dashboard_data = await get_performance_dashboard(monitor)
        return dashboard_data
    except Exception as e:
        logger.error(f"Failed to get dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard data")

@health_router.get("/readiness")
async def readiness_check():
    """Kubernetes readiness probe"""
    try:
        # Check critical dependencies
        db_healthy = await check_database_health()
        redis_healthy = await check_redis_health()
        
        if db_healthy["status"] == "healthy" and redis_healthy["status"] == "healthy":
            return {"status": "ready"}
        else:
            return JSONResponse(
                status_code=503,
                content={"status": "not ready", "reason": "Dependencies not healthy"}
            )
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "not ready", "error": str(e)}
        )

@health_router.get("/liveness")
async def liveness_check():
    """Kubernetes liveness probe"""
    try:
        # Basic liveness check - if we can respond, we're alive
        return {
            "status": "alive",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Liveness check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "not alive", "error": str(e)}
        )

async def get_system_metrics() -> Dict[str, Any]:
    """Get system-level metrics"""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        # Memory usage
        memory = psutil.virtual_memory()
        
        # Disk usage
        disk = psutil.disk_usage('/')
        
        # Network I/O
        network = psutil.net_io_counters()
        
        # Process info
        process = psutil.Process()
        process_memory = process.memory_info()
        process_cpu = process.cpu_percent()
        
        return {
            "status": "healthy",
            "cpu": {
                "usage_percent": cpu_percent,
                "count": cpu_count,
                "process_usage_percent": process_cpu
            },
            "memory": {
                "total_bytes": memory.total,
                "available_bytes": memory.available,
                "used_bytes": memory.used,
                "usage_percent": memory.percent,
                "process_memory_bytes": process_memory.rss
            },
            "disk": {
                "total_bytes": disk.total,
                "used_bytes": disk.used,
                "free_bytes": disk.free,
                "usage_percent": (disk.used / disk.total) * 100
            },
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
        }
    except Exception as e:
        logger.error(f"Failed to get system metrics: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

async def check_database_health() -> Dict[str, Any]:
    """Check database health and connectivity"""
    try:
        # Get database session
        async with get_db_session() as session:
            
                raise Exception("Database query returned unexpected result")
            
            # Get database info
            result = await session.execute(text("SELECT version() as version"))
            version = result.scalar()
            
            # Get connection count
            result = await session.execute(text("""
                SELECT count(*) as connections 
                FROM pg_stat_activity 
                WHERE state = 'active'
            """))
            active_connections = result.scalar()
            
            return {
                "status": "healthy",
                "version": version,
                "active_connections": active_connections,
                "response_time_ms": 0  # Could measure actual response time
            }
    
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

async def check_redis_health() -> Dict[str, Any]:
    """Check Redis health and connectivity"""
    try:
        # Try to connect to Redis
        redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        
        
        
        
        
        # Get Redis info
        info = redis_client.info()
        
        return {
            "status": "healthy",
            "version": info.get("redis_version"),
            "used_memory": info.get("used_memory"),
            "connected_clients": info.get("connected_clients"),
            "uptime_seconds": info.get("uptime_in_seconds")
        }
    
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

def determine_overall_health(
    system_metrics: Dict[str, Any],
    app_metrics: Dict[str, Any],
    db_status: Dict[str, Any],
    redis_status: Dict[str, Any]
) -> Dict[str, Any]:
    """Determine overall system health"""
    issues = []
    
    # Check system metrics
    if system_metrics.get("status") != "healthy":
        issues.append("System metrics unhealthy")
    
    if system_metrics.get("cpu", {}).get("usage_percent", 0) > 90:
        issues.append("High CPU usage")
    
    if system_metrics.get("memory", {}).get("usage_percent", 0) > 90:
        issues.append("High memory usage")
    
    if system_metrics.get("disk", {}).get("usage_percent", 0) > 95:
        issues.append("High disk usage")
    
    # Check application metrics
    if app_metrics.get("status") != "healthy":
        issues.append("Application metrics unhealthy")
    
    if app_metrics.get("error_rate", 0) > 0.1:
        issues.append("High error rate")
    
    if app_metrics.get("avg_response_time", 0) > 5.0:
        issues.append("High response time")
    
    # Check database
    if db_status.get("status") != "healthy":
        issues.append("Database unhealthy")
    
    # Check Redis
    if redis_status.get("status") != "healthy":
        issues.append("Redis unhealthy")
    
    # Determine overall status
    if not issues:
        status = "healthy"
        summary = "All systems operational"
    elif len(issues) <= 2:
        status = "degraded"
        summary = f"Minor issues: {', '.join(issues[:2])}"
    else:
        status = "unhealthy"
        summary = f"Multiple issues: {', '.join(issues[:3])}"
    
    return {
        "status": status,
        "summary": summary,
        "issues": issues
    }

@health_router.get("/alerts")
async def get_alerts(monitor: PerformanceMonitor = Depends(get_performance_monitor)):
    """Get current alerts and warnings"""
    try:
        # This would typically query an alerting system
        # For now, return basic performance alerts
        summary = monitor.get_performance_summary()
        alerts = []
        
        if summary.get("error_rate", 0) > 0.05:
            alerts.append({
                "type": "warning",
                "message": f"High error rate: {summary['error_rate']:.2%}",
                "timestamp": datetime.now().isoformat()
            })
        
        if summary.get("avg_response_time", 0) > 2.0:
            alerts.append({
                "type": "warning",
                "message": f"High response time: {summary['avg_response_time']:.3f}s",
                "timestamp": datetime.now().isoformat()
            })
        
        if summary.get("memory_usage_percent", 0) > 80:
            alerts.append({
                "type": "critical",
                "message": f"High memory usage: {summary['memory_usage_percent']:.1f}%",
                "timestamp": datetime.now().isoformat()
            })
        
        return {
            "alerts": alerts,
            "count": len(alerts),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Failed to get alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve alerts")

    try:
        
            db_status = await check_database_health()
            return {"status": "passed" if db_status["status"] == "healthy" else "failed", "details": db_status}
        
            redis_status = await check_redis_health()
            return {"status": "passed" if redis_status["status"] == "healthy" else "failed", "details": redis_status}
        
            monitor = get_performance_monitor()
            summary = monitor.get_performance_summary()
            return {"status": "passed" if summary.get("status") == "healthy" else "failed", "details": summary}
        
        else:
    
    except Exception as e:
        return {"status": "failed", "error": str(e)}
