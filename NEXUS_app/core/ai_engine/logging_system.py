#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
📝 Frenly AI Logging System
Comprehensive logging and audit trail for AI service
"""

import asyncio
import logging
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import redis
from pathlib import Path
from backend.config import get_config

logger = logging.getLogger(__name__)

class LogLevel(Enum):
    """Log level enumeration"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class LogCategory(Enum):
    """Log category enumeration"""
    SYSTEM = "system"
    REQUEST = "request"
    RESPONSE = "response"
    ERROR = "error"
    SECURITY = "security"
    PERFORMANCE = "performance"
    AUDIT = "audit"
    MODEL = "model"
    AGENT = "agent"
    CACHE = "cache"
    SESSION = "session"
    WEBSOCKET = "websocket"

@dataclass
class LogEntry:
    """Log entry definition"""
    id: str
    timestamp: str
    level: LogLevel
    category: LogCategory
    message: str
    component: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    trace_id: Optional[str] = None

@dataclass
class AuditLog:
    """Audit log definition"""
    id: str
    timestamp: str
    user_id: Optional[str]
    action: str
    resource: str
    result: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class LoggingSystem:
    """Comprehensive logging and audit system"""
    
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
        
        # Logging configuration
        self.log_retention_days = 30
        self.max_log_entries = 10000
        self.batch_size = 100
        self.flush_interval = 60  # seconds
        
        # Log storage
        self.log_buffer: List[LogEntry] = []
        self.audit_buffer: List[AuditLog] = []
        
        # Setup loggers
        self._setup_loggers()
        
        logger.info("✅ Logging System initialized")
    
    def _setup_loggers(self):
        """Setup application loggers"""
        # Create logs directory
        logs_dir = Path(self.config.logs_path)
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure root logger
        logging.basicConfig(
            level=getattr(logging, self.config.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(logs_dir / 'frenly_ai.log')
            ]
        )
        
        # Create component loggers
        self.loggers = {
            'system': logging.getLogger('frenly.system'),
            'request': logging.getLogger('frenly.request'),
            'response': logging.getLogger('frenly.response'),
            'error': logging.getLogger('frenly.error'),
            'security': logging.getLogger('frenly.security'),
            'performance': logging.getLogger('frenly.performance'),
            'audit': logging.getLogger('frenly.audit'),
            'model': logging.getLogger('frenly.model'),
            'agent': logging.getLogger('frenly.agent'),
            'cache': logging.getLogger('frenly.cache'),
            'session': logging.getLogger('frenly.session'),
            'websocket': logging.getLogger('frenly.websocket')
        }
        
        # Setup file handlers for each component
        for component, logger_instance in self.loggers.items():
            handler = logging.FileHandler(logs_dir / f'{component}.log')
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            ))
            logger_instance.addHandler(handler)
    
    async def start(self):
        """Start the logging system"""
        self.running = True
        logger.info("🚀 Starting Logging System...")
        
        # Start background tasks
        asyncio.create_task(self._flush_logs())
        asyncio.create_task(self._cleanup_old_logs())
        
        logger.info("✅ Logging System started")
    
    async def stop(self):
        """Stop the logging system"""
        self.running = False
        logger.info("🛑 Stopping Logging System...")
        
        # Flush remaining logs
        await self._flush_logs()
        await self._flush_audit_logs()
        
        logger.info("✅ Logging System stopped")
    
    async def log(self, level: LogLevel, category: LogCategory, message: str,
                 component: str, user_id: Optional[str] = None,
                 session_id: Optional[str] = None, request_id: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None,
                 trace_id: Optional[str] = None):
        """Log a message"""
        try:
            # Create log entry
            log_entry = LogEntry(
                id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                level=level,
                category=category,
                message=message,
                component=component,
                user_id=user_id,
                session_id=session_id,
                request_id=request_id,
                metadata=metadata or {},
                trace_id=trace_id
            )
            
            # Add to buffer
            self.log_buffer.append(log_entry)
            
            # Log to appropriate logger
            logger_instance = self.loggers.get(component, self.loggers['system'])
            log_method = getattr(logger_instance, level.value.upper())
            log_method(f"{message} | {json.dumps(metadata or {})}")
            
            # Flush if buffer is full
            if len(self.log_buffer) >= self.batch_size:
                await self._flush_logs()
            
        except Exception as e:
            logger.error(f"❌ Error logging message: {e}")
    
    async def log_request(self, request_data: Dict[str, Any], user_id: Optional[str] = None,
                         session_id: Optional[str] = None, request_id: Optional[str] = None):
        """Log API request"""
        await self.log(
            level=LogLevel.INFO,
            category=LogCategory.REQUEST,
            message=f"API request received",
            component="api",
            user_id=user_id,
            session_id=session_id,
            request_id=request_id,
            metadata={
                "method": request_data.get("method", "POST"),
                "endpoint": request_data.get("endpoint", "/api/v1/process"),
                "agent_type": request_data.get("agent_type"),
                "message_length": len(str(request_data.get("message", ""))),
                "priority": request_data.get("priority", 1)
            }
        )
    
    async def log_response(self, response_data: Dict[str, Any], user_id: Optional[str] = None,
                          session_id: Optional[str] = None, request_id: Optional[str] = None):
        """Log API response"""
        await self.log(
            level=LogLevel.INFO,
            category=LogCategory.RESPONSE,
            message=f"API response generated",
            component="api",
            user_id=user_id,
            session_id=session_id,
            request_id=request_id,
            metadata={
                "response_length": len(str(response_data.get("response", ""))),
                "confidence": response_data.get("confidence", 0.0),
                "processing_time": response_data.get("processing_time", 0.0),
                "agent_used": response_data.get("agent_used"),
                "success": response_data.get("success", True)
            }
        )
    
    async def log_error(self, error: Exception, component: str, user_id: Optional[str] = None,
                       session_id: Optional[str] = None, request_id: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None):
        """Log error"""
        await self.log(
            level=LogLevel.ERROR,
            category=LogCategory.ERROR,
            message=f"Error in {component}: {str(error)}",
            component=component,
            user_id=user_id,
            session_id=session_id,
            request_id=request_id,
            metadata={
                "error_type": type(error).__name__,
                "error_message": str(error),
                **(metadata or {})
            }
        )
    
    async def log_security_event(self, event_type: str, description: str,
                                user_id: Optional[str] = None, ip_address: Optional[str] = None,
                                metadata: Optional[Dict[str, Any]] = None):
        """Log security event"""
        await self.log(
            level=LogLevel.WARNING,
            category=LogCategory.SECURITY,
            message=f"Security event: {event_type} - {description}",
            component="security",
            user_id=user_id,
            metadata={
                "event_type": event_type,
                "description": description,
                "ip_address": ip_address,
                **(metadata or {})
            }
        )
    
    async def log_performance(self, operation: str, duration: float, component: str,
                             user_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        """Log performance metrics"""
        level = LogLevel.INFO
        if duration > 5.0:
            level = LogLevel.WARNING
        elif duration > 10.0:
            level = LogLevel.ERROR
        
        await self.log(
            level=level,
            category=LogCategory.PERFORMANCE,
            message=f"Performance: {operation} took {duration:.3f}s",
            component=component,
            user_id=user_id,
            metadata={
                "operation": operation,
                "duration": duration,
                **(metadata or {})
            }
        )
    
    async def log_audit(self, user_id: Optional[str], action: str, resource: str,
                       result: str, ip_address: Optional[str] = None,
                       user_agent: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None):
        """Log audit event"""
        try:
            # Create audit log entry
            audit_entry = AuditLog(
                id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                user_id=user_id,
                action=action,
                resource=resource,
                result=result,
                ip_address=ip_address,
                user_agent=user_agent,
                metadata=metadata or {}
            )
            
            # Add to buffer
            self.audit_buffer.append(audit_entry)
            
            # Log to audit logger
            self.loggers['audit'].info(
                f"AUDIT: {action} on {resource} by {user_id or 'anonymous'} - {result}"
            )
            
            # Flush if buffer is full
            if len(self.audit_buffer) >= self.batch_size:
                await self._flush_audit_logs()
            
        except Exception as e:
            logger.error(f"❌ Error logging audit event: {e}")
    
    async def get_logs(self, category: Optional[LogCategory] = None,
                      level: Optional[LogLevel] = None,
                      component: Optional[str] = None,
                      start_time: Optional[datetime] = None,
                      end_time: Optional[datetime] = None,
                      limit: int = 1000) -> List[LogEntry]:
        """Get logs with filtering"""
        try:
            # This would typically query from a database or log storage
            # For now, return logs from Redis cache
            if self.redis_client:
                cached_logs = self.redis_client.get("frenly_logs")
                if cached_logs:
                    logs_data = json.loads(cached_logs)
                    logs = [LogEntry(**log_data) for log_data in logs_data]
                    
                    # Apply filters
                    if category:
                        logs = [log for log in logs if log.category == category]
                    if level:
                        logs = [log for log in logs if log.level == level]
                    if component:
                        logs = [log for log in logs if log.component == component]
                    if start_time:
                        logs = [log for log in logs if datetime.fromisoformat(log.timestamp) >= start_time]
                    if end_time:
                        logs = [log for log in logs if datetime.fromisoformat(log.timestamp) <= end_time]
                    
                    return logs[-limit:] if limit else logs
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Error getting logs: {e}")
            return []
    
    async def get_audit_logs(self, user_id: Optional[str] = None,
                           action: Optional[str] = None,
                           start_time: Optional[datetime] = None,
                           end_time: Optional[datetime] = None,
                           limit: int = 1000) -> List[AuditLog]:
        """Get audit logs with filtering"""
        try:
            # This would typically query from a database
            # For now, return logs from Redis cache
            if self.redis_client:
                cached_audit = self.redis_client.get("frenly_audit_logs")
                if cached_audit:
                    audit_data = json.loads(cached_audit)
                    audit_logs = [AuditLog(**log_data) for log_data in audit_data]
                    
                    # Apply filters
                    if user_id:
                        audit_logs = [log for log in audit_logs if log.user_id == user_id]
                    if action:
                        audit_logs = [log for log in audit_logs if log.action == action]
                    if start_time:
                        audit_logs = [log for log in audit_logs if datetime.fromisoformat(log.timestamp) >= start_time]
                    if end_time:
                        audit_logs = [log for log in audit_logs if datetime.fromisoformat(log.timestamp) <= end_time]
                    
                    return audit_logs[-limit:] if limit else audit_logs
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Error getting audit logs: {e}")
            return []
    
    async def _flush_logs(self):
        """Flush log buffer to storage"""
        try:
            if not self.log_buffer:
                return
            
            # Store in Redis
            if self.redis_client:
                logs_data = [
                    {
                        "id": log.id,
                        "timestamp": log.timestamp,
                        "level": log.level.value,
                        "category": log.category.value,
                        "message": log.message,
                        "component": log.component,
                        "user_id": log.user_id,
                        "session_id": log.session_id,
                        "request_id": log.request_id,
                        "metadata": log.metadata,
                        "trace_id": log.trace_id
                    }
                    for log in self.log_buffer
                ]
                
                self.redis_client.setex(
                    "frenly_logs",
                    3600,  # 1 hour TTL
                    json.dumps(logs_data, default=str)
                )
            
            # Clear buffer
            self.log_buffer.clear()
            
        except Exception as e:
            logger.error(f"❌ Error flushing logs: {e}")
    
    async def _flush_audit_logs(self):
        """Flush audit log buffer to storage"""
        try:
            if not self.audit_buffer:
                return
            
            # Store in Redis
            if self.redis_client:
                audit_data = [
                    {
                        "id": log.id,
                        "timestamp": log.timestamp,
                        "user_id": log.user_id,
                        "action": log.action,
                        "resource": log.resource,
                        "result": log.result,
                        "ip_address": log.ip_address,
                        "user_agent": log.user_agent,
                        "metadata": log.metadata
                    }
                    for log in self.audit_buffer
                ]
                
                self.redis_client.setex(
                    "frenly_audit_logs",
                    3600,  # 1 hour TTL
                    json.dumps(audit_data, default=str)
                )
            
            # Clear buffer
            self.audit_buffer.clear()
            
        except Exception as e:
            logger.error(f"❌ Error flushing audit logs: {e}")
    
    async def _cleanup_old_logs(self):
        """Clean up old log files"""
        while self.running:
            try:
                logs_dir = Path(self.config.logs_path)
                cutoff_date = datetime.now() - timedelta(days=self.log_retention_days)
                
                # Clean up old log files
                for log_file in logs_dir.glob("*.log"):
                    if log_file.stat().st_mtime < cutoff_date.timestamp():
                        log_file.unlink()
                        logger.info(f"Cleaned up old log file: {log_file}")
                
                await asyncio.sleep(86400)  # Check daily
                
            except Exception as e:
                logger.error(f"❌ Error cleaning up old logs: {e}")
                await asyncio.sleep(3600)
    
    async def get_logging_stats(self) -> Dict[str, Any]:
        """Get logging statistics"""
        try:
            total_logs = len(self.log_buffer)
            total_audit = len(self.audit_buffer)
            
            # Count logs by level
            level_counts = {}
            for log in self.log_buffer:
                level = log.level.value
                level_counts[level] = level_counts.get(level, 0) + 1
            
            # Count logs by category
            category_counts = {}
            for log in self.log_buffer:
                category = log.category.value
                category_counts[category] = category_counts.get(category, 0) + 1
            
            return {
                "total_logs": total_logs,
                "total_audit_logs": total_audit,
                "level_counts": level_counts,
                "category_counts": category_counts,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting logging stats: {e}")
            return {}

# Global logging system instance
logging_system = LoggingSystem()
