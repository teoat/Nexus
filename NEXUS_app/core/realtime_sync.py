#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
Real-time Synchronization System for Nexus Platform
Provides WebSocket connections, live updates, and real-time data synchronization.
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import websockets
from websockets.server import WebSocketServerProtocol
import threading
import queue

logger = logging.getLogger(__name__)

class SyncEventType(Enum):
    """Types of synchronization events"""
    DATA_UPDATE = "data_update"
    CONFIG_CHANGE = "config_change"
    SYSTEM_STATUS = "system_status"
    METRICS_UPDATE = "metrics_update"
    AGENT_STATUS = "agent_status"
    TASK_UPDATE = "task_update"
    HEALTH_CHECK = "health_check"

@dataclass
class SyncEvent:
    """Synchronization event structure"""
    id: str
    type: SyncEventType
    data: Dict[str, Any]
    timestamp: str
    source: str
    target: Optional[str] = None  # None for broadcast
    
    def __post_init__(self):
        """
          Post Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

class RealtimeSyncManager:
    """Real-time synchronization manager"""
    
    def __init__(self, workspace_path: str, host: str = "localhost", port: int = 8765):
        """
          Init  
        
        
        Args:
            workspace_path: Description of workspace_path
            host: Description of host
            port: Description of port
    
        Example:
            TBD: Add usage example
        """
        self.workspace_path = workspace_path
        self.host = host
        self.port = port
        
        # WebSocket connections
        self.connections: Set[WebSocketServerProtocol] = set()
        self.connection_info: Dict[WebSocketServerProtocol, Dict[str, Any]] = {}
        
        # Event handling
        self.event_handlers: Dict[SyncEventType, List[Callable]] = {}
        self.event_queue = queue.Queue()
        
        # Data synchronization
        self.data_subscribers: Dict[str, Set[WebSocketServerProtocol]] = {}
        self.last_updates: Dict[str, Any] = {}
        
        # System status
        self.running = False
        self.server = None
        self.sync_thread = None
        
        # Initialize event handlers
        self._initialize_event_handlers()
    
    def _initialize_event_handlers(self):
        """Initialize default event handlers"""
        for event_type in SyncEventType:
            self.event_handlers[event_type] = []
    
    async def start_server(self):
        """Start the WebSocket server"""
        try:
            self.server = await websockets.serve(
                self.handle_connection,
                self.host,
                self.port
            )
            self.running = True
            
            # Start sync thread
            self.sync_thread = threading.Thread(target=self._sync_worker, daemon=True)
            self.sync_thread.start()
            
            logger.info(f"Real-time sync server started on {self.host}:{self.port}")
            
        except Exception as e:
            logger.error(f"Failed to start sync server: {e}")
            raise
    
    async def stop_server(self):
        """Stop the WebSocket server"""
        self.running = False
        
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        
        # Close all connections
        for connection in self.connections.copy():
            await connection.close()
        
        logger.info("Real-time sync server stopped")
    
    async def handle_connection(self, websocket: WebSocketServerProtocol, path: str):
        """Handle new WebSocket connection"""
        self.connections.add(websocket)
        self.connection_info[websocket] = {
            "id": str(uuid.uuid4()),
            "connected_at": datetime.now().isoformat(),
            "subscribed_to": set(),
            "last_ping": time.time()
        }
        
        logger.info(f"New connection: {self.connection_info[websocket]['id']}")
        
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logger.error(f"Error handling connection: {e}")
        finally:
            await self.cleanup_connection(websocket)
    
    async def handle_message(self, websocket: WebSocketServerProtocol, message: str):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            message_type = data.get("type")
            
            if message_type == "subscribe":
                await self.handle_subscribe(websocket, data)
            elif message_type == "unsubscribe":
                await self.handle_unsubscribe(websocket, data)
            elif message_type == "ping":
                await self.handle_ping(websocket, data)
            elif message_type == "request_data":
                await self.handle_data_request(websocket, data)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON message received")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def handle_subscribe(self, websocket: WebSocketServerProtocol, data: Dict[str, Any]):
        """Handle subscription request"""
        topic = data.get("topic")
        if not topic:
            await self.send_error(websocket, "Missing topic for subscription")
            return
        
        # Add to subscribers
        if topic not in self.data_subscribers:
            self.data_subscribers[topic] = set()
        self.data_subscribers[topic].add(websocket)
        
        # Update connection info
        self.connection_info[websocket]["subscribed_to"].add(topic)
        
        # Send confirmation
        await self.send_message(websocket, {
            "type": "subscription_confirmed",
            "topic": topic,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Client subscribed to {topic}")
    
    async def handle_unsubscribe(self, websocket: WebSocketServerProtocol, data: Dict[str, Any]):
        """Handle unsubscription request"""
        topic = data.get("topic")
        if not topic:
            await self.send_error(websocket, "Missing topic for unsubscription")
            return
        
        # Remove from subscribers
        if topic in self.data_subscribers:
            self.data_subscribers[topic].discard(websocket)
        
        # Update connection info
        self.connection_info[websocket]["subscribed_to"].discard(topic)
        
        # Send confirmation
        await self.send_message(websocket, {
            "type": "unsubscription_confirmed",
            "topic": topic,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"Client unsubscribed from {topic}")
    
    async def handle_ping(self, websocket: WebSocketServerProtocol, data: Dict[str, Any]):
        """Handle ping request"""
        self.connection_info[websocket]["last_ping"] = time.time()
        
        await self.send_message(websocket, {
            "type": "pong",
            "timestamp": datetime.now().isoformat()
        })
    
    async def handle_data_request(self, websocket: WebSocketServerProtocol, data: Dict[str, Any]):
        """Handle data request"""
        topic = data.get("topic")
        if not topic:
            await self.send_error(websocket, "Missing topic for data request")
            return
        
    
    async def send_message(self, websocket: WebSocketServerProtocol, message: Dict[str, Any]):
        """Send message to WebSocket client"""
        try:
            await websocket.send(json.dumps(message))
        except websockets.exceptions.ConnectionClosed:
            await self.cleanup_connection(websocket)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    async def send_error(self, websocket: WebSocketServerProtocol, error_message: str):
        """Send error message to WebSocket client"""
        await self.send_message(websocket, {
            "type": "error",
            "message": error_message,
            "timestamp": datetime.now().isoformat()
        })
    
    async def cleanup_connection(self, websocket: WebSocketServerProtocol):
        """Clean up disconnected WebSocket connection"""
        if websocket in self.connections:
            self.connections.remove(websocket)
        
        if websocket in self.connection_info:
            # Remove from all subscriptions
            subscribed_to = self.connection_info[websocket].get("subscribed_to", set())
            for topic in subscribed_to:
                if topic in self.data_subscribers:
                    self.data_subscribers[topic].discard(websocket)
            
            del self.connection_info[websocket]
        
        logger.info("Connection cleaned up")
    
    def publish_event(self, event: SyncEvent):
        """Publish a synchronization event"""
        try:
            # Add to event queue
            self.event_queue.put(event)
            
            # Update last updates
            self.last_updates[event.type.value] = event.data
            
            # Notify event handlers
            for handler in self.event_handlers.get(event.type, []):
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler: {e}")
            
            logger.debug(f"Published event: {event.type.value}")
            
        except Exception as e:
            logger.error(f"Error publishing event: {e}")
    
    def subscribe_to_events(self, event_type: SyncEventType, handler: Callable):
        """
        Subscribe To Events
        
        
        Args:
            event_type: Description of event_type
            handler: Description of handler
    
        Example:
            TBD: Add usage example
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def _sync_worker(self):
        """Background worker for processing sync events"""
        while self.running:
            try:
                if not self.event_queue.empty():
                    event = self.event_queue.get_nowait()
                    asyncio.create_task(self._broadcast_event(event))
                else:
                    time.sleep(0.1)
            except Exception as e:
                logger.error(f"Error in sync worker: {e}")
                time.sleep(1)
    
    async def _broadcast_event(self, event: SyncEvent):
        """Broadcast event to subscribed clients"""
        try:
            # Get subscribers for this event type
            subscribers = self.data_subscribers.get(event.type.value, set())
            
            if not subscribers:
                return
            
            # Prepare message
            message = {
                "type": "sync_event",
                "event_type": event.type.value,
                "data": event.data,
                "timestamp": event.timestamp,
                "source": event.source
            }
            
            # Send to all subscribers
            disconnected = set()
            for websocket in subscribers:
                try:
                    await self.send_message(websocket, message)
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(websocket)
                except Exception as e:
                    logger.error(f"Error broadcasting to client: {e}")
                    disconnected.add(websocket)
            
            # Clean up disconnected clients
            for websocket in disconnected:
                await self.cleanup_connection(websocket)
            
        except Exception as e:
            logger.error(f"Error broadcasting event: {e}")
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        return {
            "total_connections": len(self.connections),
            "active_subscriptions": sum(len(subs) for subs in self.data_subscribers.values()),
            "event_queue_size": self.event_queue.qsize(),
            "last_updates_count": len(self.last_updates),
            "connections": [
                {
                    "id": info["id"],
                    "connected_at": info["connected_at"],
                    "subscribed_to": list(info["subscribed_to"]),
                    "last_ping": info["last_ping"]
                }
                for info in self.connection_info.values()
            ]
        }
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get real-time system metrics"""
        return {
            "websocket_server": {
                "running": self.running,
                "host": self.host,
                "port": self.port,
                "connections": len(self.connections)
            },
            "sync_system": {
                "event_types": len(self.event_handlers),
                "subscribers": len(self.data_subscribers),
                "last_updates": len(self.last_updates),
                "queue_size": self.event_queue.qsize()
            },
            "timestamp": datetime.now().isoformat()
        }
    
    async def shutdown(self):
        """Shutdown the real-time sync system"""
        await self.stop_server()
        logger.info("Real-time sync system shutdown complete")
