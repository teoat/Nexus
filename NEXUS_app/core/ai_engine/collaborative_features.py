#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🤝 Frenly AI Collaborative Features System
Advanced collaboration capabilities for Frenly AI
"""

import asyncio
import logging
import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import redis
from backend.config import get_config

logger = logging.getLogger(__name__)

class CollaborationType(Enum):
    """Collaboration type enumeration"""
    REAL_TIME_EDITING = "real_time_editing"
    SHARED_WORKSPACE = "shared_workspace"
    TEAM_CHAT = "team_chat"
    VIDEO_CONFERENCE = "video_conference"
    SCREEN_SHARING = "screen_sharing"
    DOCUMENT_REVIEW = "document_review"
    TASK_ASSIGNMENT = "task_assignment"
    KNOWLEDGE_SHARING = "knowledge_sharing"
    VERSION_CONTROL = "version_control"
    APPROVAL_WORKFLOW = "approval_workflow"

class UserRole(Enum):
    """User role enumeration"""
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"
    GUEST = "guest"
    REVIEWER = "reviewer"
    APPROVER = "approver"

class CollaborationStatus(Enum):
    """Collaboration status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class NotificationType(Enum):
    """Notification type enumeration"""
    MENTION = "mention"
    ASSIGNMENT = "assignment"
    COMMENT = "comment"
    APPROVAL = "approval"
    UPDATE = "update"
    INVITATION = "invitation"
    DEADLINE = "deadline"

@dataclass
class CollaborationSession:
    """Collaboration session definition"""
    id: str
    name: str
    type: CollaborationType
    owner_id: str
    participants: List[str]
    status: CollaborationStatus
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UserPermission:
    """User permission definition"""
    user_id: str
    role: UserRole
    permissions: List[str]
    granted_by: str
    granted_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class CollaborationMessage:
    """Collaboration message definition"""
    id: str
    session_id: str
    sender_id: str
    content: str
    message_type: str
    reply_to: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CollaborationDocument:
    """Collaboration document definition"""
    id: str
    session_id: str
    name: str
    content: str
    version: int
    last_modified_by: str
    last_modified_at: str = field(default_factory=lambda: datetime.now().isoformat())
    collaborators: List[str] = field(default_factory=list)
    changes: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class CollaborationTask:
    """Collaboration task definition"""
    id: str
    session_id: str
    title: str
    description: str
    assignee_id: str
    assigner_id: str
    status: str
    priority: str
    due_date: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class CollaborationNotification:
    """Collaboration notification definition"""
    id: str
    user_id: str
    type: NotificationType
    title: str
    message: str
    session_id: Optional[str] = None
    task_id: Optional[str] = None
    read: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

