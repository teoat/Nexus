#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
Rate limiting middleware for Nexus Platform
"""

import time
import logging
from typing import Dict, Any
from collections import defaultdict, deque
from fastapi import Request, HTTPException

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter implementation"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
          Init  
        
        
        Args:
            max_requests: Description of max_requests
            window_seconds: Description of window_seconds
    
        Example:
            TBD: Add usage example
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(deque)
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed for client"""
        now = time.time()
        client_requests = self.requests[client_id]
        
        # Remove old requests outside the window
        while client_requests and client_requests[0] <= now - self.window_seconds:
            client_requests.popleft()
        
        # Check if under limit
        if len(client_requests) < self.max_requests:
            client_requests.append(now)
            return True
        
        return False

class RateLimitingMiddleware:
    """Rate limiting middleware"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
          Init  
        
        
        Args:
            max_requests: Description of max_requests
            window_seconds: Description of window_seconds
    
        Example:
            TBD: Add usage example
        """
        self.rate_limiter = RateLimiter(max_requests, window_seconds)
    
    def get_client_id(self, request: Request) -> str:
        """Get client identifier from request"""
        # Use IP address as client identifier
        client_ip = request.client.host if request.client else "unknown"
        return client_ip
    
    def process_request(self, request: Request) -> Request:
        """Process rate limiting for request"""
        client_id = self.get_client_id(request)
        
        if not self.rate_limiter.is_allowed(client_id):
            logger.warning(f"Rate limit exceeded for client: {client_id}")
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        return request
