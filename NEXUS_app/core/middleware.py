#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
Middleware module for Nexus Platform
Provides common middleware functionality.
"""

import time
import logging
from typing import Callable, Any
from fastapi import Request, Response

logger = logging.getLogger(__name__)

class MiddlewareManager:
    """Manages middleware for the application"""
    
    def __init__(self):
        """
          Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        self.middleware_stack = []
    
    def add_middleware(self, middleware: Callable):
        """Add middleware to the stack"""
        self.middleware_stack.append(middleware)
    
    def process_request(self, request: Request) -> Request:
        """Process request through middleware stack"""
        for middleware in self.middleware_stack:
            request = middleware(request)
        return request
    
    def process_response(self, response: Response) -> Response:
        """Process response through middleware stack"""
        for middleware in reversed(self.middleware_stack):
            response = middleware(response)
        return response

# Global middleware manager
middleware_manager = MiddlewareManager()

def timing_middleware(request: Request) -> Request:
    """Add timing information to request"""
    request.state.start_time = time.time()
    return request

def logging_middleware(request: Request) -> Request:
    """Add logging to request"""
    logger.info(f"Processing request: {request.method} {request.url}")
    return request

# Add default middleware
middleware_manager.add_middleware(timing_middleware)
middleware_manager.add_middleware(logging_middleware)