class CollaborativeFeaturesSystem:
    """Collaborative Features System for Frenly AI"""
    
    def __init__(self):
        """
          Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        self.config = get_config()
        self.redis_client = redis.Redis.from_url(self.config.redis_url)
        self.running = False
        
        # Collaboration storage
        self.sessions: Dict[str, CollaborationSession] = {}
        self.permissions: Dict[str, UserPermission] = {}
        self.messages: Dict[str, CollaborationMessage] = {}
        self.documents: Dict[str, CollaborationDocument] = {}
        self.tasks: Dict[str, CollaborationTask] = {}
        self.notifications: Dict[str, CollaborationNotification] = {}
        
        # Real-time collaboration
        self.active_users: Dict[str, Dict[str, Any]] = {}
        self.cursor_positions: Dict[str, Dict[str, Any]] = {}
        self.document_locks: Dict[str, str] = {}
        
        # Configuration
        self.session_timeout = 3600  # 1 hour
        self.message_retention_days = 30
        self.document_retention_days = 90
        self.max_participants = 100
        
        logger.info("✅ Collaborative Features System initialized")
    
    async def start(self):
        """Start the collaborative features system"""
        self.running = True
        logger.info("🚀 Starting Collaborative Features System...")
        
        # Load existing data
        await self._load_collaboration_data()
        
        # Start background tasks
        asyncio.create_task(self._cleanup_old_data())
        asyncio.create_task(self._process_notifications())
        asyncio.create_task(self._monitor_active_users())
        
        logger.info("✅ Collaborative Features System started")
    
    async def stop(self):
        """Stop the collaborative features system"""
        self.running = False
        logger.info("🛑 Stopping Collaborative Features System...")
        
        # Save collaboration data
        await self._save_collaboration_data()
        
        logger.info("✅ Collaborative Features System stopped")
    
    async def create_session(
        self,
        name: str,
        type: CollaborationType,
        owner_id: str,
        participants: Optional[List[str]] = None
    ) -> str:
        """Create a new collaboration session"""
        try:
            session_id = f"session_{int(time.time())}_{hashlib.md5(name.encode()).hexdigest()[:8]}"
            
            session = CollaborationSession(
                id=session_id,
                name=name,
                type=type,
                owner_id=owner_id,
                participants=participants or [owner_id],
                status=CollaborationStatus.ACTIVE
            )
            
            self.sessions[session_id] = session
            
            # Add owner permissions
            await self._grant_permission(session_id, owner_id, UserRole.OWNER, owner_id)
            
            logger.info(f"Collaboration session created: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"❌ Error creating collaboration session: {e}")
            raise
    
    async def join_session(self, session_id: str, user_id: str) -> bool:
        """Join a collaboration session"""
        try:
            if session_id not in self.sessions:
                raise ValueError("Session not found")
            
            session = self.sessions[session_id]
            
            if session.status != CollaborationStatus.ACTIVE:
                raise ValueError("Session is not active")
            
            if len(session.participants) >= self.max_participants:
                raise ValueError("Session is full")
            
            if user_id not in session.participants:
                session.participants.append(user_id)
                session.updated_at = datetime.now().isoformat()
                
                # Grant default permissions
                await self._grant_permission(session_id, user_id, UserRole.VIEWER, session.owner_id)
                
                # Notify other participants
                await self._send_notification(
                    user_id=None,  # Broadcast to all participants
                    type=NotificationType.UPDATE,
                    title="User Joined",
                    message=f"User {user_id} joined the session",
                    session_id=session_id
                )
            
            logger.info(f"User {user_id} joined session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error joining session: {e}")
            return False
    
    async def leave_session(self, session_id: str, user_id: str) -> bool:
        """Leave a collaboration session"""
        try:
            if session_id not in self.sessions:
                raise ValueError("Session not found")
            
            session = self.sessions[session_id]
            
            if user_id in session.participants:
                session.participants.remove(user_id)
                session.updated_at = datetime.now().isoformat()
                
                # Remove permissions
                await self._revoke_permission(session_id, user_id)
                
                # Notify other participants
                await self._send_notification(
                    user_id=None,  # Broadcast to all participants
                    type=NotificationType.UPDATE,
                    title="User Left",
                    message=f"User {user_id} left the session",
                    session_id=session_id
                )
            
            logger.info(f"User {user_id} left session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error leaving session: {e}")
            return False
    
    async def get_session(self, session_id: str) -> Optional[CollaborationSession]:
        """Get collaboration session information"""
        return self.sessions.get(session_id)
    
    async def list_sessions(self, user_id: Optional[str] = None, type: Optional[CollaborationType] = None) -> List[CollaborationSession]:
        """List collaboration sessions"""
        sessions = list(self.sessions.values())
        
        if user_id:
            sessions = [s for s in sessions if user_id in s.participants]
        
        if type:
            sessions = [s for s in sessions if s.type == type]
        
        return sessions
    
    async def send_message(
        self,
        session_id: str,
        sender_id: str,
        content: str,
        message_type: str = "text",
        reply_to: Optional[str] = None
    ) -> str:
        """Send a message in collaboration session"""
        try:
            if session_id not in self.sessions:
                raise ValueError("Session not found")
            
            session = self.sessions[session_id]
            
            if sender_id not in session.participants:
                raise ValueError("User not in session")
            
            message_id = f"message_{int(time.time())}_{hashlib.md5(content.encode()).hexdigest()[:8]}"
            
            message = CollaborationMessage(
                id=message_id,
                session_id=session_id,
                sender_id=sender_id,
                content=content,
                message_type=message_type,
                reply_to=reply_to
            )
            
            self.messages[message_id] = message
            
            # Notify participants
            await self._send_notification(
                user_id=None,  # Broadcast to all participants
                type=NotificationType.COMMENT,
                title="New Message",
                message=f"New message in {session.name}",
                session_id=session_id
            )
            
            logger.info(f"Message sent: {message_id}")
            return message_id
            
        except Exception as e:
            logger.error(f"❌ Error sending message: {e}")
            raise
    
    async def get_messages(self, session_id: str, limit: int = 50) -> List[CollaborationMessage]:
        """Get messages from collaboration session"""
        try:
            session_messages = [m for m in self.messages.values() if m.session_id == session_id]
            
            # Sort by creation time
            session_messages.sort(key=lambda m: m.created_at)
            
            return session_messages[-limit:]
            
        except Exception as e:
            logger.error(f"❌ Error getting messages: {e}")
            return []
    
    async def create_document(
        self,
        session_id: str,
        name: str,
        content: str,
        creator_id: str
    ) -> str:
        """Create a collaboration document"""
        try:
            if session_id not in self.sessions:
                raise ValueError("Session not found")
            
            document_id = f"doc_{int(time.time())}_{hashlib.md5(name.encode()).hexdigest()[:8]}"
            
            document = CollaborationDocument(
                id=document_id,
                session_id=session_id,
                name=name,
                content=content,
                version=1,
                last_modified_by=creator_id,
                collaborators=[creator_id]
            )
            
            self.documents[document_id] = document
            
            logger.info(f"Document created: {document_id}")
            return document_id
            
        except Exception as e:
            logger.error(f"❌ Error creating document: {e}")
            raise
    
    async def update_document(
        self,
        document_id: str,
        content: str,
        user_id: str
    ) -> bool:
        """Update a collaboration document"""
        try:
            if document_id not in self.documents:
                raise ValueError("Document not found")
            
            document = self.documents[document_id]
            
            # Check if user has edit permissions
            if not await self._has_permission(document.session_id, user_id, "edit"):
                raise ValueError("User does not have edit permissions")
            
            # Check for document lock
            if document_id in self.document_locks and self.document_locks[document_id] != user_id:
                raise ValueError("Document is locked by another user")
            
            # Store change
            change = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "content_length": len(content),
                "changes": len(content) - len(document.content)
            }
            document.changes.append(change)
            
            # Update document
            document.content = content
            document.version += 1
            document.last_modified_by = user_id
            document.last_modified_at = datetime.now().isoformat()
            
            if user_id not in document.collaborators:
                document.collaborators.append(user_id)
            
            logger.info(f"Document updated: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating document: {e}")
            return False
    
    async def get_document(self, document_id: str) -> Optional[CollaborationDocument]:
        """Get collaboration document"""
        return self.documents.get(document_id)
    
    async def list_documents(self, session_id: str) -> List[CollaborationDocument]:
        """List documents in collaboration session"""
        return [d for d in self.documents.values() if d.session_id == session_id]
    
    async def create_task(
        self,
        session_id: str,
        title: str,
        description: str,
        assignee_id: str,
        assigner_id: str,
        priority: str = "medium",
        due_date: Optional[str] = None
    ) -> str:
        """Create a collaboration task"""
        try:
            if session_id not in self.sessions:
                raise ValueError("Session not found")
            
            task_id = f"task_{int(time.time())}_{hashlib.md5(title.encode()).hexdigest()[:8]}"
            
            task = CollaborationTask(
                id=task_id,
                session_id=session_id,
                title=title,
                description=description,
                assignee_id=assignee_id,
                assigner_id=assigner_id,
                status="pending",
                priority=priority,
                due_date=due_date
            )
            
            self.tasks[task_id] = task
            
            # Notify assignee
            await self._send_notification(
                user_id=assignee_id,
                type=NotificationType.ASSIGNMENT,
                title="Task Assigned",
                message=f"You have been assigned a new task: {title}",
                session_id=session_id,
                task_id=task_id
            )
            
            logger.info(f"Task created: {task_id}")
            return task_id
            
        except Exception as e:
            logger.error(f"❌ Error creating task: {e}")
            raise
    
    async def update_task(self, task_id: str, user_id: str, **updates) -> bool:
        """Update a collaboration task"""
        try:
            if task_id not in self.tasks:
                raise ValueError("Task not found")
            
            task = self.tasks[task_id]
            
            # Check permissions
            if task.assignee_id != user_id and not await self._has_permission(task.session_id, user_id, "admin"):
                raise ValueError("User does not have permission to update this task")
            
            # Update fields
            for key, value in updates.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            
            task.updated_at = datetime.now().isoformat()
            
            # Notify relevant users
            await self._send_notification(
                user_id=task.assignee_id,
                type=NotificationType.UPDATE,
                title="Task Updated",
                message=f"Task '{task.title}' has been updated",
                session_id=task.session_id,
                task_id=task_id
            )
            
            logger.info(f"Task updated: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating task: {e}")
            return False
    
    async def get_task(self, task_id: str) -> Optional[CollaborationTask]:
        """Get collaboration task"""
        return self.tasks.get(task_id)
    
    async def list_tasks(self, session_id: str, assignee_id: Optional[str] = None) -> List[CollaborationTask]:
        """List tasks in collaboration session"""
        tasks = [t for t in self.tasks.values() if t.session_id == session_id]
        
        if assignee_id:
            tasks = [t for t in tasks if t.assignee_id == assignee_id]
        
        return tasks
    
    async def grant_permission(
        self,
        session_id: str,
        user_id: str,
        role: UserRole,
        granted_by: str
    ) -> bool:
        """Grant permission to user in session"""
        try:
            if session_id not in self.sessions:
                raise ValueError("Session not found")
            
            # Check if granter has admin permissions
            if not await self._has_permission(session_id, granted_by, "admin"):
                raise ValueError("User does not have permission to grant permissions")
            
            await self._grant_permission(session_id, user_id, role, granted_by)
            
            logger.info(f"Permission granted: {user_id} -> {role.value} in {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error granting permission: {e}")
            return False
    
    async def revoke_permission(self, session_id: str, user_id: str, revoked_by: str) -> bool:
        """Revoke permission from user in session"""
        try:
            if session_id not in self.sessions:
                raise ValueError("Session not found")
            
            # Check if revoker has admin permissions
            if not await self._has_permission(session_id, revoked_by, "admin"):
                raise ValueError("User does not have permission to revoke permissions")
            
            await self._revoke_permission(session_id, user_id)
            
            logger.info(f"Permission revoked: {user_id} in {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error revoking permission: {e}")
            return False
    
    async def get_notifications(self, user_id: str, unread_only: bool = False) -> List[CollaborationNotification]:
        """Get user notifications"""
        try:
            notifications = [n for n in self.notifications.values() if n.user_id == user_id]
            
            if unread_only:
                notifications = [n for n in notifications if not n.read]
            
            # Sort by creation time (newest first)
            notifications.sort(key=lambda n: n.created_at, reverse=True)
            
            return notifications
            
        except Exception as e:
            logger.error(f"❌ Error getting notifications: {e}")
            return []
    
    async def mark_notification_read(self, notification_id: str, user_id: str) -> bool:
        """Mark notification as read"""
        try:
            if notification_id not in self.notifications:
                return False
            
            notification = self.notifications[notification_id]
            
            if notification.user_id != user_id:
                return False
            
            notification.read = True
            
            logger.info(f"Notification marked as read: {notification_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error marking notification as read: {e}")
            return False
    
    async def get_collaboration_analytics(self) -> Dict[str, Any]:
        """Get collaboration system analytics"""
        try:
            total_sessions = len(self.sessions)
            total_messages = len(self.messages)
            total_documents = len(self.documents)
            total_tasks = len(self.tasks)
            total_notifications = len(self.notifications)
            
            # Active sessions
            active_sessions = [s for s in self.sessions.values() if s.status == CollaborationStatus.ACTIVE]
            
            # Session type distribution
            type_distribution = {}
            for session in self.sessions.values():
                session_type = session.type.value
                type_distribution[session_type] = type_distribution.get(session_type, 0) + 1
            
            # Task status distribution
            task_status_distribution = {}
            for task in self.tasks.values():
                status = task.status
                task_status_distribution[status] = task_status_distribution.get(status, 0) + 1
            
            # Recent activity
            recent_cutoff = datetime.now() - timedelta(hours=24)
            recent_messages = [
                m for m in self.messages.values()
                if datetime.fromisoformat(m.created_at) > recent_cutoff
            ]
            
            recent_tasks = [
                t for t in self.tasks.values()
                if datetime.fromisoformat(t.created_at) > recent_cutoff
            ]
            
            # Active users
            active_user_count = len(self.active_users)
            
            return {
                "sessions": {
                    "total": total_sessions,
                    "active": len(active_sessions),
                    "type_distribution": type_distribution
                },
                "messages": {
                    "total": total_messages,
                    "recent": len(recent_messages)
                },
                "documents": {
                    "total": total_documents
                },
                "tasks": {
                    "total": total_tasks,
                    "recent": len(recent_tasks),
                    "status_distribution": task_status_distribution
                },
                "notifications": {
                    "total": total_notifications,
                    "unread": len([n for n in self.notifications.values() if not n.read])
                },
                "users": {
                    "active": active_user_count
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting collaboration analytics: {e}")
            return {"error": str(e)}
    
    async def _grant_permission(self, session_id: str, user_id: str, role: UserRole, granted_by: str):
        """Grant permission to user"""
        try:
            permission_id = f"perm_{session_id}_{user_id}"
            
            # Define permissions based on role
            permissions = []
            if role == UserRole.OWNER:
                permissions = ["admin", "edit", "view", "invite", "remove"]
            elif role == UserRole.ADMIN:
                permissions = ["edit", "view", "invite", "remove"]
            elif role == UserRole.EDITOR:
                permissions = ["edit", "view"]
            elif role == UserRole.REVIEWER:
                permissions = ["view", "comment"]
            elif role == UserRole.APPROVER:
                permissions = ["view", "approve"]
            else:  # VIEWER, GUEST
                permissions = ["view"]
            
            permission = UserPermission(
                user_id=user_id,
                role=role,
                permissions=permissions,
                granted_by=granted_by
            )
            
            self.permissions[permission_id] = permission
            
        except Exception as e:
            logger.error(f"❌ Error granting permission: {e}")
    
    async def _revoke_permission(self, session_id: str, user_id: str):
        """Revoke permission from user"""
        try:
            permission_id = f"perm_{session_id}_{user_id}"
            
            if permission_id in self.permissions:
                del self.permissions[permission_id]
            
        except Exception as e:
            logger.error(f"❌ Error revoking permission: {e}")
    
    async def _has_permission(self, session_id: str, user_id: str, permission: str) -> bool:
        try:
            permission_id = f"perm_{session_id}_{user_id}"
            
            if permission_id not in self.permissions:
                return False
            
            user_permission = self.permissions[permission_id]
            return permission in user_permission.permissions
            
        except Exception as e:
            logger.error(f"❌ Error checking permission: {e}")
            return False
    
    async def _send_notification(
        self,
        user_id: Optional[str],
        type: NotificationType,
        title: str,
        message: str,
        session_id: Optional[str] = None,
        task_id: Optional[str] = None
    ):
        """Send notification to user(s)"""
        try:
            notification_id = f"notif_{int(time.time())}_{hashlib.md5(message.encode()).hexdigest()[:8]}"
            
            if user_id:
                notification = CollaborationNotification(
                    id=notification_id,
                    user_id=user_id,
                    type=type,
                    title=title,
                    message=message,
                    session_id=session_id,
                    task_id=task_id
                )
                self.notifications[notification_id] = notification
            else:
                # Broadcast to all participants in session
                if session_id and session_id in self.sessions:
                    session = self.sessions[session_id]
                    for participant_id in session.participants:
                        participant_notification = CollaborationNotification(
                            id=f"{notification_id}_{participant_id}",
                            user_id=participant_id,
                            type=type,
                            title=title,
                            message=message,
                            session_id=session_id,
                            task_id=task_id
                        )
                        self.notifications[f"{notification_id}_{participant_id}"] = participant_notification
            
        except Exception as e:
            logger.error(f"❌ Error sending notification: {e}")
    
    async def _process_notifications(self):
        """Process notifications"""
        while self.running:
            try:
                # Process any pending notifications
                # In practice, this would integrate with email, push notifications, etc.
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"❌ Error processing notifications: {e}")
                await asyncio.sleep(300)
    
    async def _monitor_active_users(self):
        """Monitor active users"""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Remove inactive users
                inactive_users = []
                for user_id, user_data in self.active_users.items():
                    last_seen = datetime.fromisoformat(user_data["last_seen"])
                    if (current_time - last_seen).total_seconds() > self.session_timeout:
                        inactive_users.append(user_id)
                
                for user_id in inactive_users:
                    del self.active_users[user_id]
                
                if inactive_users:
                    logger.info(f"Removed {len(inactive_users)} inactive users")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Error monitoring active users: {e}")
                await asyncio.sleep(600)
    
    async def _cleanup_old_data(self):
        """Clean up old collaboration data"""
        while self.running:
            try:
                # Clean up old messages
                message_cutoff = datetime.now() - timedelta(days=self.message_retention_days)
                
                old_messages = [
                    message_id for message_id, message in self.messages.items()
                    if datetime.fromisoformat(message.created_at) < message_cutoff
                ]
                
                for message_id in old_messages:
                    del self.messages[message_id]
                
                # Clean up old documents
                document_cutoff = datetime.now() - timedelta(days=self.document_retention_days)
                
                old_documents = [
                    doc_id for doc_id, doc in self.documents.items()
                    if datetime.fromisoformat(doc.last_modified_at) < document_cutoff
                ]
                
                for doc_id in old_documents:
                    del self.documents[doc_id]
                
                # Clean up old notifications
                notification_cutoff = datetime.now() - timedelta(days=7)
                
                old_notifications = [
                    notif_id for notif_id, notif in self.notifications.items()
                    if datetime.fromisoformat(notif.created_at) < notification_cutoff
                ]
                
                for notif_id in old_notifications:
                    del self.notifications[notif_id]
                
                if old_messages or old_documents or old_notifications:
                    logger.info(f"Cleaned up {len(old_messages)} old messages, {len(old_documents)} old documents, {len(old_notifications)} old notifications")
                
                await asyncio.sleep(86400)  # Clean up daily
                
            except Exception as e:
                logger.error(f"❌ Error cleaning up old data: {e}")
                await asyncio.sleep(3600)
    
    async def _load_collaboration_data(self):
        """Load collaboration data from storage"""
        try:
            if self.redis_client:
                # Load sessions
                sessions_data = self.redis_client.get("frenly_collaboration_sessions")
                if sessions_data:
                    sessions_json = json.loads(sessions_data)
                    for session_id, session_data in sessions_json.items():
                        session = CollaborationSession(
                            id=session_id,
                            name=session_data["name"],
                            type=CollaborationType(session_data["type"]),
                            owner_id=session_data["owner_id"],
                            participants=session_data["participants"],
                            status=CollaborationStatus(session_data["status"]),
                            created_at=session_data["created_at"],
                            updated_at=session_data["updated_at"],
                            metadata=session_data.get("metadata", {})
                        )
                        self.sessions[session_id] = session
                
                # Load permissions
                permissions_data = self.redis_client.get("frenly_collaboration_permissions")
                if permissions_data:
                    permissions_json = json.loads(permissions_data)
                    for perm_id, perm_data in permissions_json.items():
                        permission = UserPermission(
                            user_id=perm_data["user_id"],
                            role=UserRole(perm_data["role"]),
                            permissions=perm_data["permissions"],
                            granted_by=perm_data["granted_by"],
                            granted_at=perm_data["granted_at"]
                        )
                        self.permissions[perm_id] = permission
                
                # Load messages
                messages_data = self.redis_client.get("frenly_collaboration_messages")
                if messages_data:
                    messages_json = json.loads(messages_data)
                    for message_id, message_data in messages_json.items():
                        message = CollaborationMessage(
                            id=message_id,
                            session_id=message_data["session_id"],
                            sender_id=message_data["sender_id"],
                            content=message_data["content"],
                            message_type=message_data["message_type"],
                            reply_to=message_data.get("reply_to"),
                            created_at=message_data["created_at"],
                            metadata=message_data.get("metadata", {})
                        )
                        self.messages[message_id] = message
                
                # Load documents
                documents_data = self.redis_client.get("frenly_collaboration_documents")
                if documents_data:
                    documents_json = json.loads(documents_data)
                    for doc_id, doc_data in documents_json.items():
                        document = CollaborationDocument(
                            id=doc_id,
                            session_id=doc_data["session_id"],
                            name=doc_data["name"],
                            content=doc_data["content"],
                            version=doc_data["version"],
                            last_modified_by=doc_data["last_modified_by"],
                            last_modified_at=doc_data["last_modified_at"],
                            collaborators=doc_data.get("collaborators", []),
                            changes=doc_data.get("changes", [])
                        )
                        self.documents[doc_id] = document
                
                # Load tasks
                tasks_data = self.redis_client.get("frenly_collaboration_tasks")
                if tasks_data:
                    tasks_json = json.loads(tasks_data)
                    for task_id, task_data in tasks_json.items():
                        task = CollaborationTask(
                            id=task_id,
                            session_id=task_data["session_id"],
                            title=task_data["title"],
                            description=task_data["description"],
                            assignee_id=task_data["assignee_id"],
                            assigner_id=task_data["assigner_id"],
                            status=task_data["status"],
                            priority=task_data["priority"],
                            due_date=task_data.get("due_date"),
                            created_at=task_data["created_at"],
                            updated_at=task_data["updated_at"]
                        )
                        self.tasks[task_id] = task
                
                # Load notifications
                notifications_data = self.redis_client.get("frenly_collaboration_notifications")
                if notifications_data:
                    notifications_json = json.loads(notifications_data)
                    for notif_id, notif_data in notifications_json.items():
                        notification = CollaborationNotification(
                            id=notif_id,
                            user_id=notif_data["user_id"],
                            type=NotificationType(notif_data["type"]),
                            title=notif_data["title"],
                            message=notif_data["message"],
                            session_id=notif_data.get("session_id"),
                            task_id=notif_data.get("task_id"),
                            read=notif_data.get("read", False),
                            created_at=notif_data["created_at"]
                        )
                        self.notifications[notif_id] = notification
                
                logger.info(f"Loaded {len(self.sessions)} sessions, {len(self.permissions)} permissions, {len(self.messages)} messages, {len(self.documents)} documents, {len(self.tasks)} tasks, {len(self.notifications)} notifications")
            
        except Exception as e:
            logger.error(f"❌ Error loading collaboration data: {e}")
    
    async def _save_collaboration_data(self):
        """Save collaboration data to storage"""
        try:
            if self.redis_client:
                # Save sessions
                sessions_data = {
                    session_id: {
                        "name": session.name,
                        "type": session.type.value,
                        "owner_id": session.owner_id,
                        "participants": session.participants,
                        "status": session.status.value,
                        "created_at": session.created_at,
                        "updated_at": session.updated_at,
                        "metadata": session.metadata
                    }
                    for session_id, session in self.sessions.items()
                }
                self.redis_client.setex("frenly_collaboration_sessions", 86400, json.dumps(sessions_data))
                
                # Save permissions
                permissions_data = {
                    perm_id: {
                        "user_id": permission.user_id,
                        "role": permission.role.value,
                        "permissions": permission.permissions,
                        "granted_by": permission.granted_by,
                        "granted_at": permission.granted_at
                    }
                    for perm_id, permission in self.permissions.items()
                }
                self.redis_client.setex("frenly_collaboration_permissions", 86400, json.dumps(permissions_data))
                
                # Save messages
                messages_data = {
                    message_id: {
                        "session_id": message.session_id,
                        "sender_id": message.sender_id,
                        "content": message.content,
                        "message_type": message.message_type,
                        "reply_to": message.reply_to,
                        "created_at": message.created_at,
                        "metadata": message.metadata
                    }
                    for message_id, message in self.messages.items()
                }
                self.redis_client.setex("frenly_collaboration_messages", 86400, json.dumps(messages_data))
                
                # Save documents
                documents_data = {
                    doc_id: {
                        "session_id": document.session_id,
                        "name": document.name,
                        "content": document.content,
                        "version": document.version,
                        "last_modified_by": document.last_modified_by,
                        "last_modified_at": document.last_modified_at,
                        "collaborators": document.collaborators,
                        "changes": document.changes
                    }
                    for doc_id, document in self.documents.items()
                }
                self.redis_client.setex("frenly_collaboration_documents", 86400, json.dumps(documents_data))
                
                # Save tasks
                tasks_data = {
                    task_id: {
                        "session_id": task.session_id,
                        "title": task.title,
                        "description": task.description,
                        "assignee_id": task.assignee_id,
                        "assigner_id": task.assigner_id,
                        "status": task.status,
                        "priority": task.priority,
                        "due_date": task.due_date,
                        "created_at": task.created_at,
                        "updated_at": task.updated_at
                    }
                    for task_id, task in self.tasks.items()
                }
                self.redis_client.setex("frenly_collaboration_tasks", 86400, json.dumps(tasks_data))
                
                # Save notifications
                notifications_data = {
                    notif_id: {
                        "user_id": notification.user_id,
                        "type": notification.type.value,
                        "title": notification.title,
                        "message": notification.message,
                        "session_id": notification.session_id,
                        "task_id": notification.task_id,
                        "read": notification.read,
                        "created_at": notification.created_at
                    }
                    for notif_id, notification in self.notifications.items()
                }
                self.redis_client.setex("frenly_collaboration_notifications", 86400, json.dumps(notifications_data))
            
        except Exception as e:
            logger.error(f"❌ Error saving collaboration data: {e}")

# Global collaborative features system instance
collaborative_features = CollaborativeFeaturesSystem()
