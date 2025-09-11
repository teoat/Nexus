#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🌐 Frenly AI WebSocket Handler
Real-time communication and streaming for AI responses
"""

import asyncio
import logging
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Set, Callable
from dataclasses import dataclass, field
from enum import Enum
from fastapi import WebSocket, WebSocketDisconnect
from backend.config import get_config

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """WebSocket message type enumeration"""
    REQUEST = "request"
    RESPONSE = "response"
    STREAMING = "streaming"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    STATUS = "status"
    NOTIFICATION = "notification"

class ConnectionStatus(Enum):
    """Connection status enumeration"""
    CONNECTED = "connected"
    AUTHENTICATED = "authenticated"
    DISCONNECTED = "disconnected"
    ERROR = "error"

@dataclass
class WebSocketMessage:
    """WebSocket message definition"""
    id: str
    type: MessageType
    data: Dict[str, Any]
    timestamp: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None

@dataclass
class Connection:
    """WebSocket connection definition"""
    websocket: WebSocket
    connection_id: str
    status: ConnectionStatus
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    connected_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_activity: str = field(default_factory=lambda: datetime.now().isoformat())
    message_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

class WebSocketManager:
    """Manages WebSocket connections and real-time communication"""
    
    def __init__(self):
        """
          Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        self.config = get_config()
        self.active_connections: Dict[str, Connection] = {}
        self.connection_groups: Dict[str, Set[str]] = {}  # group_name -> set of connection_ids
        self.message_handlers: Dict[MessageType, Callable] = {}
        self.running = False
        
        # WebSocket configuration
        self.heartbeat_interval = 30  # seconds
        self.connection_timeout = 300  # 5 minutes
        self.max_connections = 1000
        
        # Initialize message handlers
        self._initialize_message_handlers()
        
        logger.info("✅ WebSocket Manager initialized")
    
    def _initialize_message_handlers(self):
        """Initialize message handlers for different message types"""
        self.message_handlers = {
            MessageType.REQUEST: self._handle_request_message,
            MessageType.HEARTBEAT: self._handle_heartbeat_message,
            MessageType.STATUS: self._handle_status_message,
            MessageType.NOTIFICATION: self._handle_notification_message
        }
    
    async def start(self):
        """Start the WebSocket manager"""
        self.running = True
        logger.info("🚀 Starting WebSocket Manager...")
        
        # Start background tasks
        asyncio.create_task(self._heartbeat_monitor())
        asyncio.create_task(self._connection_cleanup())
        
        logger.info("✅ WebSocket Manager started")
    
    async def stop(self):
        """Stop the WebSocket manager"""
        self.running = False
        logger.info("🛑 Stopping WebSocket Manager...")
        
        # Close all connections
        for connection in self.active_connections.values():
            try:
                await connection.websocket.close()
            except Exception as e:
                logger.error(f"❌ Error closing connection {connection.connection_id}: {e}")
        
        self.active_connections.clear()
        self.connection_groups.clear()
        
        logger.info("✅ WebSocket Manager stopped")
    
    async def connect(self, websocket: WebSocket, connection_id: Optional[str] = None) -> str:
        """Accept new WebSocket connection"""
        try:
            # Generate connection ID if not provided
            if not connection_id:
                connection_id = str(uuid.uuid4())
            
            # Check connection limit
            if len(self.active_connections) >= self.max_connections:
                await websocket.close(code=1013, reason="Server overloaded")
                raise Exception("Maximum connections exceeded")
            
            # Accept WebSocket connection
            await websocket.accept()
            
            # Create connection object
            connection = Connection(
                websocket=websocket,
                connection_id=connection_id,
                status=ConnectionStatus.CONNECTED
            )
            
            # Store connection
            self.active_connections[connection_id] = connection
            
            logger.info(f"✅ WebSocket connected: {connection_id}")
            
            # Send welcome message
            await self._send_message(connection_id, MessageType.STATUS, {
                "message": "Connected to Frenly AI WebSocket",
                "connection_id": connection_id,
                "timestamp": datetime.now().isoformat()
            })
            
            return connection_id
            
        except Exception as e:
            logger.error(f"❌ Error connecting WebSocket: {e}")
            raise
    
    async def disconnect(self, connection_id: str):
        """Disconnect WebSocket connection"""
        try:
            if connection_id in self.active_connections:
                connection = self.active_connections[connection_id]
                
                # Close WebSocket
                try:
                    await connection.websocket.close()
                except Exception as e:
                    logger.warning(f"⚠️ Error closing WebSocket {connection_id}: {e}")
                
                # Remove from groups
                for group_name, connections in self.connection_groups.items():
                    connections.discard(connection_id)
                
                # Remove connection
                del self.active_connections[connection_id]
                
                logger.info(f"✅ WebSocket disconnected: {connection_id}")
            
        except Exception as e:
            logger.error(f"❌ Error disconnecting WebSocket {connection_id}: {e}")
    
    async def authenticate_connection(self, connection_id: str, user_id: str, session_id: Optional[str] = None) -> bool:
        """Authenticate WebSocket connection"""
        try:
            if connection_id not in self.active_connections:
                return False
            
            connection = self.active_connections[connection_id]
            connection.user_id = user_id
            connection.session_id = session_id
            connection.status = ConnectionStatus.AUTHENTICATED
            
            # Send authentication confirmation
            await self._send_message(connection_id, MessageType.STATUS, {
                "message": "Authentication successful",
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"✅ WebSocket authenticated: {connection_id} (user: {user_id})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error authenticating connection {connection_id}: {e}")
            return False
    
    async def send_message(self, connection_id: str, message_type: MessageType, data: Dict[str, Any]) -> bool:
        try:
            if connection_id not in self.active_connections:
                return False
            
            return await self._send_message(connection_id, message_type, data)
            
        except Exception as e:
            logger.error(f"❌ Error sending message to {connection_id}: {e}")
            return False
    
    async def broadcast_message(self, message_type: MessageType, data: Dict[str, Any], 
                              group_name: Optional[str] = None) -> int:
        try:
            sent_count = 0
            
            if group_name and group_name in self.connection_groups:
                for connection_id in self.connection_groups[group_name]:
                    if await self._send_message(connection_id, message_type, data):
                        sent_count += 1
            else:
                # Send to all connections
                for connection_id in self.active_connections:
                    if await self._send_message(connection_id, message_type, data):
                        sent_count += 1
            
            logger.debug(f"Broadcast message sent to {sent_count} connections")
            return sent_count
            
        except Exception as e:
            logger.error(f"❌ Error broadcasting message: {e}")
            return 0
    
    async def add_to_group(self, connection_id: str, group_name: str) -> bool:
        """Add connection to group"""
        try:
            if connection_id not in self.active_connections:
                return False
            
            if group_name not in self.connection_groups:
                self.connection_groups[group_name] = set()
            
            self.connection_groups[group_name].add(connection_id)
            
            logger.debug(f"Connection {connection_id} added to group {group_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding connection to group: {e}")
            return False
    
    async def remove_from_group(self, connection_id: str, group_name: str) -> bool:
        """Remove connection from group"""
        try:
            if group_name in self.connection_groups:
                self.connection_groups[group_name].discard(connection_id)
                
                # Remove empty groups
                if not self.connection_groups[group_name]:
                    del self.connection_groups[group_name]
                
                logger.debug(f"Connection {connection_id} removed from group {group_name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error removing connection from group: {e}")
            return False
    
    async def handle_message(self, connection_id: str, message: str):
        """Handle incoming WebSocket message"""
        try:
            if connection_id not in self.active_connections:
                return
            
            # Parse message
            try:
                message_data = json.loads(message)
            except json.JSONDecodeError:
                await self._send_error(connection_id, "Invalid JSON message")
                return
            
            # Create WebSocket message object
            ws_message = WebSocketMessage(
                id=message_data.get("id", str(uuid.uuid4())),
                type=MessageType(message_data.get("type", "request")),
                data=message_data.get("data", {}),
                timestamp=datetime.now().isoformat(),
                session_id=message_data.get("session_id"),
                user_id=message_data.get("user_id")
            )
            
            # Update connection activity
            connection = self.active_connections[connection_id]
            connection.last_activity = datetime.now().isoformat()
            connection.message_count += 1
            
            # Handle message based on type
            if ws_message.type in self.message_handlers:
                await self.message_handlers[ws_message.type](connection_id, ws_message)
            else:
                await self._send_error(connection_id, f"Unknown message type: {ws_message.type}")
            
        except Exception as e:
            logger.error(f"❌ Error handling message from {connection_id}: {e}")
            await self._send_error(connection_id, "Error processing message")
    
    async def _handle_request_message(self, connection_id: str, message: WebSocketMessage):
        """Handle request message"""
        try:
            # Process AI request
            request_data = message.data
            
            response_data = {
                "request_id": message.id,
                "response": f"AI response for: {request_data.get('message', '')[:50]}...",
                "confidence": 0.85,
                "processing_time": 0.5,
                "timestamp": datetime.now().isoformat()
            }
            
            # Send response
            await self._send_message(connection_id, MessageType.RESPONSE, response_data)
            
        except Exception as e:
            logger.error(f"❌ Error handling request message: {e}")
            await self._send_error(connection_id, "Error processing request")
    
    async def _handle_heartbeat_message(self, connection_id: str, message: WebSocketMessage):
        """Handle heartbeat message"""
        try:
            # Send heartbeat response
            await self._send_message(connection_id, MessageType.HEARTBEAT, {
                "message": "pong",
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"❌ Error handling heartbeat message: {e}")
    
    async def _handle_status_message(self, connection_id: str, message: WebSocketMessage):
        """Handle status message"""
        try:
            # Send status response
            connection = self.active_connections[connection_id]
            status_data = {
                "connection_id": connection_id,
                "status": connection.status.value,
                "user_id": connection.user_id,
                "session_id": connection.session_id,
                "connected_at": connection.connected_at,
                "message_count": connection.message_count,
                "timestamp": datetime.now().isoformat()
            }
            
            await self._send_message(connection_id, MessageType.STATUS, status_data)
            
        except Exception as e:
            logger.error(f"❌ Error handling status message: {e}")
    
    async def _handle_notification_message(self, connection_id: str, message: WebSocketMessage):
        """Handle notification message"""
        try:
            # Process notification
            notification_data = message.data
            
            # Echo notification back
            await self._send_message(connection_id, MessageType.NOTIFICATION, {
                "message": "Notification received",
                "data": notification_data,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"❌ Error handling notification message: {e}")
    
    async def _send_message(self, connection_id: str, message_type: MessageType, data: Dict[str, Any]) -> bool:
        """Send message to connection"""
        try:
            if connection_id not in self.active_connections:
                return False
            
            connection = self.active_connections[connection_id]
            
            # Create message
            message = {
                "id": str(uuid.uuid4()),
                "type": message_type.value,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }
            
            # Send message
            await connection.websocket.send_text(json.dumps(message))
            
            return True
            
        except WebSocketDisconnect:
            await self.disconnect(connection_id)
            return False
        except Exception as e:
            logger.error(f"❌ Error sending message to {connection_id}: {e}")
            return False
    
    async def _send_error(self, connection_id: str, error_message: str):
        """Send error message"""
        try:
            await self._send_message(connection_id, MessageType.ERROR, {
                "error": error_message,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"❌ Error sending error message: {e}")
    
    async def _heartbeat_monitor(self):
        """Monitor connections and send heartbeats"""
        while self.running:
            try:
                current_time = datetime.now()
                inactive_connections = []
                
                for connection_id, connection in self.active_connections.items():
                    last_activity = datetime.fromisoformat(connection.last_activity)
                    
                    # Check if connection is inactive
                    if (current_time - last_activity).total_seconds() > self.connection_timeout:
                        inactive_connections.append(connection_id)
                        continue
                    
                    # Send heartbeat
                    try:
                        await self._send_message(connection_id, MessageType.HEARTBEAT, {
                            "message": "ping",
                            "timestamp": current_time.isoformat()
                        })
                    except Exception as e:
                        logger.warning(f"⚠️ Error sending heartbeat to {connection_id}: {e}")
                        inactive_connections.append(connection_id)
                
                # Remove inactive connections
                for connection_id in inactive_connections:
                    await self.disconnect(connection_id)
                
                await asyncio.sleep(self.heartbeat_interval)
                
            except Exception as e:
                logger.error(f"❌ Error in heartbeat monitor: {e}")
                await asyncio.sleep(60)
    
    async def _connection_cleanup(self):
        """Clean up disconnected connections"""
        while self.running:
            try:
                # Remove connections that are no longer active
                disconnected_connections = []
                
                for connection_id, connection in self.active_connections.items():
                    try:
                        # Try to send a ping to check if connection is alive
                        await connection.websocket.ping()
                    except Exception:
                        disconnected_connections.append(connection_id)
                
                for connection_id in disconnected_connections:
                    await self.disconnect(connection_id)
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Error in connection cleanup: {e}")
                await asyncio.sleep(60)
    
    async def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics"""
        try:
            total_connections = len(self.active_connections)
            authenticated_connections = len([
                c for c in self.active_connections.values() 
                if c.status == ConnectionStatus.AUTHENTICATED
            ])
            
            total_messages = sum(c.message_count for c in self.active_connections.values())
            
            group_stats = {
                group_name: len(connections) 
                for group_name, connections in self.connection_groups.items()
            }
            
            return {
                "total_connections": total_connections,
                "authenticated_connections": authenticated_connections,
                "total_messages": total_messages,
                "groups": group_stats,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting connection stats: {e}")
            return {}

# Global WebSocket manager instance
websocket_manager = WebSocketManager()
