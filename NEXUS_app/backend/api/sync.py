from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import asyncio
import json
import redis
from core.database import get_database_health

logger = logging.getLogger(__name__)

router = APIRouter(tags=["sync"])

# Redis client for real-time sync
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()
    logger.info("Redis client initialized successfully")
except Exception as e:
    redis_client = None

    
    def __init__(self):
        self._data = {}
    
    def ping(self):
        return True
    
    def get(self, key):
        return self._data.get(key)
    
    def setex(self, key, time, value):
        self._data[key] = value
        return True
    
    def publish(self, channel, message):
        return 1
    
    def pubsub(self):

    
    def __init__(self):
        self._subscribed = False
    
    async def subscribe(self, channel):
        self._subscribed = True
    
    async def listen(self):

if redis_client is None:

@router.get("/status")
async def get_sync_status():
    """Get real-time synchronization status"""
    try:
        # Check Redis connection
        redis_health = "healthy" if redis_client.ping() else "unhealthy"
        
        # Get WebSocket connections count
        ws_connections = await get_websocket_connections_count()
        
        return {
            "success": True,
            "data": {
                "redis_health": redis_health,
                "websocket_connections": ws_connections,
                "last_sync": datetime.now().isoformat(),
                "active_subscriptions": await get_active_subscriptions()
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting sync status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get sync status")

@router.post("/{entity_type}")
async def sync_entity(entity_type: str, data: Dict[str, Any], background_tasks: BackgroundTasks):
    """Sync entity data to all connected clients"""
    try:
        # Store entity data in Redis
        entity_id = data.get("id", "default")
        redis_key = f"entity:{entity_type}:{entity_id}"
        
        sync_data = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "source": "api"
        }
        
        # Store in Redis
        redis_client.setex(redis_key, 3600, json.dumps(sync_data))  # 1 hour TTL
        
        # Publish sync event
        await publish_sync_event(sync_data)
        
        # Background task to update related entities
        background_tasks.add_task(update_related_entities, entity_type, data)
        
        return {
            "success": True,
            "message": f"Entity {entity_type}:{entity_id} synced successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error syncing entity {entity_type}: {e}")
        raise HTTPException(status_code=500, detail="Failed to sync entity")

@router.get("/{entity_type}/{entity_id}")
async def get_entity(entity_type: str, entity_id: str):
    """Get entity data from Redis"""
    try:
        redis_key = f"entity:{entity_type}:{entity_id}"
        data = redis_client.get(redis_key)
        
        if not data:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        entity_data = json.loads(data)
        
        return {
            "success": True,
            "data": entity_data,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting entity {entity_type}:{entity_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get entity")

@router.post("/broadcast")
async def broadcast_message(message: Dict[str, Any], background_tasks: BackgroundTasks):
    """Broadcast message to all connected clients"""
    try:
        # Publish broadcast event
        broadcast_data = {
            "type": "broadcast",
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        await publish_sync_event(broadcast_data)
        
        return {
            "success": True,
            "message": "Broadcast sent successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error broadcasting message: {e}")
        raise HTTPException(status_code=500, detail="Failed to broadcast message")

async def publish_sync_event(event_data: Dict[str, Any]):
    """Publish sync event to Redis channel"""
    try:
        channel = "sync_events"
        message = json.dumps(event_data)
        redis_client.publish(channel, message)
        logger.info(f"Published sync event: {event_data['entity_type']}")
    except Exception as e:
        logger.error(f"Error publishing sync event: {e}")

async def get_websocket_connections_count() -> int:
    """Get count of active WebSocket connections"""
    try:
        # This would be implemented based on your WebSocket server

async def get_active_subscriptions() -> List[str]:
    """Get list of active entity subscriptions"""
    try:
        # This would be implemented based on your WebSocket server

async def update_related_entities(entity_type: str, data: Dict[str, Any]):
    """Update related entities when an entity changes"""
    try:
        if entity_type == "automation":
            # Update metrics when automation changes
            metrics_data = {
                "id": "metrics",
                "activeUsers": data.get("activeTasks", 0),
                "lastUpdated": datetime.now().isoformat()
            }
            await sync_entity("metrics", metrics_data, None)
            
        elif entity_type == "metrics":
            # Update system health when metrics change
            health_data = {
                "id": "system_health",
                "overall": "healthy" if data.get("systemHealth", 0) > 95 else "unhealthy",
                "lastUpdated": datetime.now().isoformat()
            }
            await sync_entity("system_health", health_data, None)
            
    except Exception as e:
        logger.error(f"Error updating related entities: {e}")
