#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🔒 Enhanced Security Middleware for Nexus Platform
Comprehensive security headers, rate limiting, and protection mechanisms
"""

import time
import logging
from typing import Dict, Any, Optional
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import redis
import json
from datetime import datetime, timedelta
import hashlib
import re

logger = logging.getLogger(__name__)

class EnhancedSecurityMiddleware(BaseHTTPMiddleware):
    """Enhanced security middleware with comprehensive protection"""
    
    def __init__(
        """
          Init  
        
        
        Args:
            app: Description of app
            redis_client: Description of redis_client
            rate_limit_requests: Description of rate_limit_requests
            rate_limit_window: Description of rate_limit_window
            max_request_size: Description of max_request_size
            enable_csrf: Description of enable_csrf
            enable_xss_protection: Description of enable_xss_protection
            enable_sql_injection_protection: Description of enable_sql_injection_protection
    
        Example:
            TBD: Add usage example
        """
        self,
        app: ASGIApp,
        redis_client: Optional[redis.Redis] = None,
        rate_limit_requests: int = 100,
        rate_limit_window: int = 60,
        max_request_size: int = 10 * 1024 * 1024,  # 10MB
        enable_csrf: bool = True,
        enable_xss_protection: bool = True,
        enable_sql_injection_protection: bool = True
    ):
        super().__init__(app)
        self.redis_client = redis_client
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_window = rate_limit_window
        self.max_request_size = max_request_size
        self.enable_csrf = enable_csrf
        self.enable_xss_protection = enable_xss_protection
        self.enable_sql_injection_protection = enable_sql_injection_protection
        
        # Security patterns
        self.xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>',
            r'<link[^>]*>',
            r'<meta[^>]*>',
            r'<style[^>]*>.*?</style>'
        ]
        
        self.sql_injection_patterns = [
            r"('|(\\')|(;)|(\\;)|(--)|(\\--)|(/\*)|(\\/\*)|(\*/)|(\\\*/))",
            r"(union|select|insert|update|delete|drop|create|alter|exec|execute)",
            r"(or|and)\s+\d+\s*=\s*\d+",
            r"(or|and)\s+['\"]\s*=\s*['\"]",
            r"(or|and)\s+1\s*=\s*1",
            r"(or|and)\s+true",
            r"(or|and)\s+false"
        ]
        
        # Compile patterns for better performance
        self.xss_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.xss_patterns]
        self.sql_regex = [re.compile(pattern, re.IGNORECASE) for pattern in self.sql_injection_patterns]
    
    async def dispatch(self, request: Request, call_next):
        """Process request through security middleware"""
        start_time = time.time()
        
        try:
            # 1. Request size validation
            await self._validate_request_size(request)
            
            # 2. Rate limiting
            await self._check_rate_limit(request)
            
            # 3. Security header validation
            await self._validate_security_headers(request)
            
            # 4. Input validation
            await self._validate_inputs(request)
            
            # 5. CSRF protection
            if self.enable_csrf:
                await self._check_csrf(request)
            
            # Process request
            response = await call_next(request)
            
            # 6. Add security headers to response
            self._add_security_headers(response)
            
            # 7. Log security event
            await self._log_security_event(request, response, start_time)
            
            return response
            
        except HTTPException as e:
            # Log security violations
            await self._log_security_violation(request, str(e), start_time)
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.detail, "timestamp": datetime.now().isoformat()}
            )
        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            return JSONResponse(
                status_code=500,
                content={"error": "Internal security error", "timestamp": datetime.now().isoformat()}
            )
    
    async def _validate_request_size(self, request: Request):
        """Validate request size"""
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.max_request_size:
            raise HTTPException(
                status_code=413,
                detail=f"Request too large. Maximum size: {self.max_request_size} bytes"
            )
    
    async def _check_rate_limit(self, request: Request):
        """Check rate limiting"""
        if not self.redis_client:
            return
        
        client_ip = self._get_client_ip(request)
        user_id = self._get_user_id(request)
        key = f"rate_limit:{user_id or client_ip}"
        
        try:
            # Get current count
            current_count = self.redis_client.get(key)
            
            if current_count is None:
                # First request in window
                self.redis_client.setex(key, self.rate_limit_window, 1)
            else:
                count = int(current_count)
                if count >= self.rate_limit_requests:
                    raise HTTPException(
                        status_code=429,
                        detail=f"Rate limit exceeded. Max {self.rate_limit_requests} requests per {self.rate_limit_window} seconds"
                    )
                else:
                    self.redis_client.incr(key)
        except redis.RedisError as e:
            logger.warning(f"Rate limiting error: {e}")
    
    async def _validate_security_headers(self, request: Request):
        """Validate incoming security headers"""
        # Check for suspicious headers
        suspicious_headers = [
            "x-forwarded-for",
            "x-real-ip",
            "x-cluster-client-ip",
            "x-forwarded",
            "forwarded-for",
            "forwarded"
        ]
        
        for header in suspicious_headers:
            if header in request.headers:
                value = request.headers[header]
                # Basic validation for IP spoofing attempts
                if not self._is_valid_ip_header(value):
                    logger.warning(f"Suspicious header detected: {header}={value}")
    
    async def _validate_inputs(self, request: Request):
        """Validate request inputs for security threats"""
        # Check URL parameters
        for param, value in request.query_params.items():
            await self._validate_input_value(param, value, "query_param")
        
        # Check form data
        if request.headers.get("content-type", "").startswith("application/x-www-form-urlencoded"):
            form_data = await request.form()
            for field, value in form_data.items():
                await self._validate_input_value(field, str(value), "form_data")
        
        # Check JSON body
        if request.headers.get("content-type", "").startswith("application/json"):
            try:
                body = await request.json()
                await self._validate_json_input(body)
            except Exception:
                # If JSON parsing fails, let the application handle it
                pass
    
    async def _validate_input_value(self, field: str, value: str, input_type: str):
        """Validate individual input value"""
        if not value:
            return
        
        # XSS Protection
        if self.enable_xss_protection:
            for pattern in self.xss_regex:
                if pattern.search(value):
                    raise HTTPException(
                        status_code=400,
                        detail=f"XSS attempt detected in {input_type}: {field}"
                    )
        
        # SQL Injection Protection
        if self.enable_sql_injection_protection:
            for pattern in self.sql_regex:
                if pattern.search(value):
                    raise HTTPException(
                        status_code=400,
                        detail=f"SQL injection attempt detected in {input_type}: {field}"
                    )
    
    async def _validate_json_input(self, data: Any, path: str = ""):
        """Recursively validate JSON input"""
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                await self._validate_json_input(value, current_path)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                await self._validate_json_input(item, current_path)
        elif isinstance(data, str):
            await self._validate_input_value(path, data, "json_field")
    
    async def _check_csrf(self, request: Request):
        """Check CSRF protection"""
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return
        
        # Check CSRF token
        csrf_token = request.headers.get("x-csrf-token")
        if not csrf_token:
            raise HTTPException(
                status_code=403,
                detail="CSRF token missing"
            )
        
        # Validate CSRF token (implement your validation logic)
        if not self._validate_csrf_token(csrf_token, request):
            raise HTTPException(
                status_code=403,
                detail="Invalid CSRF token"
            )
    
    def _validate_csrf_token(self, token: str, request: Request) -> bool:
        """Validate CSRF token"""
        # Implement your CSRF token validation logic
        return len(token) > 10  # Basic validation
    
    def _add_security_headers(self, response: Response):
        """Add comprehensive security headers"""
        security_headers = {
            # Prevent MIME type sniffing
            "X-Content-Type-Options": "nosniff",
            
            # Prevent clickjacking
            "X-Frame-Options": "DENY",
            
            # XSS Protection
            "X-XSS-Protection": "1; mode=block",
            
            # HSTS (only for HTTPS)
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            
            # Content Security Policy
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' wss:; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            ),
            
            # Referrer Policy
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Permissions Policy
            "Permissions-Policy": (
                "camera=(), microphone=(), geolocation=(), "
                "interest-cohort=(), payment=(), usb=(), "
                "magnetometer=(), gyroscope=(), accelerometer=()"
            ),
            
            # Cache Control for sensitive endpoints
            "Cache-Control": "no-store, no-cache, must-revalidate, proxy-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _get_user_id(self, request: Request) -> Optional[str]:
        """Get user ID from request (implement based on your auth system)"""
        # Extract user ID from JWT token or session
        return None
    
    def _is_valid_ip_header(self, value: str) -> bool:
        """Validate IP header value"""
        import ipaddress
        try:
            # Split by comma and validate each IP
            ips = [ip.strip() for ip in value.split(",")]
            for ip in ips:
                ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    async def _log_security_event(self, request: Request, response: Response, start_time: float):
        """Log security event"""
        duration = time.time() - start_time
        
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": "security_event",
            "method": request.method,
            "url": str(request.url),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", ""),
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
            "response_size": len(response.body) if hasattr(response, 'body') else 0
        }
        
        logger.info(f"Security event: {json.dumps(event)}")
    
    async def _log_security_violation(self, request: Request, error: str, start_time: float):
        """Log security violation"""
        duration = time.time() - start_time
        
        violation = {
            "timestamp": datetime.now().isoformat(),
            "type": "security_violation",
            "method": request.method,
            "url": str(request.url),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", ""),
            "error": error,
            "duration_ms": round(duration * 1000, 2)
        }
        
        logger.warning(f"Security violation: {json.dumps(violation)}")
        
        # Store in Redis for analysis
        if self.redis_client:
            try:
                key = f"security_violation:{datetime.now().strftime('%Y%m%d%H%M%S')}"
                self.redis_client.setex(key, 86400, json.dumps(violation))  # Keep for 24 hours
            except redis.RedisError as e:
                logger.error(f"Failed to store security violation: {e}")

# Security utilities
class SecurityUtils:
    """Security utility functions"""
    
    @staticmethod
    def generate_csrf_token(user_id: str, session_id: str) -> str:
        """Generate CSRF token"""
        data = f"{user_id}:{session_id}:{datetime.now().timestamp()}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    @staticmethod
    def sanitize_input(value: str) -> str:
        """Sanitize user input"""
        if not value:
            return ""
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Normalize unicode
        value = value.encode('utf-8', errors='ignore').decode('utf-8')
        
        # Trim whitespace
        value = value.strip()
        
        return value
    
    @staticmethod
    def is_safe_filename(filename: str) -> bool:
        """Check if filename is safe"""
        if not filename:
            return False
        
        # Check for path traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            return False
        
        # Check for dangerous extensions
        dangerous_extensions = ['.exe', '.bat', '.cmd', '.scr', '.pif', '.com']
        filename_lower = filename.lower()
        for ext in dangerous_extensions:
            if filename_lower.endswith(ext):
                return False
        
        return True
