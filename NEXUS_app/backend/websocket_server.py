#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
WebSocket Server for Real-time Synchronization
Handles WebSocket connections and real-time data sync
"""

import asyncio
import json
import logging
import websockets
from datetime import datetime
from typing import Dict, Set, Any
import redis
from core.redis_client import get_redis_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSocketServer:
    """WebSocket server for real-time synchronization"""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        """
          Init  
        
        
        Args:
            host: Description of host
            port: Description of port
    
        Example:
            TBD: Add usage example
        """
        self.host = host
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.subscriptions: Dict[websockets.WebSocketServerProtocol, Set[str]] = {}
        self.redis_client = get_redis_client()
        self.running = False
        
    async def register_client(self, websocket: websockets.WebSocketServerProtocol):
        """Register a new WebSocket client"""
        self.clients.add(websocket)
        self.subscriptions[websocket] = set()
        logger.info(f"Client connected. Total clients: {len(self.clients)}")
        
    async def unregister_client(self, websocket: websockets.WebSocketServerProtocol):
        """Unregister a WebSocket client"""
        self.clients.discard(websocket)
        self.subscriptions.pop(websocket, None)
        logger.info(f"Client disconnected. Total clients: {len(self.clients)}")
        
    async def handle_message(self, websocket: websockets.WebSocketServerProtocol, message: str):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'subscribe':
                entity_types = data.get('entity_types', [])
                self.subscriptions[websocket].update(entity_types)
                logger.info(f"Client subscribed to: {entity_types}")
                
                # Send confirmation
                await websocket.send(json.dumps({
                    'type': 'subscription_confirmed',
                    'entity_types': entity_types
                }))
                
            elif message_type == 'unsubscribe':
                entity_types = data.get('entity_types', [])
                self.subscriptions[websocket] -= set(entity_types)
                logger.info(f"Client unsubscribed from: {entity_types}")
                
            elif message_type == 'sync_request':
                entity_type = data.get('entity_type')
                entity_id = data.get('entity_id')
                await self.handle_sync_request(websocket, entity_type, entity_id)
                
            elif message_type == 'ping':
                await websocket.send(json.dumps({'type': 'pong'}))
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON message received")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def handle_sync_request(self, websocket: websockets.WebSocketServerProtocol, entity_type: str, entity_id: str):
        """Handle sync request from client"""
        try:
            # Get entity data from Redis
            redis_key = f"entity:{entity_type}:{entity_id}"
            data = self.redis_client.get(redis_key)
            
            if data:
                entity_data = json.loads(data)
                await websocket.send(json.dumps({
                    'type': 'sync_response',
                    'entity_type': entity_type,
                    'entity_id': entity_id,
                    'data': entity_data
                }))
            else:
                await websocket.send(json.dumps({
                    'type': 'sync_error',
                    'entity_type': entity_type,
                    'entity_id': entity_id,
                    'error': 'Entity not found'
                }))
                
        except Exception as e:
            logger.error(f"Error handling sync request: {e}")
            await websocket.send(json.dumps({
                'type': 'sync_error',
                'entity_type': entity_type,
                'entity_id': entity_id,
                'error': str(e)
            }))
    
    async def broadcast_to_subscribers(self, entity_type: str, data: Dict[str, Any]):
        """Broadcast data to all subscribers of an entity type"""
        if not self.clients:
            return
            
        message = json.dumps({
            'type': 'sync_event',
            'entity_type': entity_type,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
        
        # Send to all clients subscribed to this entity type
        disconnected_clients = set()
        for client in self.clients:
            try:
                if entity_type in self.subscriptions.get(client, set()):
                    await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.add(client)
            except Exception as e:
                logger.error(f"Error sending to client: {e}")
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        for client in disconnected_clients:
            await self.unregister_client(client)
    
    async def start_redis_listener(self):
        """Start listening to Redis pub/sub for sync events"""
        try:
            pubsub = self.redis_client.pubsub()
            await pubsub.subscribe('sync_events')
            
            logger.info("Started Redis listener for sync events")
            
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        entity_type = data.get('entity_type')
                        if entity_type:
                            await self.broadcast_to_subscribers(entity_type, data)
                    except Exception as e:
                        logger.error(f"Error processing Redis message: {e}")
                        
        except Exception as e:
            logger.error(f"Error in Redis listener: {e}")
    
    async def handle_client(self, websocket: websockets.WebSocketServerProtocol, path: str):
        """Handle individual WebSocket client connection"""
        await self.register_client(websocket)
        
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logger.error(f"Error handling client: {e}")
        finally:
            await self.unregister_client(websocket)
    
    async def start_server(self):
        """Start the WebSocket server"""
        try:
            logger.info(f"Starting WebSocket server on {self.host}:{self.port}")
            
            # Start Redis listener in background
            asyncio.create_task(self.start_redis_listener())
            
            # Start WebSocket server
            self.running = True
            async with websockets.serve(self.handle_client, self.host, self.port):
                logger.info("WebSocket server started successfully")
                await asyncio.Future()  # Run forever
                
        except Exception as e:
            logger.error(f"Error starting WebSocket server: {e}")
            self.running = False
    
    async def stop_server(self):
        """Stop the WebSocket server"""
        self.running = False
        logger.info("WebSocket server stopped")


if __name__ == "__main__":
    asyncio.run(main())
