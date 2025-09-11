#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
📝 Logging Middleware - Nexus Platform
Request/response logging middleware
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from fastapi import Request
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    LoggingMiddleware Class
    
    Logging Middleware
    
    Attributes:
        TBD: Add attribute descriptions
    
    Methods:
        TBD: Add method descriptions
    
    Example:
        TBD: Add usage example
    """
    def __init__(self, app: ASGIApp):
        """
          Init  
        
        
        Args:
            app: Description of app
    
        Example:
            TBD: Add usage example
        """
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(f"Response: {response.status_code} - {process_time:.4f}s")
        
        return response

if __name__ == "__main__":
    pass