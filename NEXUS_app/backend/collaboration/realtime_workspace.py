#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
Real-Time Collaborative Workspace System
Google Docs-like collaborative environment with real-time editing, version control, and conflict resolution
"""

import os
import sys
import json
import asyncio
import websockets
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid
import hashlib
import threading
from collections import defaultdict, deque
import redis
import sqlite3
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OperationType(Enum):
    """
    OperationType Class
    
    Operation Type
    
    Attributes:
        TBD: Add attribute descriptions
    
    Methods:
        TBD: Add method descriptions
    
    Example:
        TBD: Add usage example
    """
    INSERT = "insert"
    DELETE = "delete"
    RETAIN = "retain"
    FORMAT = "format"

class UserPresence(Enum):
    """
    UserPresence Class
    
    User Presence
    
    Attributes:
        TBD: Add attribute descriptions
    
    Methods:
        TBD: Add method descriptions
    
    Example:
        TBD: Add usage example
    """
    ONLINE = "online"
    AWAY = "away"
    OFFLINE = "offline"
    EDITING = "editing"

class ConflictResolutionStrategy(Enum):
    """
    ConflictResolutionStrategy Class
    
    Conflict Resolution Strategy
    
    Attributes:
        TBD: Add attribute descriptions
    
    Methods:
        TBD: Add method descriptions
    
    Example:
        TBD: Add usage example
    """
    LAST_WRITE_WINS = "last_write_wins"
    OPERATIONAL_TRANSFORM = "operational_transform"
    MANUAL_RESOLUTION = "manual_resolution"

@dataclass
class Operation:
    """Represents a document operation"""
    id: str
    type: OperationType
    position: int
    content: str = ""
    length: int = 0
    attributes: Dict[str, Any] = field(default_factory=dict)
    user_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    version: int = 0

@dataclass
class Document:
    """Represents a collaborative document"""
    id: str
    title: str
    content: str
    version: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    permissions: Dict[str, List[str]] = field(default_factory=dict)  # user_id -> [permissions]
    collaborators: Set[str] = field(default_factory=set)
    is_locked: bool = False
    locked_by: Optional[str] = None

@dataclass
class User:
    """Represents a user in the workspace"""
    id: str
    username: str
    email: str
    presence: UserPresence = UserPresence.OFFLINE
    current_document: Optional[str] = None
    cursor_position: int = 0
    selection_start: int = 0
    selection_end: int = 0
    last_seen: datetime = field(default_factory=datetime.now)
    color: str = "#000000"

@dataclass
class Cursor:
    """Represents a user's cursor position"""
    user_id: str
    position: int
    selection_start: int = 0
    selection_end: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

