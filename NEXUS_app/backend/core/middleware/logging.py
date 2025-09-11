"""
logging Module

Logging

This module provides functionality for logging.

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
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import logging
import json
from typing import Dict, Any
import uuid

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive logging middleware for the Nexus Platform.
    Logs all requests and responses with detailed information.
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
        
        # Configure structured logging
        self.logger = logging.getLogger("nexus.request")
        self.logger.setLevel(logging.INFO)
        
        # Request logging configuration
        self.log_requests = True
        self.log_responses = True
        self.log_headers = True
        self.log_body = False  # Set to True for debugging
        self.max_body_length = 1000  # Truncate long bodies
        
        # Sensitive headers to mask
        self.sensitive_headers = {
            "authorization", "x-api-key", "cookie", "x-csrf-token",
            "x-auth-token", "x-access-token", "x-refresh-token"
        }
        
        # Sensitive body fields to mask
        self.sensitive_fields = {
            "password", "token", "secret", "key", "credential",
            "ssn", "credit_card", "bank_account"
        }
    
    async def dispatch(self, request: Request, call_next):
        """Process request through logging middleware."""
        # Generate unique request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request
        if self.log_requests:
            await self._log_request(request, request_id)
        
        # Process request
        start_time = time.time()
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            if self.log_responses:
                await self._log_response(request, response, request_id, process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            
            # Log error
            await self._log_error(request, e, request_id, process_time)
            raise
    
    async def _log_request(self, request: Request, request_id: str):
        """Log incoming request."""
        try:
            # Extract request information
            request_data = {
                "request_id": request_id,
                "timestamp": time.time(),
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client_ip": request.client.host,
                "user_agent": request.headers.get("user-agent", ""),
                "content_type": request.headers.get("content-type", ""),
                "content_length": request.headers.get("content-length", "0"),
            }
            
            # Add headers (masked)
            if self.log_headers:
                request_data["headers"] = self._mask_sensitive_headers(dict(request.headers))
            
            # Add body (if enabled and not too large)
            if self.log_body and request.method in ["POST", "PUT", "PATCH"]:
                body = await self._get_request_body(request)
                if body:
                    request_data["body"] = self._mask_sensitive_data(body)
            
            # Log request
            self.logger.info(
                f"Request received",
                extra={"request_data": request_data}
            )
            
        except Exception as e:
            logger.error(f"Error logging request: {e}")
    
    async def _log_response(self, request: Request, response: Response, request_id: str, process_time: float):
        """Log outgoing response."""
        try:
            # Extract response information
            response_data = {
                "request_id": request_id,
                "timestamp": time.time(),
                "status_code": response.status_code,
                "process_time": round(process_time, 3),
                "content_type": response.headers.get("content-type", ""),
                "content_length": response.headers.get("content-length", "0"),
            }
            
            # Add response headers (masked)
            if self.log_headers:
                response_data["headers"] = self._mask_sensitive_headers(dict(response.headers))
            
            # Determine log level based on status code
            if response.status_code >= 500:
                log_level = "error"
            elif response.status_code >= 400:
                log_level = "warning"
            else:
                log_level = "info"
            
            # Log response
            getattr(self.logger, log_level)(
                f"Response sent",
                extra={"response_data": response_data}
            )
            
        except Exception as e:
            logger.error(f"Error logging response: {e}")
    
    async def _log_error(self, request: Request, error: Exception, request_id: str, process_time: float):
        """Log error response."""
        try:
            error_data = {
                "request_id": request_id,
                "timestamp": time.time(),
                "error_type": type(error).__name__,
                "error_message": str(error),
                "process_time": round(process_time, 3),
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host,
            }
            
            # Log error
            self.logger.error(
                f"Request failed",
                extra={"error_data": error_data},
                exc_info=True
            )
            
        except Exception as e:
            logger.error(f"Error logging error: {e}")
    
    async def _get_request_body(self, request: Request) -> str:
        """Get request body as string."""
        try:
            # Read body
            body = await request.body()
            
            # Check size limit
            if len(body) > self.max_body_length:
                return f"[Body too large: {len(body)} bytes]"
            
            # Decode body
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                try:
                    return json.dumps(json.loads(body), indent=2)
                except json.JSONDecodeError:
                    return body.decode("utf-8", errors="replace")
            else:
                return body.decode("utf-8", errors="replace")
                
        except Exception as e:
            return f"[Error reading body: {e}]"
    
    def _mask_sensitive_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Mask sensitive headers."""
        masked_headers = {}
        
        for key, value in headers.items():
            if key.lower() in self.sensitive_headers:
                masked_headers[key] = "***MASKED***"
            else:
                masked_headers[key] = value
        
        return masked_headers
    
    def _mask_sensitive_data(self, data: Any) -> Any:
        """Mask sensitive data in request/response body."""
        if isinstance(data, dict):
            masked_data = {}
            for key, value in data.items():
                if any(sensitive in key.lower() for sensitive in self.sensitive_fields):
                    masked_data[key] = "***MASKED***"
                else:
                    masked_data[key] = self._mask_sensitive_data(value)
            return masked_data
        elif isinstance(data, list):
            return [self._mask_sensitive_data(item) for item in data]
        elif isinstance(data, str):
            # Check if string contains sensitive patterns
            if any(sensitive in data.lower() for sensitive in self.sensitive_fields):
                return "***MASKED***"
            return data
        else:
            return data
    
    def _get_user_info(self, request: Request) -> Dict[str, Any]:
        """Extract user information from request."""
        user_info = {}
        
        # Try to get user ID from various sources
        user_id = request.headers.get("x-user-id")
        if user_id:
            user_info["user_id"] = user_id
        
        # Try to get API key
        api_key = request.headers.get("x-api-key")
        if api_key:
            user_info["api_key"] = api_key[:8] + "..."  # Truncated for security
        
        # Try to get session info
        session_id = request.headers.get("x-session-id")
        if session_id:
            user_info["session_id"] = session_id
        
        return user_info
    
    def _get_geolocation_info(self, request: Request) -> Dict[str, Any]:
        """Extract geolocation information from request."""
        geo_info = {}
        
        # Get IP address
        client_ip = request.client.host
        geo_info["ip_address"] = client_ip
        
        # Try to get country from headers (if behind a proxy)
        country = request.headers.get("cf-ipcountry") or request.headers.get("x-country")
        if country:
            geo_info["country"] = country
        
        # Try to get city from headers
        city = request.headers.get("cf-ipcity") or request.headers.get("x-city")
        if city:
            geo_info["city"] = city
        
        return geo_info
    
    def _get_performance_metrics(self, request: Request, process_time: float) -> Dict[str, Any]:
        """Calculate performance metrics."""
        return {
            "process_time": round(process_time, 3),
            "process_time_ms": round(process_time * 1000, 1),
            "timestamp": time.time(),
            "method": request.method,
            "path": request.url.path,
        }
    
    def _should_log_request(self, request: Request) -> bool:
        """Determine if request should be logged."""
        # Skip logging for health checks
        if request.url.path in ["/health", "/health/detailed"]:
            return False
        
        # Skip logging for static files
        if request.url.path.startswith("/static/"):
            return False
        
        return True
    
    def _should_log_response(self, response: Response) -> bool:
        """Determine if response should be logged."""
        # Always log errors
        if response.status_code >= 400:
            return True
        
        # Log successful responses based on configuration
        return self.log_responses
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Get logging statistics."""
        # This would typically come from a metrics collector
        return {
            "total_requests": 0,  # Would be tracked in production
            "error_rate": 0.0,
            "average_response_time": 0.0,
            "log_level": self.logger.level,
            "log_requests": self.log_requests,
            "log_responses": self.log_responses,
        }
    
    def update_logging_config(self, config: Dict[str, Any]):
        """Update logging configuration."""
        self.log_requests = config.get("log_requests", self.log_requests)
        self.log_responses = config.get("log_responses", self.log_responses)
        self.log_headers = config.get("log_headers", self.log_headers)
        self.log_body = config.get("log_body", self.log_body)
        self.max_body_length = config.get("max_body_length", self.max_body_length)
        
        logger.info(f"Logging configuration updated: {config}")
