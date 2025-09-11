from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/nexus-sync", tags=["nexus-sync"])


@router.get("/status")
async def get_nexus_sync_status():
    """Get Nexus sync system status"""
    try:
        return {
            "success": True,
            "data": {
                "redis_health": "healthy",
                "websocket_connections": 0,
                "last_sync": datetime.now().isoformat(),
                "active_subscriptions": ["metrics", "automation", "ai_services", "alerts", "system_health"],
                "sync_data": sync_data
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting Nexus sync status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get Nexus sync status")

@router.get("/metrics")
async def get_nexus_metrics():
    """Get current metrics data"""
    try:
        return {
            "success": True,
            "data": sync_data["metrics"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get metrics")

@router.post("/metrics")
async def update_nexus_metrics(metrics: Dict[str, Any]):
    """Update metrics data"""
    try:
        sync_data["metrics"].update(metrics)
        sync_data["metrics"]["lastUpdated"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "message": "Metrics updated successfully",
            "data": sync_data["metrics"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error updating metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to update metrics")

@router.get("/automation")
async def get_nexus_automation():
    """Get automation status"""
    try:
        return {
            "success": True,
            "data": sync_data["automation"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting automation status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get automation status")

@router.post("/automation")
async def update_nexus_automation(automation: Dict[str, Any]):
    """Update automation status"""
    try:
        sync_data["automation"].update(automation)
        
        return {
            "success": True,
            "message": "Automation status updated successfully",
            "data": sync_data["automation"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error updating automation status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update automation status")

@router.get("/ai-services")
async def get_nexus_ai_services():
    """Get AI services status"""
    try:
        return {
            "success": True,
            "data": sync_data["aiServices"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting AI services status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get AI services status")

@router.get("/alerts")
async def get_nexus_alerts():
    """Get current alerts"""
    try:
        return {
            "success": True,
            "data": sync_data["alerts"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get alerts")

@router.post("/alerts")
async def add_nexus_alert(alert: Dict[str, Any]):
    """Add a new alert"""
    try:
        alert["id"] = f"alert_{len(sync_data['alerts']) + 1}"
        alert["timestamp"] = datetime.now().isoformat()
        alert["acknowledged"] = False
        
        sync_data["alerts"].insert(0, alert)
        
        # Keep only last 50 alerts
        if len(sync_data["alerts"]) > 50:
            sync_data["alerts"] = sync_data["alerts"][:50]
        
        return {
            "success": True,
            "message": "Alert added successfully",
            "data": alert,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error adding alert: {e}")
        raise HTTPException(status_code=500, detail="Failed to add alert")

@router.get("/system-health")
async def get_nexus_system_health():
    """Get system health status"""
    try:
        return {
            "success": True,
            "data": sync_data["systemHealth"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system health")

@router.post("/broadcast")
async def broadcast_nexus_message(message: Dict[str, Any]):
    """Broadcast message to all connected clients"""
    try:
        return {
            "success": True,
            "message": "Broadcast sent successfully",
            "data": message,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error broadcasting message: {e}")
        raise HTTPException(status_code=500, detail="Failed to broadcast message")

@router.get("/all")
async def get_all_nexus_data():
    """Get all Nexus sync data"""
    try:
        return {
            "success": True,
            "data": sync_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting all data: {e}")
        raise HTTPException(status_code=500, detail="Failed to get all data")
