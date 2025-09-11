#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
👥 Frenly AI Session Manager
Manages user sessions, context, and conversation state
"""

import asyncio
import logging
import time
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import redis
from backend.config import get_config

logger = logging.getLogger(__name__)

class SessionStatus(Enum):
    """Session status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    TERMINATED = "terminated"

class MessageType(Enum):
    """Message type enumeration"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    ERROR = "error"

@dataclass
class Message:
    """Message definition"""
    id: str
    type: MessageType
    content: str
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SessionContext:
    """Session context definition"""
    user_id: Optional[str] = None
    agent_type: Optional[str] = None
    conversation_history: List[Message] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)
    last_activity: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class Session:
    """Session definition"""
    id: str
    status: SessionStatus
    created_at: str
    last_accessed: str
    context: SessionContext
    message_count: int = 0
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

class SessionManager:
    """Manages user sessions and conversation state"""
    
    def __init__(self):
        """
          Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        self.config = get_config()
        self.redis_client = redis.Redis.from_url(self.config.redis_url)
        self.sessions: Dict[str, Session] = {}
        self.running = False
        
        # Session configuration
        self.session_timeout = self.config.session_timeout
        self.max_messages_per_session = 1000
        self.max_session_duration = 24 * 3600  # 24 hours
        
        logger.info("✅ Session Manager initialized")
    
    async def start(self):
        """Start the session manager"""
        self.running = True
        logger.info("🚀 Starting Session Manager...")
        
        # Start background tasks
        asyncio.create_task(self._cleanup_expired_sessions())
        asyncio.create_task(self._sync_sessions_to_redis())
        
        logger.info("✅ Session Manager started")
    
    async def stop(self):
        """Stop the session manager"""
        self.running = False
        logger.info("🛑 Stopping Session Manager...")
        
        # Save all sessions to Redis
        await self._save_all_sessions()
        
        logger.info("✅ Session Manager stopped")
    
    async def create_session(self, user_id: Optional[str] = None, 
                           agent_type: Optional[str] = None,
                           metadata: Optional[Dict[str, Any]] = None) -> str:
        """Create a new session"""
        try:
            session_id = str(uuid.uuid4())
            current_time = datetime.now().isoformat()
            
            # Create session context
            context = SessionContext(
                user_id=user_id,
                agent_type=agent_type,
                last_activity=current_time
            )
            
            # Create session
            session = Session(
                id=session_id,
                status=SessionStatus.ACTIVE,
                created_at=current_time,
                last_accessed=current_time,
                context=context,
                metadata=metadata or {}
            )
            
            # Store session
            self.sessions[session_id] = session
            
            # Save to Redis
            await self._save_session_to_redis(session)
            
            logger.info(f"✅ Session created: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"❌ Error creating session: {e}")
            raise
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        try:
            # Try local cache first
            if session_id in self.sessions:
                session = self.sessions[session_id]
                
                # Check if session is expired
                if self._is_session_expired(session):
                    await self._expire_session(session_id)
                    return None
                
                # Update last accessed
                session.last_accessed = datetime.now().isoformat()
                session.context.last_activity = session.last_accessed
                
                return session
            
            # Try Redis
            session_data = await self._load_session_from_redis(session_id)
            if session_data:
                session = self._deserialize_session(session_data)
                
                # Check if session is expired
                if self._is_session_expired(session):
                    await self._expire_session(session_id)
                    return None
                
                # Store in local cache
                self.sessions[session_id] = session
                
                return session
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error getting session {session_id}: {e}")
            return None
    
    async def add_message(self, session_id: str, message_type: MessageType, 
                         content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add message to session"""
        try:
            session = await self.get_session(session_id)
            if not session:
                return False
            
            # Create message
            message = Message(
                id=str(uuid.uuid4()),
                type=message_type,
                content=content,
                timestamp=datetime.now().isoformat(),
                metadata=metadata or {}
            )
            
            # Add to conversation history
            session.context.conversation_history.append(message)
            session.message_count += 1
            
            # Limit conversation history
            if len(session.context.conversation_history) > self.max_messages_per_session:
                # Keep only recent messages
                session.context.conversation_history = session.context.conversation_history[-self.max_messages_per_session:]
            
            # Update session
            session.last_accessed = datetime.now().isoformat()
            session.context.last_activity = session.last_accessed
            
            # Save to Redis
            await self._save_session_to_redis(session)
            
            logger.debug(f"Message added to session {session_id}: {message_type.value}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding message to session {session_id}: {e}")
            return False
    
    async def get_conversation_history(self, session_id: str, limit: Optional[int] = None) -> List[Message]:
        """Get conversation history for session"""
        try:
            session = await self.get_session(session_id)
            if not session:
                return []
            
            history = session.context.conversation_history
            if limit:
                history = history[-limit:]
            
            return history
            
        except Exception as e:
            logger.error(f"❌ Error getting conversation history for session {session_id}: {e}")
            return []
    
    async def update_session_context(self, session_id: str, 
                                   variables: Optional[Dict[str, Any]] = None,
                                   preferences: Optional[Dict[str, Any]] = None,
                                   agent_type: Optional[str] = None) -> bool:
        """Update session context"""
        try:
            session = await self.get_session(session_id)
            if not session:
                return False
            
            # Update context
            if variables:
                session.context.variables.update(variables)
            
            if preferences:
                session.context.preferences.update(preferences)
            
            if agent_type:
                session.context.agent_type = agent_type
            
            # Update last accessed
            session.last_accessed = datetime.now().isoformat()
            session.context.last_activity = session.last_accessed
            
            # Save to Redis
            await self._save_session_to_redis(session)
            
            logger.debug(f"Session context updated: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating session context {session_id}: {e}")
            return False
    
    async def get_session_variable(self, session_id: str, key: str) -> Optional[Any]:
        """Get session variable"""
        try:
            session = await self.get_session(session_id)
            if not session:
                return None
            
            return session.context.variables.get(key)
            
        except Exception as e:
            logger.error(f"❌ Error getting session variable {key} from session {session_id}: {e}")
            return None
    
    async def set_session_variable(self, session_id: str, key: str, value: Any) -> bool:
        """Set session variable"""
        try:
            session = await self.get_session(session_id)
            if not session:
                return False
            
            session.context.variables[key] = value
            session.last_accessed = datetime.now().isoformat()
            session.context.last_activity = session.last_accessed
            
            # Save to Redis
            await self._save_session_to_redis(session)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting session variable {key} in session {session_id}: {e}")
            return False
    
    async def record_request(self, session_id: str, success: bool, response_time: float) -> bool:
        """Record request statistics"""
        try:
            session = await self.get_session(session_id)
            if not session:
                return False
            
            session.total_requests += 1
            if success:
                session.successful_requests += 1
            else:
                session.failed_requests += 1
            
            # Update average response time
            session.avg_response_time = (
                (session.avg_response_time * (session.total_requests - 1) + response_time) /
                session.total_requests
            )
            
            session.last_accessed = datetime.now().isoformat()
            session.context.last_activity = session.last_accessed
            
            # Save to Redis
            await self._save_session_to_redis(session)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error recording request for session {session_id}: {e}")
            return False
    
    async def terminate_session(self, session_id: str) -> bool:
        """Terminate session"""
        try:
            session = await self.get_session(session_id)
            if not session:
                return False
            
            session.status = SessionStatus.TERMINATED
            session.last_accessed = datetime.now().isoformat()
            
            # Save to Redis
            await self._save_session_to_redis(session)
            
            # Remove from local cache
            if session_id in self.sessions:
                del self.sessions[session_id]
            
            logger.info(f"Session terminated: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error terminating session {session_id}: {e}")
            return False
    
    async def get_active_sessions(self) -> List[Session]:
        """Get all active sessions"""
        try:
            active_sessions = []
            
            for session in self.sessions.values():
                if session.status == SessionStatus.ACTIVE and not self._is_session_expired(session):
                    active_sessions.append(session)
            
            return active_sessions
            
        except Exception as e:
            logger.error(f"❌ Error getting active sessions: {e}")
            return []
    
    async def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        try:
            total_sessions = len(self.sessions)
            active_sessions = len(await self.get_active_sessions())
            
            total_messages = sum(session.message_count for session in self.sessions.values())
            total_requests = sum(session.total_requests for session in self.sessions.values())
            successful_requests = sum(session.successful_requests for session in self.sessions.values())
            
            success_rate = 0.0
            if total_requests > 0:
                success_rate = successful_requests / total_requests
            
            return {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "total_messages": total_messages,
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "success_rate": success_rate,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting session stats: {e}")
            return {}
    
    def _is_session_expired(self, session: Session) -> bool:
        """Check if session is expired"""
        last_accessed = datetime.fromisoformat(session.last_accessed)
        return datetime.now() - last_accessed > timedelta(seconds=self.session_timeout)
    
    async def _expire_session(self, session_id: str):
        """Expire session"""
        try:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                session.status = SessionStatus.EXPIRED
                session.last_accessed = datetime.now().isoformat()
                
                # Save to Redis
                await self._save_session_to_redis(session)
                
                # Remove from local cache
                del self.sessions[session_id]
                
                logger.info(f"Session expired: {session_id}")
                
        except Exception as e:
            logger.error(f"❌ Error expiring session {session_id}: {e}")
    
    async def _save_session_to_redis(self, session: Session):
        """Save session to Redis"""
        try:
            if not self.redis_client:
                return
            
            session_data = self._serialize_session(session)
            redis_key = f"frenly_session:{session.id}"
            
            self.redis_client.setex(
                redis_key,
                self.session_timeout + 3600,  # Keep in Redis longer than session timeout
                json.dumps(session_data, default=str)
            )
            
        except Exception as e:
            logger.error(f"❌ Error saving session to Redis: {e}")
    
    async def _load_session_from_redis(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session from Redis"""
        try:
            if not self.redis_client:
                return None
            
            redis_key = f"frenly_session:{session_id}"
            session_data = self.redis_client.get(redis_key)
            
            if session_data:
                return json.loads(session_data)
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error loading session from Redis: {e}")
            return None
    
    def _serialize_session(self, session: Session) -> Dict[str, Any]:
        """Serialize session to dictionary"""
        return {
            "id": session.id,
            "status": session.status.value,
            "created_at": session.created_at,
            "last_accessed": session.last_accessed,
            "context": {
                "user_id": session.context.user_id,
                "agent_type": session.context.agent_type,
                "conversation_history": [
                    {
                        "id": msg.id,
                        "type": msg.type.value,
                        "content": msg.content,
                        "timestamp": msg.timestamp,
                        "metadata": msg.metadata
                    }
                    for msg in session.context.conversation_history
                ],
                "variables": session.context.variables,
                "preferences": session.context.preferences,
                "last_activity": session.context.last_activity
            },
            "message_count": session.message_count,
            "total_requests": session.total_requests,
            "successful_requests": session.successful_requests,
            "failed_requests": session.failed_requests,
            "avg_response_time": session.avg_response_time,
            "metadata": session.metadata
        }
    
    def _deserialize_session(self, session_data: Dict[str, Any]) -> Session:
        """Deserialize session from dictionary"""
        context_data = session_data["context"]
        
        # Deserialize conversation history
        conversation_history = [
            Message(
                id=msg["id"],
                type=MessageType(msg["type"]),
                content=msg["content"],
                timestamp=msg["timestamp"],
                metadata=msg["metadata"]
            )
            for msg in context_data["conversation_history"]
        ]
        
        # Create context
        context = SessionContext(
            user_id=context_data["user_id"],
            agent_type=context_data["agent_type"],
            conversation_history=conversation_history,
            variables=context_data["variables"],
            preferences=context_data["preferences"],
            last_activity=context_data["last_activity"]
        )
        
        # Create session
        return Session(
            id=session_data["id"],
            status=SessionStatus(session_data["status"]),
            created_at=session_data["created_at"],
            last_accessed=session_data["last_accessed"],
            context=context,
            message_count=session_data["message_count"],
            total_requests=session_data["total_requests"],
            successful_requests=session_data["successful_requests"],
            failed_requests=session_data["failed_requests"],
            avg_response_time=session_data["avg_response_time"],
            metadata=session_data["metadata"]
        )
    
    async def _cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        while self.running:
            try:
                current_time = datetime.now()
                expired_sessions = []
                
                for session_id, session in self.sessions.items():
                    if self._is_session_expired(session):
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    await self._expire_session(session_id)
                
                if expired_sessions:
                    logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"❌ Session cleanup error: {e}")
                await asyncio.sleep(60)
    
    async def _sync_sessions_to_redis(self):
        """Sync sessions to Redis"""
        while self.running:
            try:
                for session in self.sessions.values():
                    await self._save_session_to_redis(session)
                
                await asyncio.sleep(30)  # Sync every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Session sync error: {e}")
                await asyncio.sleep(60)
    
    async def _save_all_sessions(self):
        """Save all sessions to Redis"""
        try:
            for session in self.sessions.values():
                await self._save_session_to_redis(session)
            
            logger.info(f"Saved {len(self.sessions)} sessions to Redis")
            
        except Exception as e:
            logger.error(f"❌ Error saving all sessions: {e}")

# Global session manager instance
session_manager = SessionManager()
