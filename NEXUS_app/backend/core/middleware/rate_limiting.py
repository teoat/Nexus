"""
rate_limiting Module

Rate Limiting

This module provides functionality for rate limiting.

Classes:
    TBD: Add class descriptions

Functions:
    TBD: Add function descriptions

Example:
    TBD: Add usage example

Author: NEXUS Platform
Created: 2025-09-11
Version: 1.0.0
"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import logging
from typing import Dict, List, Optional
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Advanced rate limiting middleware with multiple strategies.
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
        
        # Rate limiting configuration
        self.default_limits = {
            "global": {"requests": 1000, "window": 3600},  # 1000 requests per hour
            "per_ip": {"requests": 100, "window": 60},     # 100 requests per minute per IP
            "per_user": {"requests": 200, "window": 60},   # 200 requests per minute per user
            "auth": {"requests": 10, "window": 60},        # 10 auth attempts per minute
            "api": {"requests": 1000, "window": 3600},     # 1000 API calls per hour
        }
        
        # Storage for rate limiting data
        self.rate_limits: Dict[str, Dict[str, deque]] = defaultdict(lambda: defaultdict(deque))
        
        # Cleanup configuration
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
        
        # Exempt paths
        self.exempt_paths = [
            "/health",
            "/health/detailed",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]
        
        # User identification methods
        self.user_id_headers = ["x-user-id", "x-api-key", "authorization"]
    
    async def dispatch(self, request: Request, call_next):
        """Process request through rate limiting middleware."""
        try:
            # Skip rate limiting for exempt paths
            if self._is_exempt_path(request):
                return await call_next(request)
            
            # Get rate limit key
            rate_limit_key = self._get_rate_limit_key(request)
            
            # Check rate limits
            self._check_rate_limits(request, rate_limit_key)
            
            # Process request
            response = await call_next(request)
            
            # Record successful request
            self._record_request(rate_limit_key)
            
            # Add rate limit headers
            self._add_rate_limit_headers(response, rate_limit_key)
            
            # Cleanup old data periodically
            self._cleanup_old_data()
            
            return response
            
        except HTTPException as e:
            if e.status_code == 429:
                # Add rate limit headers even for blocked requests
                response = HTTPException(
                    status_code=429,
                    detail=e.detail
                )
                self._add_rate_limit_headers(response, rate_limit_key)
            raise
        except Exception as e:
            logger.error(f"Rate limiting middleware error: {e}")
            return await call_next(request)
    
    def _is_exempt_path(self, request: Request) -> bool:
        """Check if path is exempt from rate limiting."""
        path = str(request.url.path)
        return any(path.startswith(exempt) for exempt in self.exempt_paths)
    
    def _get_rate_limit_key(self, request: Request) -> Dict[str, str]:
        """Get rate limiting keys for different strategies."""
        client_ip = request.client.host
        user_id = self._get_user_id(request)
        endpoint_type = self._get_endpoint_type(request)
        
        return {
            "global": "global",
            "per_ip": f"ip:{client_ip}",
            "per_user": f"user:{user_id}" if user_id else f"ip:{client_ip}",
            "endpoint": f"{endpoint_type}:{client_ip}",
            "path": f"path:{request.url.path}:{client_ip}"
        }
    
    def _get_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request headers."""
        for header in self.user_id_headers:
            value = request.headers.get(header)
            if value:
                # Extract user ID from different header formats
                if header == "authorization":
                    # Extract from Bearer token (simplified)
                    if value.startswith("Bearer "):
                        return value[7:12]  # First 5 chars of token
                else:
                    return value
        return None
    
    def _get_endpoint_type(self, request: Request) -> str:
        """Determine endpoint type for rate limiting."""
        path = str(request.url.path)
        
        if path.startswith("/auth"):
            return "auth"
        elif path.startswith("/api"):
            return "api"
        elif path.startswith("/admin"):
            return "admin"
        else:
            return "general"
    
    def _check_rate_limits(self, request: Request, rate_limit_key: Dict[str, str]):
        """Check all applicable rate limits."""
        current_time = time.time()
        
        # Check global rate limit
        self._check_single_rate_limit(
            "global", 
            rate_limit_key["global"], 
            self.default_limits["global"],
            current_time
        )
        
        # Check per-IP rate limit
        self._check_single_rate_limit(
            "per_ip", 
            rate_limit_key["per_ip"], 
            self.default_limits["per_ip"],
            current_time
        )
        
        # Check per-user rate limit (if user identified)
        if rate_limit_key["per_user"].startswith("user:"):
            self._check_single_rate_limit(
                "per_user", 
                rate_limit_key["per_user"], 
                self.default_limits["per_user"],
                current_time
            )
        
        endpoint_type = self._get_endpoint_type(request)
        if endpoint_type in self.default_limits:
            self._check_single_rate_limit(
                endpoint_type, 
                rate_limit_key["endpoint"], 
                self.default_limits[endpoint_type],
                current_time
            )
    
    def _check_single_rate_limit(self, limit_type: str, key: str, limits: Dict, current_time: float):
        """Check a single rate limit."""
        requests = limits["requests"]
        window = limits["window"]
        
        # Get request times for this key
        request_times = self.rate_limits[limit_type][key]
        
        # Remove old requests outside the window
        cutoff_time = current_time - window
        while request_times and request_times[0] <= cutoff_time:
            request_times.popleft()
        
        # Check if limit exceeded
        if len(request_times) >= requests:
            remaining_time = request_times[0] + window - current_time
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded for {limit_type}. Try again in {int(remaining_time)} seconds."
            )
    
    def _record_request(self, rate_limit_key: Dict[str, str]):
        """Record a successful request."""
        current_time = time.time()
        
        for limit_type, key in rate_limit_key.items():
            self.rate_limits[limit_type][key].append(current_time)
    
    def _add_rate_limit_headers(self, response, rate_limit_key: Dict[str, str]):
        """Add rate limit information to response headers."""
        if hasattr(response, 'headers'):
            current_time = time.time()
            
            # Add headers for each rate limit type
            for limit_type, key in rate_limit_key.items():
                if limit_type in self.default_limits:
                    limits = self.default_limits[limit_type]
                    request_times = self.rate_limits[limit_type][key]
                    
                    # Clean old requests
                    cutoff_time = current_time - limits["window"]
                    while request_times and request_times[0] <= cutoff_time:
                        request_times.popleft()
                    
                    # Add headers
                    response.headers[f"X-RateLimit-{limit_type.title()}-Limit"] = str(limits["requests"])
                    response.headers[f"X-RateLimit-{limit_type.title()}-Remaining"] = str(max(0, limits["requests"] - len(request_times)))
                    response.headers[f"X-RateLimit-{limit_type.title()}-Reset"] = str(int(current_time + limits["window"]))
    
    def _cleanup_old_data(self):
        """Clean up old rate limiting data."""
        current_time = time.time()
        
        # Only cleanup every cleanup_interval seconds
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        self.last_cleanup = current_time
        
        # Clean up old data for each rate limit type
        for limit_type, limits in self.default_limits.items():
            window = limits["window"]
            cutoff_time = current_time - window
            
            # Clean up old entries
            for key in list(self.rate_limits[limit_type].keys()):
                request_times = self.rate_limits[limit_type][key]
                
                # Remove old requests
                while request_times and request_times[0] <= cutoff_time:
                    request_times.popleft()
                
                # Remove empty entries
                if not request_times:
                    del self.rate_limits[limit_type][key]
        
        logger.debug(f"Rate limiting data cleaned up. Active keys: {sum(len(keys) for keys in self.rate_limits.values())}")
    
    def get_rate_limit_status(self, identifier: str) -> Dict:
        """Get current rate limit status for an identifier."""
        current_time = time.time()
        status = {}
        
        for limit_type, limits in self.default_limits.items():
            key = f"{limit_type}:{identifier}"
            request_times = self.rate_limits[limit_type].get(key, deque())
            
            # Clean old requests
            cutoff_time = current_time - limits["window"]
            while request_times and request_times[0] <= cutoff_time:
                request_times.popleft()
            
            status[limit_type] = {
                "limit": limits["requests"],
                "remaining": max(0, limits["requests"] - len(request_times)),
                "used": len(request_times),
                "reset_time": int(current_time + limits["window"])
            }
        
        return status
    
    def reset_rate_limit(self, identifier: str, limit_type: Optional[str] = None):
        """Reset rate limit for an identifier."""
        if limit_type:
            if limit_type in self.rate_limits:
                key = f"{limit_type}:{identifier}"
                if key in self.rate_limits[limit_type]:
                    del self.rate_limits[limit_type][key]
        else:
            # Reset all rate limits for this identifier
            for limit_type in self.rate_limits:
                key = f"{limit_type}:{identifier}"
                if key in self.rate_limits[limit_type]:
                    del self.rate_limits[limit_type][key]
    
    def update_rate_limits(self, new_limits: Dict[str, Dict[str, int]]):
        """Update rate limiting configuration."""
        self.default_limits.update(new_limits)
        logger.info(f"Rate limiting configuration updated: {new_limits}")
    
    def get_statistics(self) -> Dict:
        """Get rate limiting statistics."""
        current_time = time.time()
        stats = {
            "total_keys": sum(len(keys) for keys in self.rate_limits.values()),
            "active_limits": {},
            "last_cleanup": self.last_cleanup
        }
        
        for limit_type, limits in self.default_limits.items():
            active_keys = 0
            total_requests = 0
            
            for key, request_times in self.rate_limits[limit_type].items():
                # Clean old requests
                cutoff_time = current_time - limits["window"]
                while request_times and request_times[0] <= cutoff_time:
                    request_times.popleft()
                
                if request_times:
                    active_keys += 1
                    total_requests += len(request_times)
            
            stats["active_limits"][limit_type] = {
                "active_keys": active_keys,
                "total_requests": total_requests,
                "limit": limits["requests"],
                "window": limits["window"]
            }
        
        return stats
