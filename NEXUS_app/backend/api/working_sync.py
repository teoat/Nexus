"""
Working Sync API - Uses existing automation API as base
This provides a working sync system without routing conflicts
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/sync", tags=["sync"])

# In production, this would use Redis or database
sync_data = {
    "metrics": {
        "activeUsers": 0,
        "investigations": 0,
        "reconciliations": 0,
        "systemHealth": 100.0,
        "lastUpdated": datetime.now().isoformat()
    },
    "alerts": [],
    "automation": {
        "running": False,
        "activeTasks": 0,
        "lastStarted": None
    }
}

@router.get("/status")
async def get_sync_status():
    """Get sync system status"""
    try:
        return {
            "success": True,
            "data": {
                "status": "operational",
                "timestamp": datetime.now().isoformat(),
                "components": {
                    "metrics": "active",
                    "alerts": "active", 
                    "automation": "active"
                }
            }
        }
    except Exception as e:
        logger.error(f"Error getting sync status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
async def get_metrics():
    """Get current metrics"""
    try:
        return {
            "success": True,
            "data": sync_data["metrics"]
        }
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/metrics")
async def update_metrics(metrics: Dict[str, Any]):
    """Update metrics"""
    try:
        # Update metrics with new data
        sync_data["metrics"].update(metrics)
        sync_data["metrics"]["lastUpdated"] = datetime.now().isoformat()
        
        logger.info(f"Metrics updated: {metrics}")
        
        return {
            "success": True,
            "data": sync_data["metrics"],
            "message": "Metrics updated successfully"
        }
    except Exception as e:
        logger.error(f"Error updating metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts")
async def get_alerts():
    """Get current alerts"""
    try:
        return {
            "success": True,
            "data": sync_data["alerts"]
        }
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alerts")
async def add_alert(alert: Dict[str, Any]):
    """Add new alert"""
    try:
        alert_data = {
            "id": f"alert_{len(sync_data['alerts']) + 1}",
            "type": alert.get("type", "info"),
            "title": alert.get("title", "New Alert"),
            "description": alert.get("description", ""),
            "timestamp": datetime.now().isoformat(),
            "acknowledged": False
        }
        
        sync_data["alerts"].append(alert_data)
        
        logger.info(f"Alert added: {alert_data['title']}")
        
        return {
            "success": True,
            "data": alert_data,
            "message": "Alert added successfully"
        }
    except Exception as e:
        logger.error(f"Error adding alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str):
    """Acknowledge an alert"""
    try:
        for alert in sync_data["alerts"]:
            if alert["id"] == alert_id:
                alert["acknowledged"] = True
                alert["acknowledgedAt"] = datetime.now().isoformat()
                
                logger.info(f"Alert acknowledged: {alert_id}")
                
                return {
                    "success": True,
                    "data": alert,
                    "message": "Alert acknowledged successfully"
                }
        
        raise HTTPException(status_code=404, detail="Alert not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/automation")
async def get_automation_status():
    """Get automation status"""
    try:
        return {
            "success": True,
            "data": sync_data["automation"]
        }
    except Exception as e:
        logger.error(f"Error getting automation status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/automation/start")
async def start_automation():
    """Start automation"""
    try:
        sync_data["automation"]["running"] = True
        sync_data["automation"]["activeTasks"] = 1
        sync_data["automation"]["lastStarted"] = datetime.now().isoformat()
        
        logger.info("Automation started via sync API")
        
        return {
            "success": True,
            "data": sync_data["automation"],
            "message": "Automation started successfully"
        }
    except Exception as e:
        logger.error(f"Error starting automation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/automation/stop")
async def stop_automation():
    """Stop automation"""
    try:
        sync_data["automation"]["running"] = False
        sync_data["automation"]["activeTasks"] = 0
        
        logger.info("Automation stopped via sync API")
        
        return {
            "success": True,
            "data": sync_data["automation"],
            "message": "Automation stopped successfully"
        }
    except Exception as e:
        logger.error(f"Error stopping automation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/broadcast")
async def broadcast_update(update: Dict[str, Any]):
    """Broadcast update to all connected clients"""
    try:
        # In a real implementation, this would use WebSocket broadcasting
        logger.info(f"Broadcasting update: {update}")
        
        return {
            "success": True,
            "data": {
                "message": "Update broadcasted successfully",
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error broadcasting update: {e}")
        raise HTTPException(status_code=500, detail=str(e))


