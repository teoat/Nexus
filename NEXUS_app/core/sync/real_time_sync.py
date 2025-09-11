"""
Real-time Data Synchronization Engine
Handles real-time data synchronization across all NEXUS Platform components
"""

import asyncio
import json
import time
import uuid
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import redis
import aioredis
from sqlalchemy.orm import Session
from sqlalchemy import text
import websockets
from websockets.server import WebSocketServerProtocol
import logging

logger = logging.getLogger(__name__)


class SyncEventType(Enum):
    """Types of synchronization events"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    SYNC = "sync"
    CONFLICT = "conflict"
    RESOLVE = "resolve"


class SyncStatus(Enum):
    """Synchronization status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"


@dataclass
class SyncEvent:
    """Synchronization event data structure"""
    id: str
    event_type: SyncEventType
    entity_type: str
    entity_id: str
    data: Dict[str, Any]
    timestamp: float
    source: str
    version: int
    status: SyncStatus = SyncStatus.PENDING
    conflicts: List[str] = None
    resolved_by: Optional[str] = None

    def __post_init__(self):
        """
          Post Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        if self.conflicts is None:
            self.conflicts = []


class ConflictResolver:
    """Handles conflict resolution for synchronized data"""
    
    def __init__(self):
        """
          Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        self.resolution_strategies = {
            "last_write_wins": self._last_write_wins,
            "first_write_wins": self._first_write_wins,
            "merge": self._merge_data,
            "manual": self._manual_resolution
        }
    
    def resolve_conflict(self, local_event: SyncEvent, remote_event: SyncEvent, 
                        strategy: str = "last_write_wins") -> SyncEvent:
        """Resolve conflict between local and remote events"""
        if strategy not in self.resolution_strategies:
            raise ValueError(f"Unknown resolution strategy: {strategy}")
        
        return self.resolution_strategies[strategy](local_event, remote_event)
    
    def _last_write_wins(self, local_event: SyncEvent, remote_event: SyncEvent) -> SyncEvent:
        """Last write wins conflict resolution"""
        if local_event.timestamp > remote_event.timestamp:
            return local_event
        return remote_event
    
    def _first_write_wins(self, local_event: SyncEvent, remote_event: SyncEvent) -> SyncEvent:
        """First write wins conflict resolution"""
        if local_event.timestamp < remote_event.timestamp:
            return local_event
        return remote_event
    
    def _merge_data(self, local_event: SyncEvent, remote_event: SyncEvent) -> SyncEvent:
        """Merge data from both events"""
        merged_data = {**local_event.data, **remote_event.data}
        merged_event = SyncEvent(
            id=str(uuid.uuid4()),
            event_type=SyncEventType.UPDATE,
            entity_type=local_event.entity_type,
            entity_id=local_event.entity_id,
            data=merged_data,
            timestamp=max(local_event.timestamp, remote_event.timestamp),
            source="merged",
            version=max(local_event.version, remote_event.version) + 1
        )
        return merged_event
    
    def _manual_resolution(self, local_event: SyncEvent, remote_event: SyncEvent) -> SyncEvent:
        """Manual resolution - mark for human intervention"""
        local_event.status = SyncStatus.CONFLICT
        local_event.conflicts.append(remote_event.id)
        return local_event


