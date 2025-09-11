#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🔗 Frenly AI Integrated Service
Complete integration of all Frenly AI components
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, WebSocket, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import all Frenly AI components
from backend.config import get_config, validate_config
from agent_manager import agent_manager
from model_manager import model_manager
from cache_manager import cache_manager
from session_manager import session_manager
from performance_monitor import performance_monitor
from security_manager import security_manager
from websocket_handler import websocket_manager
from database_manager import database_manager
from health_checker import health_checker
from logging_system import logging_system

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FrenlyAIIntegratedService:
    """Integrated Frenly AI service with all components"""
    
    def __init__(self):
        """
          Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        self.config = get_config()
        self.app = None
        self.running = False
        self.startup_time = None
        
        logger.info("✅ Frenly AI Integrated Service initialized")
    
    async def startup(self):
        """Startup all components"""
        logger.info("🚀 Starting Frenly AI Integrated Service...")
        
        try:
            # Validate configuration
            if not validate_config():
                raise Exception("Configuration validation failed")
            
            # Start all components
            await asyncio.gather(
                agent_manager.start(),
                model_manager.start(),
                cache_manager.start(),
                session_manager.start(),
                performance_monitor.start(),
                security_manager.start(),
                websocket_manager.start(),
                database_manager.start(),
                health_checker.start(),
                logging_system.start()
            )
            
            # Create database tables
            await database_manager.create_tables()
            
            # Record startup time
            self.startup_time = time.time()
            
            logger.info("✅ Frenly AI Integrated Service started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start Frenly AI Integrated Service: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown all components"""
        logger.info("🛑 Shutting down Frenly AI Integrated Service...")
        
        try:
            # Stop all components
            await asyncio.gather(
                agent_manager.stop(),
                model_manager.stop(),
                cache_manager.stop(),
                session_manager.stop(),
                performance_monitor.stop(),
                security_manager.stop(),
                websocket_manager.stop(),
                database_manager.stop(),
                health_checker.stop(),
                logging_system.stop()
            )
            
            logger.info("✅ Frenly AI Integrated Service shut down successfully")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")
    
    def create_app(self) -> FastAPI:
        """Create integrated FastAPI application"""
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            await self.startup()
            yield
            # Shutdown
            await self.shutdown()
        
        app = FastAPI(
            title="Frenly AI Integrated Service",
            description="Complete AI service with all components integrated",
            version=self.config.version,
            docs_url="/docs",
            redoc_url="/redoc",
            lifespan=lifespan
        )
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Add all routes
        self._add_routes(app)
        
        return app
    
    def _add_routes(self, app: FastAPI):
        """Add all API routes"""
        
        # Health check endpoints
        @app.get("/health")
        async def health_check():
            """Overall health check"""
            try:
                health = await health_checker.check_overall_health()
                return {
                    "status": health.overall_status.value,
                    "timestamp": health.timestamp,
                    "uptime": health.uptime,
                    "version": health.version,
                    "components": [
                        {
                            "component": comp.component.value,
                            "status": comp.status.value,
                            "message": comp.message
                        }
                        for comp in health.components
                    ]
                }
            except Exception as e:
                return {
                    "status": "critical",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        @app.get("/health/detailed")
        async def detailed_health_check():
            """Detailed health check"""
            return await health_checker.check_overall_health()
        
        # AI processing endpoints
        @app.post("/api/v1/process")
        async def process_request(request_data: Dict[str, Any], background_tasks: BackgroundTasks):
            """Process AI request with full integration"""
            try:
                # Security check
                source_ip = request_data.get("source_ip", "127.0.0.1")
                auth_result, auth_message = await security_manager.authenticate_request(
                    request_data, source_ip
                )
                
                if not auth_result:
                    await logging_system.log_security_event(
                        "authentication_failed",
                        f"Request authentication failed: {auth_message}",
                        request_data.get("user_id"),
                        source_ip
                    )
                    raise HTTPException(status_code=401, detail=auth_message)
                
                # Create session if needed
                session_id = request_data.get("session_id")
                if not session_id:
                    session_id = await session_manager.create_session(
                        user_id=request_data.get("user_id"),
                        agent_type=request_data.get("agent_type", "general")
                    )
                
                # Log request
                await logging_system.log_request(request_data, request_data.get("user_id"), session_id)
                
                # Process with agent manager
                start_time = time.time()
                try:
                    response = await agent_manager.submit_request(
                        request_data.get("agent_type", "general"),
                        request_data
                    )
                    processing_time = time.time() - start_time
                    success = True
                    
                    # Record performance metrics
                    await performance_monitor.record_request(True, processing_time, request_data.get("agent_type"))
                    
                    # Log response
                    await logging_system.log_response(response, request_data.get("user_id"), session_id)
                    
                    # Save to database
                    await database_manager.save_ai_request({
                        "id": response.get("request_id", str(int(time.time() * 1000))),
                        "session_id": session_id,
                        "user_id": request_data.get("user_id"),
                        "request_data": request_data,
                        "response_data": response,
                        "agent_type": request_data.get("agent_type", "general"),
                        "processing_time": processing_time,
                        "confidence": response.get("confidence", 0.0),
                        "created_at": datetime.now().isoformat()
                    })
                    
                    # Update session
                    await session_manager.record_request(session_id, True, processing_time)
                    await session_manager.add_message(
                        session_id, 
                        "user", 
                        request_data.get("message", ""),
                        {"request_id": response.get("request_id")}
                    )
                    await session_manager.add_message(
                        session_id,
                        "assistant",
                        response.get("response", ""),
                        {"confidence": response.get("confidence")}
                    )
                    
                except Exception as e:
                    processing_time = time.time() - start_time
                    success = False
                    
                    # Record performance metrics
                    await performance_monitor.record_request(False, processing_time, request_data.get("agent_type"))
                    
                    # Log error
                    await logging_system.log_error(e, "agent_manager", request_data.get("user_id"), session_id)
                    
                    # Update session
                    await session_manager.record_request(session_id, False, processing_time)
                    
                    raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
                
                return {
                    "success": success,
                    "response": response.get("response", ""),
                    "confidence": response.get("confidence", 0.0),
                    "agent_used": response.get("agent_id", ""),
                    "processing_time": processing_time,
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat()
                }
                
            except HTTPException:
                raise
            except Exception as e:
                await logging_system.log_error(e, "api", request_data.get("user_id"))
                raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
        
        # Agent management endpoints
        @app.get("/api/v1/agents")
        async def get_agents():
            """Get all agents status"""
            return await agent_manager.get_agent_status()
        
        @app.get("/api/v1/agents/{agent_id}")
        async def get_agent(agent_id: str):
            return await agent_manager.get_agent_status(agent_id)
        
        # Model management endpoints
        @app.get("/api/v1/models")
        async def get_models():
            """Get all models status"""
            return await model_manager.get_model_status()
        
        @app.get("/api/v1/models/{model_id}")
        async def get_model(model_id: str):
            return await model_manager.get_model_status(model_id)
        
        # Session management endpoints
        @app.get("/api/v1/sessions/{session_id}")
        async def get_session(session_id: str):
            """Get session information"""
            session = await session_manager.get_session(session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            return session
        
        @app.post("/api/v1/sessions")
        async def create_session(user_id: Optional[str] = None, agent_type: Optional[str] = None):
            """Create new session"""
            session_id = await session_manager.create_session(user_id, agent_type)
            return {"session_id": session_id}
        
        # Performance monitoring endpoints
        @app.get("/api/v1/metrics")
        async def get_metrics():
            """Get performance metrics"""
            return await performance_monitor.get_dashboard_data()
        
        @app.get("/api/v1/metrics/performance")
        async def get_performance_stats():
            """Get performance statistics"""
            return await performance_monitor.get_performance_stats()
        
        # Security endpoints
        @app.get("/api/v1/security/events")
        async def get_security_events(limit: int = 100):
            """Get security events"""
            return await security_manager.get_security_events(limit)
        
        @app.get("/api/v1/security/stats")
        async def get_security_stats():
            """Get security statistics"""
            return await security_manager.get_security_stats()
        
        # Cache management endpoints
        @app.get("/api/v1/cache/stats")
        async def get_cache_stats():
            """Get cache statistics"""
            return await cache_manager.get_stats()
        
        @app.delete("/api/v1/cache/clear")
        async def clear_cache():
            """Clear cache"""
            success = await cache_manager.clear()
            return {"success": success}
        
        # Database endpoints
        @app.get("/api/v1/database/stats")
        async def get_database_stats():
            """Get database statistics"""
            return await database_manager.get_database_stats()
        
        @app.get("/api/v1/database/health")
        async def get_database_health():
            """Get database health"""
            return await database_manager.health_check()
        
        # Logging endpoints
        @app.get("/api/v1/logs")
        async def get_logs(category: Optional[str] = None, level: Optional[str] = None, limit: int = 1000):
            """Get logs"""
            from logging_system import LogCategory, LogLevel
            category_enum = LogCategory(category) if category else None
            level_enum = LogLevel(level) if level else None
            return await logging_system.get_logs(category_enum, level_enum, limit=limit)
        
        @app.get("/api/v1/logs/audit")
        async def get_audit_logs(user_id: Optional[str] = None, limit: int = 1000):
            """Get audit logs"""
            return await logging_system.get_audit_logs(user_id, limit=limit)
        
        # WebSocket endpoint
        @app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time communication"""
            connection_id = await websocket_manager.connect(websocket)
            
            try:
                while True:
                    message = await websocket.receive_text()
                    await websocket_manager.handle_message(connection_id, message)
            except Exception as e:
                await logging_system.log_error(e, "websocket", connection_id=connection_id)
            finally:
                await websocket_manager.disconnect(connection_id)
        
        # Root endpoint
        @app.get("/")
        async def root():
            """Root endpoint"""
            return {
                "service": "Frenly AI Integrated Service",
                "version": self.config.version,
                "status": "running",
                "uptime": time.time() - self.startup_time if self.startup_time else 0,
                "timestamp": datetime.now().isoformat(),
                "components": [
                    "agent_manager",
                    "model_manager", 
                    "cache_manager",
                    "session_manager",
                    "performance_monitor",
                    "security_manager",
                    "websocket_manager",
                    "database_manager",
                    "health_checker",
                    "logging_system"
                ]
            }

def create_app() -> FastAPI:
    """Create the integrated Frenly AI application"""
    service = FrenlyAIIntegratedService()
    return service.create_app()

# Create the app
app = create_app()

if __name__ == "__main__":
    import uvicorn
    
    config = get_config()
    uvicorn.run(
        "integrated_service:app",
        host=config.host,
        port=config.port,
        workers=config.workers,
        log_level=config.log_level.lower(),
        reload=config.debug
    )
