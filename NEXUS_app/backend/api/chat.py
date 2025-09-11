from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/")
async def send_chat_message(message_data: Dict[str, Any]):
    """Send a chat message and get AI response"""
    try:
        message_id = str(uuid.uuid4())
        session_id = message_data.get("session_id", "default")
        user_message = message_data.get("message", "")
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Create message object
        message = {
            "id": message_id,
            "session_id": session_id,
            "user_message": user_message,
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        
        # Store message
        chat_messages.append(message)
        
        # Update session
        if session_id not in chat_sessions:
            chat_sessions[session_id] = {
                "id": session_id,
                "created_at": datetime.now().isoformat(),
                "message_count": 0,
                "last_activity": datetime.now().isoformat()
            }
        
        chat_sessions[session_id]["message_count"] += 1
        chat_sessions[session_id]["last_activity"] = datetime.now().isoformat()
        
        logger.info(f"Chat message processed: {message_id}")
        return {
            "success": True,
            "data": message,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(status_code=500, detail="Failed to process chat message")

@router.get("/sessions")
async def get_chat_sessions():
    """Get all chat sessions"""
    try:
        return {
            "success": True,
            "data": {
                "sessions": list(chat_sessions.values()),
                "total": len(chat_sessions)
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting chat sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get chat sessions")

@router.get("/sessions/{session_id}/messages")
async def get_session_messages(session_id: str):
    try:
        session_messages = [m for m in chat_messages if m["session_id"] == session_id]
        
        return {
            "success": True,
            "data": {
                "session_id": session_id,
                "messages": session_messages,
                "total": len(session_messages)
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting session messages: {e}")
        raise HTTPException(status_code=500, detail="Failed to get session messages")

@router.post("/sessions")
async def create_chat_session(session_data: Dict[str, Any] = None):
    """Create a new chat session"""
    try:
        session_id = str(uuid.uuid4())
        session = {
            "id": session_id,
            "created_at": datetime.now().isoformat(),
            "message_count": 0,
            "last_activity": datetime.now().isoformat(),
            "metadata": session_data or {}
        }
        
        chat_sessions[session_id] = session
        
        logger.info(f"Created chat session: {session_id}")
        return {
            "success": True,
            "data": session,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error creating chat session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create chat session")

@router.delete("/sessions/{session_id}")
async def delete_chat_session(session_id: str):
    """Delete a chat session and its messages"""
    try:
        if session_id not in chat_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Remove session
        del chat_sessions[session_id]
        
        # Remove messages for this session
        global chat_messages
        chat_messages = [m for m in chat_messages if m["session_id"] != session_id]
        
        logger.info(f"Deleted chat session: {session_id}")
        return {
            "success": True,
            "message": "Chat session deleted successfully",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chat session: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete chat session")

@router.get("/health")
async def chat_health_check():
    """Health check for chat service"""
    try:
        return {
            "success": True,
            "data": {
                "status": "healthy",
                "active_sessions": len(chat_sessions),
                "total_messages": len(chat_messages),
                "uptime": "running"
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error in chat health check: {e}")
        raise HTTPException(status_code=500, detail="Chat service health check failed")