class RealTimeSyncEngine:
    """Main real-time synchronization engine"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0", 
        """
          Init  
        
        
        Args:
            redis_url: Description of redis_url
            db_session: Description of db_session
    
        Example:
            TBD: Add usage example
        """
                 db_session: Optional[Session] = None):
        self.redis_url = redis_url
        self.db_session = db_session
        self.redis_client = None
        self.websocket_clients: List[WebSocketServerProtocol] = []
        self.conflict_resolver = ConflictResolver()
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.sync_queue = asyncio.Queue()
        self.is_running = False
        
    async def initialize(self):
        """Initialize the synchronization engine"""
        try:
            self.redis_client = await aioredis.from_url(self.redis_url)
            logger.info("Real-time sync engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize sync engine: {e}")
            raise
    
    async def start(self):
        """Start the synchronization engine"""
        if self.is_running:
            return
        
        self.is_running = True
        await self.initialize()
        
        # Start background tasks
        asyncio.create_task(self._process_sync_queue())
        asyncio.create_task(self._monitor_conflicts())
        asyncio.create_task(self._cleanup_old_events())
        
        logger.info("Real-time sync engine started")
    
    async def stop(self):
        """Stop the synchronization engine"""
        self.is_running = False
        
        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()
        
        # Close WebSocket connections
        for client in self.websocket_clients:
            await client.close()
        
        logger.info("Real-time sync engine stopped")
    
    async def sync_event(self, event: SyncEvent) -> bool:
        """Synchronize an event across all components"""
        try:
            # Add to sync queue
            await self.sync_queue.put(event)
            
            # Store event in Redis
            await self._store_event(event)
            
            # Broadcast to WebSocket clients
            await self._broadcast_event(event)
            
            # Process event handlers
            await self._process_event_handlers(event)
            
            logger.info(f"Event {event.id} synchronized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to sync event {event.id}: {e}")
            event.status = SyncStatus.FAILED
            return False
    
    async def create_entity(self, entity_type: str, entity_id: str, 
                           data: Dict[str, Any], source: str = "local") -> SyncEvent:
        """Create a new entity and sync it"""
        event = SyncEvent(
            id=str(uuid.uuid4()),
            event_type=SyncEventType.CREATE,
            entity_type=entity_type,
            entity_id=entity_id,
            data=data,
            timestamp=time.time(),
            source=source,
            version=1
        )
        
        await self.sync_event(event)
        return event
    
    async def update_entity(self, entity_type: str, entity_id: str, 
                           data: Dict[str, Any], source: str = "local") -> SyncEvent:
        """Update an entity and sync it"""
        # Get current version
        current_version = await self._get_entity_version(entity_type, entity_id)
        
        event = SyncEvent(
            id=str(uuid.uuid4()),
            event_type=SyncEventType.UPDATE,
            entity_type=entity_type,
            entity_id=entity_id,
            data=data,
            timestamp=time.time(),
            source=source,
            version=current_version + 1
        )
        
        await self.sync_event(event)
        return event
    
    async def delete_entity(self, entity_type: str, entity_id: str, 
                           source: str = "local") -> SyncEvent:
        """Delete an entity and sync it"""
        event = SyncEvent(
            id=str(uuid.uuid4()),
            event_type=SyncEventType.DELETE,
            entity_type=entity_type,
            entity_id=entity_id,
            data={},
            timestamp=time.time(),
            source=source,
            version=await self._get_entity_version(entity_type, entity_id) + 1
        )
        
        await self.sync_event(event)
        return event
    
    async def get_entity(self, entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get the current state of an entity"""
        key = f"entity:{entity_type}:{entity_id}"
        data = await self.redis_client.get(key)
        
        if data:
            return json.loads(data)
        return None
    
    async def get_entity_history(self, entity_type: str, entity_id: str) -> List[SyncEvent]:
        """Get the history of changes for an entity"""
        key = f"history:{entity_type}:{entity_id}"
        events_data = await self.redis_client.lrange(key, 0, -1)
        
        events = []
        for event_data in events_data:
            event_dict = json.loads(event_data)
            event = SyncEvent(**event_dict)
            events.append(event)
        
        return sorted(events, key=lambda x: x.timestamp)
    
    def register_event_handler(self, entity_type: str, handler: Callable):
        """
        Register Event Handler
        
        
        Args:
            entity_type: Description of entity_type
            handler: Description of handler
    
        Example:
            TBD: Add usage example
        """
        if entity_type not in self.event_handlers:
            self.event_handlers[entity_type] = []
        
        self.event_handlers[entity_type].append(handler)
        logger.info(f"Registered event handler for {entity_type}")
    
    async def add_websocket_client(self, websocket: WebSocketServerProtocol):
        """Add a WebSocket client for real-time updates"""
        self.websocket_clients.append(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.websocket_clients)}")
    
    async def remove_websocket_client(self, websocket: WebSocketServerProtocol):
        """Remove a WebSocket client"""
        if websocket in self.websocket_clients:
            self.websocket_clients.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total clients: {len(self.websocket_clients)}")
    
    async def _process_sync_queue(self):
        """Process events from the sync queue"""
        while self.is_running:
            try:
                event = await asyncio.wait_for(self.sync_queue.get(), timeout=1.0)
                
                # Check for conflicts
                conflicts = await self._check_conflicts(event)
                if conflicts:
                    await self._handle_conflicts(event, conflicts)
                else:
                    # Apply event to database
                    await self._apply_event_to_database(event)
                    event.status = SyncStatus.COMPLETED
                
                # Store updated event
                await self._store_event(event)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing sync queue: {e}")
    
    async def _monitor_conflicts(self):
        """Monitor for conflicts and resolve them"""
        while self.is_running:
            try:
                # Check for events with conflict status
                conflict_events = await self._get_conflict_events()
                
                for event in conflict_events:
                    await self._resolve_conflict(event)
                
                await asyncio.sleep(1)  # Check every second
                
            except Exception as e:
                logger.error(f"Error monitoring conflicts: {e}")
    
    async def _cleanup_old_events(self):
        """Clean up old events to prevent memory issues"""
        while self.is_running:
            try:
                # Remove events older than 24 hours
                cutoff_time = time.time() - (24 * 60 * 60)
                
                # Clean up Redis keys
                pattern = "event:*"
                keys = await self.redis_client.keys(pattern)
                
                for key in keys:
                    event_data = await self.redis_client.get(key)
                    if event_data:
                        event_dict = json.loads(event_data)
                        if event_dict.get('timestamp', 0) < cutoff_time:
                            await self.redis_client.delete(key)
                
                await asyncio.sleep(3600)  # Clean up every hour
                
            except Exception as e:
                logger.error(f"Error cleaning up old events: {e}")
    
    async def _store_event(self, event: SyncEvent):
        """Store an event in Redis"""
        key = f"event:{event.id}"
        event_data = json.dumps(asdict(event), default=str)
        await self.redis_client.set(key, event_data, ex=86400)  # Expire in 24 hours
        
        # Add to entity history
        history_key = f"history:{event.entity_type}:{event.entity_id}"
        await self.redis_client.lpush(history_key, event_data)
        await self.redis_client.ltrim(history_key, 0, 999)  # Keep last 1000 events
    
    async def _broadcast_event(self, event: SyncEvent):
        """Broadcast event to all WebSocket clients"""
        if not self.websocket_clients:
            return
        
        message = json.dumps(asdict(event), default=str)
        
        # Send to all connected clients
        disconnected_clients = []
        for client in self.websocket_clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected_clients.append(client)
        
        # Remove disconnected clients
        for client in disconnected_clients:
            await self.remove_websocket_client(client)
    
    async def _process_event_handlers(self, event: SyncEvent):
        """Process registered event handlers"""
        handlers = self.event_handlers.get(event.entity_type, [])
        
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(f"Error in event handler: {e}")
    
    async def _check_conflicts(self, event: SyncEvent) -> List[SyncEvent]:
        """Check for conflicts with existing events"""
        conflicts = []
        
        # Get recent events for the same entity
        history_key = f"history:{event.entity_type}:{event.entity_id}"
        recent_events_data = await self.redis_client.lrange(history_key, 0, 9)  # Last 10 events
        
        for event_data in recent_events_data:
            existing_event_dict = json.loads(event_data)
            existing_event = SyncEvent(**existing_event_dict)
            
            # Check if there's a conflict
            if (existing_event.version >= event.version and 
                existing_event.timestamp > event.timestamp - 60):  # Within last minute
                conflicts.append(existing_event)
        
        return conflicts
    
    async def _handle_conflicts(self, event: SyncEvent, conflicts: List[SyncEvent]):
        """Handle conflicts between events"""
        event.status = SyncStatus.CONFLICT
        event.conflicts = [conflict.id for conflict in conflicts]
        
        # Try to resolve conflicts automatically
        for conflict in conflicts:
            resolved_event = self.conflict_resolver.resolve_conflict(
                event, conflict, strategy="last_write_wins"
            )
            
            if resolved_event.status != SyncStatus.CONFLICT:
                await self._apply_event_to_database(resolved_event)
                resolved_event.status = SyncStatus.COMPLETED
                await self._store_event(resolved_event)
    
    async def _resolve_conflict(self, event: SyncEvent):
        """Resolve a conflict for an event"""
        if not event.conflicts:
            return
        
        # Get conflicting events
        conflict_events = []
        for conflict_id in event.conflicts:
            conflict_data = await self.redis_client.get(f"event:{conflict_id}")
            if conflict_data:
                conflict_dict = json.loads(conflict_data)
                conflict_events.append(SyncEvent(**conflict_dict))
        
        # Resolve conflicts
        for conflict in conflict_events:
            resolved_event = self.conflict_resolver.resolve_conflict(
                event, conflict, strategy="last_write_wins"
            )
            
            if resolved_event.status != SyncStatus.CONFLICT:
                await self._apply_event_to_database(resolved_event)
                resolved_event.status = SyncStatus.COMPLETED
                await self._store_event(resolved_event)
    
    async def _apply_event_to_database(self, event: SyncEvent):
        """Apply an event to the database"""
        if not self.db_session:
            return
        
        try:
            if event.event_type == SyncEventType.CREATE:
                await self._create_entity_in_db(event)
            elif event.event_type == SyncEventType.UPDATE:
                await self._update_entity_in_db(event)
            elif event.event_type == SyncEventType.DELETE:
                await self._delete_entity_in_db(event)
            
            # Update entity cache
            await self._update_entity_cache(event)
            
        except Exception as e:
            logger.error(f"Error applying event to database: {e}")
            raise
    
    async def _create_entity_in_db(self, event: SyncEvent):
        """Create entity in database"""
        # Implementation depends on your database schema
        pass
    
    async def _update_entity_in_db(self, event: SyncEvent):
        """Update entity in database"""
        # Implementation depends on your database schema
        pass
    
    async def _delete_entity_in_db(self, event: SyncEvent):
        """Delete entity from database"""
        # Implementation depends on your database schema
        pass
    
    async def _update_entity_cache(self, event: SyncEvent):
        """Update entity in cache"""
        if event.event_type != SyncEventType.DELETE:
            key = f"entity:{event.entity_type}:{event.entity_id}"
            await self.redis_client.set(key, json.dumps(event.data), ex=3600)
        else:
            key = f"entity:{event.entity_type}:{event.entity_id}"
            await self.redis_client.delete(key)
    
    async def _get_entity_version(self, entity_type: str, entity_id: str) -> int:
        """Get the current version of an entity"""
        key = f"version:{entity_type}:{entity_id}"
        version = await self.redis_client.get(key)
        return int(version) if version else 0
    
    async def _get_conflict_events(self) -> List[SyncEvent]:
        """Get events with conflict status"""
        # This would query Redis for events with conflict status
        return []