class OperationalTransform:
    """Operational Transform implementation for conflict resolution"""
    
    def __init__(self):
        """
          Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        self.operations: List[Operation] = []
    
    def transform_operation(self, op1: Operation, op2: Operation) -> Tuple[Operation, Operation]:
        """Transform two operations to resolve conflicts"""
        if op1.type == OperationType.RETAIN and op2.type == OperationType.RETAIN:
            return op1, op2
        
        elif op1.type == OperationType.INSERT and op2.type == OperationType.RETAIN:
            if op1.position <= op2.position:
                return op1, Operation(
                    id=op2.id,
                    type=op2.type,
                    position=op2.position + len(op1.content),
                    content=op2.content,
                    length=op2.length,
                    attributes=op2.attributes,
                    user_id=op2.user_id,
                    timestamp=op2.timestamp,
                    version=op2.version
                )
            else:
                return op1, op2
        
        elif op1.type == OperationType.RETAIN and op2.type == OperationType.INSERT:
            if op2.position <= op1.position:
                return Operation(
                    id=op1.id,
                    type=op1.type,
                    position=op1.position + len(op2.content),
                    content=op1.content,
                    length=op1.length,
                    attributes=op1.attributes,
                    user_id=op1.user_id,
                    timestamp=op1.timestamp,
                    version=op1.version
                ), op2
            else:
                return op1, op2
        
        elif op1.type == OperationType.DELETE and op2.type == OperationType.RETAIN:
            if op1.position < op2.position:
                return op1, Operation(
                    id=op2.id,
                    type=op2.type,
                    position=max(op1.position, op2.position - op1.length),
                    content=op2.content,
                    length=op2.length,
                    attributes=op2.attributes,
                    user_id=op2.user_id,
                    timestamp=op2.timestamp,
                    version=op2.version
                )
            else:
                return op1, op2
        
        elif op1.type == OperationType.RETAIN and op2.type == OperationType.DELETE:
            if op2.position < op1.position:
                return Operation(
                    id=op1.id,
                    type=op1.type,
                    position=max(op2.position, op1.position - op2.length),
                    content=op1.content,
                    length=op1.length,
                    attributes=op1.attributes,
                    user_id=op1.user_id,
                    timestamp=op1.timestamp,
                    version=op1.version
                ), op2
            else:
                return op1, op2
        
        else:
            # Complex cases - simplified for this implementation
            return op1, op2
    
    def apply_operation(self, document: Document, operation: Operation) -> Document:
        """Apply an operation to a document"""
        content = document.content
        
        if operation.type == OperationType.INSERT:
            content = content[:operation.position] + operation.content + content[operation.position:]
        elif operation.type == OperationType.DELETE:
            start = operation.position
            end = min(operation.position + operation.length, len(content))
            content = content[:start] + content[end:]
        elif operation.type == OperationType.RETAIN:
            # Retain operation - no content change
            pass
        
        return Document(
            id=document.id,
            title=document.title,
            content=content,
            version=document.version + 1,
            created_at=document.created_at,
            updated_at=datetime.now(),
            created_by=document.created_by,
            permissions=document.permissions,
            collaborators=document.collaborators,
            is_locked=document.is_locked,
            locked_by=document.locked_by
        )

class VersionControl:
    """Version control system for documents"""
    
    def __init__(self, db_path: str = "collaboration.db"):
        """
          Init  
        
        
        Args:
            db_path: Description of db_path
    
        Example:
            TBD: Add usage example
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for version control"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS document_versions (
                id TEXT PRIMARY KEY,
                document_id TEXT,
                version INTEGER,
                content TEXT,
                operations TEXT,
                created_at TIMESTAMP,
                created_by TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS operations (
                id TEXT PRIMARY KEY,
                document_id TEXT,
                version INTEGER,
                operation_type TEXT,
                position INTEGER,
                content TEXT,
                length INTEGER,
                attributes TEXT,
                user_id TEXT,
                timestamp TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_version(self, document: Document, operations: List[Operation]):
        """Save a new version of the document"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        version_id = str(uuid.uuid4())
        operations_json = json.dumps([{
            'id': op.id,
            'type': op.type.value,
            'position': op.position,
            'content': op.content,
            'length': op.length,
            'attributes': op.attributes,
            'user_id': op.user_id,
            'timestamp': op.timestamp.isoformat(),
            'version': op.version
        } for op in operations])
        
        cursor.execute('''
            INSERT INTO document_versions 
            (id, document_id, version, content, operations, created_at, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            version_id,
            document.id,
            document.version,
            document.content,
            operations_json,
            document.updated_at.isoformat(),
            document.created_by
        ))
        
        # Save individual operations
        for op in operations:
            cursor.execute('''
                INSERT INTO operations 
                (id, document_id, version, operation_type, position, content, length, attributes, user_id, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                op.id,
                document.id,
                document.version,
                op.type.value,
                op.position,
                op.content,
                op.length,
                json.dumps(op.attributes),
                op.user_id,
                op.timestamp.isoformat()
            ))
        
        conn.commit()
        conn.close()
    
    def get_version(self, document_id: str, version: int) -> Optional[Tuple[Document, List[Operation]]]:
        """
        Retrieve version
        
        
        Args:
            document_id: Description of document_id
            version: Description of version
    
        Returns:
            Unknown: Description of return value
    
        Example:
            TBD: Add usage example
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT content, operations, created_at, created_by
            FROM document_versions
            WHERE document_id = ? AND version = ?
        ''', (document_id, version))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return None
        
        content, operations_json, created_at, created_by = result
        
        operations = []
        for op_data in json.loads(operations_json):
            operations.append(Operation(
                id=op_data['id'],
                type=OperationType(op_data['type']),
                position=op_data['position'],
                content=op_data['content'],
                length=op_data['length'],
                attributes=op_data['attributes'],
                user_id=op_data['user_id'],
                timestamp=datetime.fromisoformat(op_data['timestamp']),
                version=op_data['version']
            ))
        
        document = Document(
            id=document_id,
            title="",  # Would need to be stored separately
            content=content,
            version=version,
            created_at=datetime.fromisoformat(created_at),
            updated_at=datetime.fromisoformat(created_at),
            created_by=created_by
        )
        
        conn.close()
        return document, operations
    
    def get_version_history(self, document_id: str) -> List[Dict[str, Any]]:
        """Get version history for a document"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT version, created_at, created_by
            FROM document_versions
            WHERE document_id = ?
            ORDER BY version DESC
        ''', (document_id,))
        
        versions = []
        for row in cursor.fetchall():
            versions.append({
                'version': row[0],
                'created_at': row[1],
                'created_by': row[2]
            })
        
        conn.close()
        return versions

