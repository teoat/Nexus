#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🚀 Frenly AI Service Launcher
Main launcher for Frenly AI service with full orchestration
"""

import asyncio
import logging
import signal
import sys
import time
from pathlib import Path
from typing import Dict, Any
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import get_config, validate_config
from agent_manager import agent_manager
from api_router import router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/workspace/logs/frenly_ai.log')
    ]
)
logger = logging.getLogger(__name__)

class FrenlyAILauncher:
    """Main launcher for Frenly AI service"""
    
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
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        logger.info("✅ Frenly AI Launcher initialized")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        sys.exit(0)
    
    async def startup(self):
        """Startup tasks"""
        logger.info("🚀 Starting Frenly AI Service...")
        
        try:
            # Validate configuration
            if not validate_config():
                logger.error("❌ Configuration validation failed")
                return False
            
            # Create logs directory
            Path(self.config.logs_path).mkdir(parents=True, exist_ok=True)
            
            # Start agent manager
            await agent_manager.start()
            
            # Record startup time
            self.startup_time = time.time()
            
            logger.info("✅ Frenly AI Service started successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start Frenly AI Service: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown tasks"""
        logger.info("🛑 Shutting down Frenly AI Service...")
        
        try:
            # Stop agent manager
            await agent_manager.stop()
            
            logger.info("✅ Frenly AI Service shut down successfully")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")
    
    def create_app(self) -> FastAPI:
        """Create FastAPI application"""
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            await self.startup()
            yield
            # Shutdown
            await self.shutdown()
        
        app = FastAPI(
            title="Frenly AI Service",
            description="Meta-Agent Coordinator for Nexus Platform",
            version=self.config.version,
            docs_url="/docs",
            redoc_url="/redoc",
            lifespan=lifespan
        )
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Include API router
        app.include_router(router)
        
        # Add root endpoint
        @app.get("/")
        async def root():
            return {
                "service": "Frenly AI Service",
                "version": self.config.version,
                "status": "running",
                "uptime": time.time() - self.startup_time if self.startup_time else 0,
                "timestamp": time.time()
            }
        
        # Add health check endpoint
        @app.get("/health")
        async def health():
            return await health_check()
        
        return app
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for the service"""
        try:
            # Get agent status
            agents_data = await agent_manager.get_agent_status()
            active_agents = len([agent for agent in agents_data if agent["status"] in ["idle", "busy"]])
            
            # Calculate total requests
            total_requests = sum(agent["metrics"]["total_requests"] for agent in agents_data)
            
            return {
                "status": "healthy",
                "timestamp": time.time(),
                "version": self.config.version,
                "uptime": time.time() - self.startup_time if self.startup_time else 0,
                "active_agents": active_agents,
                "total_agents": len(agents_data),
                "total_requests": total_requests,
                "database_connected": True,  # Simplified for now
                "redis_connected": True      # Simplified for now
            }
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return {
                "status": "unhealthy",
                "timestamp": time.time(),
                "error": str(e)
            }
    
    def run(self):
        """Run the Frenly AI service"""
        try:
            # Create FastAPI app
            self.app = self.create_app()
            
            # Configure uvicorn
            uvicorn_config = uvicorn.Config(
                app=self.app,
                host=self.config.host,
                port=self.config.port,
                workers=self.config.workers,
                log_level=self.config.log_level.lower(),
                access_log=True,
                reload=self.config.debug
            )
            
            # Create server
            server = uvicorn.Server(uvicorn_config)
            
            # Run server
            logger.info(f"🌐 Starting server on {self.config.host}:{self.config.port}")
            self.running = True
            server.run()
            
        except Exception as e:
            logger.error(f"❌ Failed to run Frenly AI service: {e}")
            sys.exit(1)

def main():
    """Main entry point"""
    try:
        # Create and run launcher
        launcher = FrenlyAILauncher()
        launcher.run()
        
    except KeyboardInterrupt:
        logger.info("🛑 Received keyboard interrupt, shutting down...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
