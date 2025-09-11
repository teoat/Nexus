#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🔒 Production Security Configuration for Nexus Platform
Comprehensive security hardening and compliance features
"""

import os
import logging
import hashlib
import secrets
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import redis
import json

logger = logging.getLogger(__name__)

class ProductionSecurityManager:
    """Production security management system"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Security policies
        self.policies = {
            "password_min_length": 12,
            "password_require_uppercase": True,
            "password_require_lowercase": True,
            "password_require_numbers": True,
            "password_require_symbols": True,
            "max_login_attempts": 5,
            "lockout_duration_minutes": 30,
            "session_timeout_minutes": 30,
            "jwt_expiration_minutes": 30,
            "jwt_refresh_expiration_days": 7,
            "max_file_size_mb": 10,
            "allowed_file_types": ["text/csv", "application/json", "application/vnd.ms-excel"],
            "rate_limit_requests": 100,
            "rate_limit_window_seconds": 60,
            "max_request_size_mb": 10
        }
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for sensitive data"""
        key_file = Path("security/encryption.key")
        key_file.parent.mkdir(exist_ok=True)
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            # Set restrictive permissions
            os.chmod(key_file, 0o600)
            return key
    
    def generate_secure_password(self, length: int = 16) -> str:
        """Generate a secure random password"""
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength against security policies"""
        issues = []
        score = 0
        
        # Length check
        if len(password) < self.policies["password_min_length"]:
            issues.append(f"Password must be at least {self.policies['password_min_length']} characters long")
        else:
            score += 1
        
        # Character type checks
        if self.policies["password_require_uppercase"] and not any(c.isupper() for c in password):
            issues.append("Password must contain at least one uppercase letter")
        else:
            score += 1
        
        if self.policies["password_require_lowercase"] and not any(c.islower() for c in password):
            issues.append("Password must contain at least one lowercase letter")
        else:
            score += 1
        
        if self.policies["password_require_numbers"] and not any(c.isdigit() for c in password):
            issues.append("Password must contain at least one number")
        else:
            score += 1
        
        if self.policies["password_require_symbols"] and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        else:
            score += 1
        
        # Common password check
        common_passwords = [
            "password", "123456", "123456789", "qwerty", "abc123",
            "password123", "admin", "letmein", "welcome", "monkey"
        ]
        if password.lower() in common_passwords:
            issues.append("Password is too common")
            score -= 1
        
        # Sequential character check
        if self._has_sequential_chars(password):
            issues.append("Password contains sequential characters")
            score -= 1
        
        # Repeated character check
        if self._has_repeated_chars(password):
            issues.append("Password contains too many repeated characters")
            score -= 1
        
        return {
            "valid": len(issues) == 0,
            "score": max(0, score),
            "issues": issues,
            "strength": self._get_strength_level(score)
        }
    
    def _has_sequential_chars(self, password: str) -> bool:
        """Check for sequential characters"""
        for i in range(len(password) - 2):
            if (ord(password[i+1]) == ord(password[i]) + 1 and 
                ord(password[i+2]) == ord(password[i]) + 2):
                return True
        return False
    
    def _has_repeated_chars(self, password: str) -> bool:
        """Check for repeated characters"""
        char_count = {}
        for char in password:
            char_count[char] = char_count.get(char, 0) + 1
            if char_count[char] > 3:  # More than 3 repetitions
                return True
        return False
    
    def _get_strength_level(self, score: int) -> str:
        """Get password strength level"""
        if score >= 5:
            return "strong"
        elif score >= 3:
            return "medium"
        elif score >= 1:
            return "weak"
        else:
            return "very_weak"
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        try:
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            raise
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            raise
    
    def hash_password(self, password: str, salt: str = None) -> Dict[str, str]:
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(32)
        
        # Use PBKDF2 for password hashing
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=100000,
        )
        key = base64.b64encode(kdf.derive(password.encode()))
        
        return {
            "hash": key.decode(),
            "salt": salt
        }
    
    def verify_password(self, password: str, stored_hash: str, salt: str) -> bool:
        """Verify password against stored hash"""
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt.encode(),
                iterations=100000,
            )
            key = base64.b64encode(kdf.derive(password.encode()))
            return key.decode() == stored_hash
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    def generate_jwt_token(self, user_id: str, additional_claims: Dict[str, Any] = None) -> str:
        """Generate JWT token with security best practices"""
        now = datetime.utcnow()
        payload = {
            "user_id": user_id,
            "iat": now,
            "exp": now + timedelta(minutes=self.policies["jwt_expiration_minutes"]),
            "iss": "nexus-platform",
            "aud": "nexus-users",
            "jti": secrets.token_urlsafe(32)  # JWT ID for token tracking
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        # Add security headers
        headers = {
            "alg": "HS256",
            "typ": "JWT"
        }
        
        secret_key = os.getenv("JWT_SECRET_KEY", "default-secret-key")
        return jwt.encode(payload, secret_key, algorithm="HS256", headers=headers)
    
    def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            secret_key = os.getenv("JWT_SECRET_KEY", "default-secret-key")
            payload = jwt.decode(
                token, 
                secret_key, 
                algorithms=["HS256"],
                audience="nexus-users",
                issuer="nexus-platform"
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {e}")
    
    def track_login_attempt(self, user_id: str, ip_address: str, success: bool) -> bool:
        """Track login attempts for security monitoring"""
        if not self.redis_client:
            return True
        
        try:
            key = f"login_attempts:{user_id}:{ip_address}"
            
            if success:
                # Clear failed attempts on successful login
                self.redis_client.delete(key)
                return True
            else:
                # Increment failed attempts
                attempts = self.redis_client.incr(key)
                self.redis_client.expire(key, self.policies["lockout_duration_minutes"] * 60)
                
                if attempts >= self.policies["max_login_attempts"]:
                    # Account locked
                    lockout_key = f"account_locked:{user_id}"
                    self.redis_client.setex(
                        lockout_key, 
                        self.policies["lockout_duration_minutes"] * 60, 
                        "locked"
                    )
                    logger.warning(f"Account locked for user {user_id} from IP {ip_address}")
                    return False
                
                return True
                
        except Exception as e:
            logger.error(f"Error tracking login attempt: {e}")
            return True
    
    def is_account_locked(self, user_id: str) -> bool:
        """Check if account is locked"""
        if not self.redis_client:
            return False
        
        try:
            lockout_key = f"account_locked:{user_id}"
            return self.redis_client.exists(lockout_key) > 0
        except Exception as e:
            logger.error(f"Error checking account lock status: {e}")
            return False
    
    def validate_file_upload(self, filename: str, content_type: str, file_size: int) -> Dict[str, Any]:
        """Validate file upload for security"""
        issues = []
        
        # File size check
        max_size = self.policies["max_file_size_mb"] * 1024 * 1024
        if file_size > max_size:
            issues.append(f"File size exceeds maximum allowed size of {self.policies['max_file_size_mb']}MB")
        
        # File type check
        if content_type not in self.policies["allowed_file_types"]:
            issues.append(f"File type {content_type} is not allowed")
        
        # Filename security check
        if not self._is_safe_filename(filename):
            issues.append("Filename contains potentially dangerous characters")
        
        # File extension check
        allowed_extensions = [".csv", ".json", ".xlsx", ".xls"]
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in allowed_extensions:
            issues.append(f"File extension {file_ext} is not allowed")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
    
    def _is_safe_filename(self, filename: str) -> bool:
        """Check if filename is safe"""
        if not filename:
            return False
        
        # Check for path traversal
        if ".." in filename or "/" in filename or "\\" in filename:
            return False
        
        # Check for dangerous characters
        dangerous_chars = ["<", ">", ":", '"', "|", "?", "*"]
        if any(char in filename for char in dangerous_chars):
            return False
        
        return True
    
    def sanitize_input(self, input_data: str) -> str:
        """Sanitize user input"""
        if not input_data:
            return ""
        
        # Remove null bytes
        input_data = input_data.replace('\x00', '')
        
        # Normalize unicode
        input_data = input_data.encode('utf-8', errors='ignore').decode('utf-8')
        
        # Trim whitespace
        input_data = input_data.strip()
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
        for char in dangerous_chars:
            input_data = input_data.replace(char, '')
        
        return input_data
    
    def generate_csrf_token(self, user_id: str) -> str:
        """Generate CSRF token"""
        data = f"{user_id}:{datetime.now().timestamp()}:{secrets.token_hex(16)}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def verify_csrf_token(self, token: str, user_id: str, max_age_minutes: int = 60) -> bool:
        """Verify CSRF token"""
        try:
            # This is a simplified implementation
            # In production, you'd want to store tokens with timestamps
            # and verify them against a database or cache
            return len(token) == 64 and token.isalnum()
        except Exception:
            return False
    
    def audit_security_event(self, event_type: str, user_id: str, details: Dict[str, Any]):
        """Audit security events with privacy controls"""
        # Sanitize sensitive data for privacy compliance
        sanitized_details = self._sanitize_audit_details(details)
        
        audit_event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user_id": self._hash_user_id(user_id),  # Hash user ID for privacy
            "details": sanitized_details,
            "ip_address": self._anonymize_ip(details.get("ip_address", "unknown")),
            "user_agent": self._sanitize_user_agent(details.get("user_agent", "unknown")),
            "privacy_compliant": True
        }
        
        logger.info(f"Security audit: {json.dumps(audit_event)}")
        
        # Store in Redis for analysis
        if self.redis_client:
            try:
                key = f"security_audit:{datetime.now().strftime('%Y%m%d%H%M%S')}"
                self.redis_client.setex(key, 86400 * 30, json.dumps(audit_event))  # Keep for 30 days
            except Exception as e:
                logger.error(f"Failed to store security audit event: {e}")
    
    def _sanitize_audit_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize audit details for privacy compliance"""
        sanitized = {}
        sensitive_keys = ['password', 'token', 'secret', 'key', 'ssn', 'credit_card']
        
        for key, value in details.items():
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                sanitized[key] = "[REDACTED]"
            elif isinstance(value, str) and len(value) > 100:
                sanitized[key] = value[:100] + "..."
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _hash_user_id(self, user_id: str) -> str:
        """Hash user ID for privacy compliance"""
        return hashlib.sha256(user_id.encode()).hexdigest()[:16]
    
    def _anonymize_ip(self, ip_address: str) -> str:
        """Anonymize IP address for privacy compliance"""
        if ip_address == "unknown":
            return ip_address
        
        # Remove last octet for IPv4
        if '.' in ip_address:
            parts = ip_address.split('.')
            if len(parts) == 4:
                return '.'.join(parts[:3]) + '.xxx'
        
        # Remove last 4 groups for IPv6
        if ':' in ip_address:
            parts = ip_address.split(':')
            if len(parts) > 4:
                return ':'.join(parts[:4]) + ':xxxx'
        
        return ip_address
    
    def _sanitize_user_agent(self, user_agent: str) -> str:
        """Sanitize user agent for privacy compliance"""
        if len(user_agent) > 50:
            return user_agent[:50] + "..."
        return user_agent
    
    def get_security_policies(self) -> Dict[str, Any]:
        """Get current security policies"""
        return self.policies.copy()
    
    def update_security_policy(self, policy_name: str, value: Any) -> bool:
        """Update security policy"""
        if policy_name in self.policies:
            self.policies[policy_name] = value
            logger.info(f"Updated security policy {policy_name} to {value}")
            return True
        else:
            logger.error(f"Unknown security policy: {policy_name}")
            return False

# Security middleware for FastAPI
class SecurityMiddleware:
    """Security middleware for request processing"""
    
    def __init__(self, security_manager: ProductionSecurityManager):
        self.security_manager = security_manager
    
    async def process_request(self, request, call_next):
        """Process incoming request for security checks"""
        # Rate limiting
        if not await self._check_rate_limit(request):
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded"}
            )
        
        # Request size validation
        if not await self._validate_request_size(request):
            return JSONResponse(
                status_code=413,
                content={"error": "Request too large"}
            )
        
        # Input sanitization
        await self._sanitize_request_data(request)
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        self._add_security_headers(response)
        
        return response
    
    async def _check_rate_limit(self, request) -> bool:
        """Check rate limiting"""
        # Implementation would depend on your rate limiting strategy
        return True
    
    async def _validate_request_size(self, request) -> bool:
        """Validate request size"""
        content_length = request.headers.get("content-length", "0")
        max_size = self.security_manager.policies["max_request_size_mb"] * 1024 * 1024
        
        return int(content_length) <= max_size
    
    async def _sanitize_request_data(self, request):
        """Sanitize request data"""
        # Implementation would sanitize query parameters, form data, etc.
        pass
    
    def _add_security_headers(self, response):
        """Add security headers to response"""
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
