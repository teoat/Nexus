#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
Logging middleware for Nexus Platform
"""

import time
import logging
from typing import Dict, Any
from fastapi import Request, Response

logger = logging.getLogger(__name__)

class LoggingMiddleware:
    """Logging middleware for request/response logging"""
    
    def __init__(self, log_level: str = "INFO"):
        """
          Init  
        
        
        Args:
            log_level: Description of log_level
    
        Example:
            TBD: Add usage example
        """
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger = logging.getLogger("middleware.logging")
        self.logger.setLevel(self.log_level)
    
    def log_request(self, request: Request) -> Request:
        """Log incoming request"""
        self.logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        request.state.start_time = time.time()
        return request
    
    def log_response(self, response: Response) -> Response:
        """Log outgoing response"""
        if hasattr(response, 'request') and hasattr(response.request, 'state'):
            duration = time.time() - getattr(response.request.state, 'start_time', 0)
            self.logger.info(
                f"Response: {response.status_code} "
                f"in {duration:.3f}s"
            )
        return response
    
    def process_request(self, request: Request) -> Request:
        """Process request logging"""
        return self.log_request(request)
    
    def process_response(self, response: Response) -> Response:
        """Process response logging"""
        return self.log_response(response)