class CollaborativeWorkspace:
    """Real-time collaborative workspace system"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """Initialize the collaborative workspace"""
        self.redis_client = redis.from_url(redis_url)
        self.documents: Dict[str, Document] = {}
        self.users: Dict[str, User] = {}
        self.connected_clients: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.document_cursors: Dict[str, List[Cursor]] = defaultdict(list)
        self.operational_transform = OperationalTransform()
        self.version_control = VersionControl()
        self.running = False
        
        # WebSocket server
        self.server = None
        self.host = "localhost"
        self.port = 8765
        
        logger.info("Collaborative Workspace initialized")
    
    async def start_server(self):
        """Start the WebSocket server"""
        self.running = True
        
        async def handle_client(websocket, path):
            """Handle new client connections"""
            client_id = str(uuid.uuid4())
            self.connected_clients[client_id] = websocket
            
            try:
                logger.info(f"Client connected: {client_id}")
                
                async for message in websocket:
                    await self.handle_message(client_id, message)
            
            except websockets.exceptions.ConnectionClosed:
                logger.info(f"Client disconnected: {client_id}")
            finally:
                if client_id in self.connected_clients:
                    del self.connected_clients[client_id]
        
        self.server = await websockets.serve(handle_client, self.host, self.port)
        logger.info(f"WebSocket server started on {self.host}:{self.port}")
    
    async def stop_server(self):
        """Stop the WebSocket server"""
        self.running = False
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        logger.info("WebSocket server stopped")
    
    async def handle_message(self, client_id: str, message: str):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(message)
            message_type = data.get('type')
            
            if message_type == 'join_document':
                await self.handle_join_document(client_id, data)
            elif message_type == 'leave_document':
                await self.handle_leave_document(client_id, data)
            elif message_type == 'operation':
                await self.handle_operation(client_id, data)
            elif message_type == 'cursor_update':
                await self.handle_cursor_update(client_id, data)
            elif message_type == 'user_presence':
                await self.handle_user_presence(client_id, data)
            elif message_type == 'lock_document':
                await self.handle_lock_document(client_id, data)
            elif message_type == 'unlock_document':
                await self.handle_unlock_document(client_id, data)
            else:
                logger.warning(f"Unknown message type: {message_type}")
        
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message from {client_id}")
        except Exception as e:
            logger.error(f"Error handling message from {client_id}: {e}")
    
    async def handle_join_document(self, client_id: str, data: Dict[str, Any]):
        """Handle user joining a document"""
        document_id = data.get('document_id')
        user_id = data.get('user_id')
        
        if not document_id or not user_id:
            await self.send_error(client_id, "Missing document_id or user_id")
            return
        
        # Create or get document
        if document_id not in self.documents:
            self.documents[document_id] = Document(
                id=document_id,
                title=data.get('title', 'Untitled Document'),
                content=data.get('content', ''),
                created_by=user_id
            )
        
        document = self.documents[document_id]
        document.collaborators.add(user_id)
        
        # Create or update user
        if user_id not in self.users:
            self.users[user_id] = User(
                id=user_id,
                username=data.get('username', f'User {user_id}'),
                email=data.get('email', ''),
                color=data.get('color', f'#{hash(user_id) % 0xFFFFFF:06x}')
            )
        
        user = self.users[user_id]
        user.presence = UserPresence.ONLINE
        user.current_document = document_id
        
        # Send document state to client
        await self.send_message(client_id, {
            'type': 'document_state',
            'document_id': document_id,
            'content': document.content,
            'version': document.version,
            'collaborators': list(document.collaborators),
            'cursors': [
                {
                    'user_id': c.user_id,
                    'position': c.position,
                    'selection_start': c.selection_start,
                    'selection_end': c.selection_end,
                    'color': self.users[c.user_id].color
                }
                for c in self.document_cursors[document_id]
            ]
        })
        
        # Notify other clients
        await self.broadcast_to_document(document_id, {
            'type': 'user_joined',
            'user_id': user_id,
            'username': user.username,
            'color': user.color
        }, exclude_client=client_id)
    
    async def handle_leave_document(self, client_id: str, data: Dict[str, Any]):
        """Handle user leaving a document"""
        document_id = data.get('document_id')
        user_id = data.get('user_id')
        
        if document_id and user_id:
            if document_id in self.documents:
                self.documents[document_id].collaborators.discard(user_id)
            
            if user_id in self.users:
                self.users[user_id].presence = UserPresence.OFFLINE
                self.users[user_id].current_document = None
            
            # Remove user's cursor
            self.document_cursors[document_id] = [
                c for c in self.document_cursors[document_id] if c.user_id != user_id
            ]
            
            # Notify other clients
            await self.broadcast_to_document(document_id, {
                'type': 'user_left',
                'user_id': user_id
            }, exclude_client=client_id)
    
    async def handle_operation(self, client_id: str, data: Dict[str, Any]):
        """Handle document operation"""
        document_id = data.get('document_id')
        user_id = data.get('user_id')
        operation_data = data.get('operation')
        
        if not document_id or not user_id or not operation_data:
            await self.send_error(client_id, "Missing required fields")
            return
        
        if document_id not in self.documents:
            await self.send_error(client_id, "Document not found")
            return
        
        # Create operation
        operation = Operation(
            id=str(uuid.uuid4()),
            type=OperationType(operation_data['type']),
            position=operation_data['position'],
            content=operation_data.get('content', ''),
            length=operation_data.get('length', 0),
            attributes=operation_data.get('attributes', {}),
            user_id=user_id,
            timestamp=datetime.now(),
            version=self.documents[document_id].version + 1
        )
        
        # Apply operation to document
        document = self.documents[document_id]
        new_document = self.operational_transform.apply_operation(document, operation)
        self.documents[document_id] = new_document
        
        # Save version
        self.version_control.save_version(new_document, [operation])
        
        # Broadcast operation to other clients
        await self.broadcast_to_document(document_id, {
            'type': 'operation_applied',
            'operation': {
                'id': operation.id,
                'type': operation.type.value,
                'position': operation.position,
                'content': operation.content,
                'length': operation.length,
                'attributes': operation.attributes,
                'user_id': operation.user_id,
                'timestamp': operation.timestamp.isoformat(),
                'version': operation.version
            },
            'document_version': new_document.version
        }, exclude_client=client_id)
    
    async def handle_cursor_update(self, client_id: str, data: Dict[str, Any]):
        """Handle cursor position update"""
        document_id = data.get('document_id')
        user_id = data.get('user_id')
        position = data.get('position', 0)
        selection_start = data.get('selection_start', 0)
        selection_end = data.get('selection_end', 0)
        
        if not document_id or not user_id:
            return
        
        # Update cursor
        cursor = Cursor(
            user_id=user_id,
            position=position,
            selection_start=selection_start,
            selection_end=selection_end,
            timestamp=datetime.now()
        )
        
        # Remove old cursor for this user
        self.document_cursors[document_id] = [
            c for c in self.document_cursors[document_id] if c.user_id != user_id
        ]
        
        # Add new cursor
        self.document_cursors[document_id].append(cursor)
        
        # Broadcast cursor update
        await self.broadcast_to_document(document_id, {
            'type': 'cursor_updated',
            'user_id': user_id,
            'position': position,
            'selection_start': selection_start,
            'selection_end': selection_end,
            'color': self.users[user_id].color if user_id in self.users else '#000000'
        }, exclude_client=client_id)
    
    async def handle_user_presence(self, client_id: str, data: Dict[str, Any]):
        """Handle user presence update"""
        user_id = data.get('user_id')
        presence = data.get('presence')
        
        if user_id and presence and user_id in self.users:
            self.users[user_id].presence = UserPresence(presence)
            self.users[user_id].last_seen = datetime.now()
    
    async def handle_lock_document(self, client_id: str, data: Dict[str, Any]):
        """Handle document lock request"""
        document_id = data.get('document_id')
        user_id = data.get('user_id')
        
        if not document_id or not user_id:
            await self.send_error(client_id, "Missing document_id or user_id")
            return
        
        if document_id not in self.documents:
            await self.send_error(client_id, "Document not found")
            return
        
        document = self.documents[document_id]
        
        if document.is_locked and document.locked_by != user_id:
            await self.send_error(client_id, "Document is locked by another user")
            return
        
        document.is_locked = True
        document.locked_by = user_id
        
        # Notify all clients
        await self.broadcast_to_document(document_id, {
            'type': 'document_locked',
            'locked_by': user_id,
            'username': self.users[user_id].username if user_id in self.users else user_id
        })
    
    async def handle_unlock_document(self, client_id: str, data: Dict[str, Any]):
        """Handle document unlock request"""
        document_id = data.get('document_id')
        user_id = data.get('user_id')
        
        if not document_id or not user_id:
            await self.send_error(client_id, "Missing document_id or user_id")
            return
        
        if document_id not in self.documents:
            await self.send_error(client_id, "Document not found")
            return
        
        document = self.documents[document_id]
        
        if document.locked_by != user_id:
            await self.send_error(client_id, "Only the user who locked the document can unlock it")
            return
        
        document.is_locked = False
        document.locked_by = None
        
        # Notify all clients
        await self.broadcast_to_document(document_id, {
            'type': 'document_unlocked',
            'unlocked_by': user_id
        })
    
    async def send_message(self, client_id: str, message: Dict[str, Any]):
        if client_id in self.connected_clients:
            try:
                await self.connected_clients[client_id].send(json.dumps(message))
            except websockets.exceptions.ConnectionClosed:
                del self.connected_clients[client_id]
    
    async def send_error(self, client_id: str, error_message: str):
        """Send error message to client"""
        await self.send_message(client_id, {
            'type': 'error',
            'message': error_message
        })
    
    async def broadcast_to_document(self, document_id: str, message: Dict[str, Any], exclude_client: Optional[str] = None):
        """Broadcast message to all clients in a document"""
        for client_id, websocket in self.connected_clients.items():
            if client_id == exclude_client:
                continue
            
            # Check if client is in this document
            user_id = None
            for uid, user in self.users.items():
                if user.current_document == document_id:
                    # This is a simplified check - in real implementation, you'd track client-document mapping
                    user_id = uid
                    break
            
            if user_id and user_id in self.documents[document_id].collaborators:
                try:
                    await websocket.send(json.dumps(message))
                except websockets.exceptions.ConnectionClosed:
                    del self.connected_clients[client_id]
    
    def get_document_status(self, document_id: str) -> Dict[str, Any]:
        """Get status of a document"""
        if document_id not in self.documents:
            return {"error": "Document not found"}
        
        document = self.documents[document_id]
        cursors = self.document_cursors[document_id]
        
        return {
            "id": document.id,
            "title": document.title,
            "version": document.version,
            "collaborators": list(document.collaborators),
            "is_locked": document.is_locked,
            "locked_by": document.locked_by,
            "cursors": [
                {
                    "user_id": c.user_id,
                    "position": c.position,
                    "selection_start": c.selection_start,
                    "selection_end": c.selection_end,
                    "username": self.users[c.user_id].username if c.user_id in self.users else c.user_id,
                    "color": self.users[c.user_id].color if c.user_id in self.users else '#000000'
                }
                for c in cursors
            ],
            "created_at": document.created_at.isoformat(),
            "updated_at": document.updated_at.isoformat()
        }
    
    def get_workspace_status(self) -> Dict[str, Any]:
        """Get overall workspace status"""
        return {
            "total_documents": len(self.documents),
            "total_users": len(self.users),
            "connected_clients": len(self.connected_clients),
            "documents": {
                doc_id: self.get_document_status(doc_id)
                for doc_id in self.documents
            },
            "users": {
                user_id: {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "presence": user.presence.value,
                    "current_document": user.current_document,
                    "last_seen": user.last_seen.isoformat(),
                    "color": user.color
                }
                for user_id, user in self.users.items()
            }
        }

    
    # Initialize workspace
    workspace = CollaborativeWorkspace()
    
    # Start server
    await workspace.start_server()
    
    print(f"✅ Collaborative Workspace System ready!")
    print(f"   WebSocket Server: ws://{workspace.host}:{workspace.port}")
    print(f"   Total Documents: {len(workspace.documents)}")
    print(f"   Total Users: {len(workspace.users)}")
    print(f"   Connected Clients: {len(workspace.connected_clients)}")
    
    # Keep server running
    try:
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        await workspace.stop_server()

if __name__ == "__main__":
    asyncio.run(main())