# WebSocket handler for real-time updates
async def websocket_handler(websocket: WebSocketServerProtocol, path: str, 
                          sync_engine: RealTimeSyncEngine):
    """Handle WebSocket connections for real-time updates"""
    await sync_engine.add_websocket_client(websocket)
    
    try:
        async for message in websocket:
            # Handle incoming messages from clients
            data = json.loads(message)
            
            if data.get("type") == "subscribe":
                entity_types = data.get("entity_types", [])
                # Implementation for subscription management
                
            elif data.get("type") == "sync_request":
                # Client is requesting synchronization
                entity_type = data.get("entity_type")
                entity_id = data.get("entity_id")
                
                if entity_type and entity_id:
                    entity_data = await sync_engine.get_entity(entity_type, entity_id)
                    response = {
                        "type": "sync_response",
                        "entity_type": entity_type,
                        "entity_id": entity_id,
                        "data": entity_data
                    }
                    await websocket.send(json.dumps(response))
    
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        await sync_engine.remove_websocket_client(websocket)


    
    # Register event handlers
    def handle_user_update(event: SyncEvent):
        """
        Handle User Update
        
        
        Args:
            event: Description of event
    
        Example:
            TBD: Add usage example
        """
        print(f"User {event.entity_id} updated: {event.data}")
    
    sync_engine.register_event_handler("user", handle_user_update)
    
    
    # Start WebSocket server
    start_server = websockets.serve(
        lambda ws, path: websocket_handler(ws, path, sync_engine),
        "localhost", 8765
    )
    
    await start_server
    print("Real-time sync engine running on ws://localhost:8765")
    
    # Keep running
    try:
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        await sync_engine.stop()


if __name__ == "__main__":
    asyncio.run(main())

