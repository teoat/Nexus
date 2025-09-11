#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🔐 JWT Handler for Nexus Platform
Secure JWT token generation, validation, and management
"""

import jwt
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

logger = logging.getLogger(__name__)

class JWTHandler:
    """JWT token management with security best practices"""
    
    def __init__(self, secret_key: str = None, algorithm: str = "HS256"):
        """
          Init  
        
        
        Args:
            secret_key: Description of secret_key
            algorithm: Description of algorithm
    
        Example:
            TBD: Add usage example
        """
        self.secret_key = secret_key or os.getenv("JWT_SECRET_KEY", self._generate_secret_key())
        self.algorithm = algorithm
        self.access_token_expire_minutes = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.refresh_token_expire_days = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    def _generate_secret_key(self) -> str:
        """Generate a secure secret key"""
        return secrets.token_urlsafe(32)
    
    def create_access_token(self, user_id: str, additional_claims: Dict[str, Any] = None) -> str:
        """Create JWT access token"""
        now = datetime.utcnow()
        payload = {
            "user_id": user_id,
            "type": "access",
            "iat": now,
            "exp": now + timedelta(minutes=self.access_token_expire_minutes),
            "iss": "nexus-platform",
            "aud": "nexus-users",
            "jti": secrets.token_urlsafe(32)  # JWT ID for token tracking
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        # Add security headers
        headers = {
            "alg": self.algorithm,
            "typ": "JWT"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm, headers=headers)
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create JWT refresh token"""
        now = datetime.utcnow()
        payload = {
            "user_id": user_id,
            "type": "refresh",
            "iat": now,
            "exp": now + timedelta(days=self.refresh_token_expire_days),
            "iss": "nexus-platform",
            "aud": "nexus-users",
            "jti": secrets.token_urlsafe(32)
        }
        
        headers = {
            "alg": self.algorithm,
            "typ": "JWT"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm, headers=headers)
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                audience="nexus-users",
                issuer="nexus-platform"
            )
            
            # Verify token type
            if payload.get("type") != token_type:
                raise jwt.InvalidTokenError("Invalid token type")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {e}")
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """Create new access token from refresh token"""
        try:
            payload = self.verify_token(refresh_token, "refresh")
            user_id = payload.get("user_id")
            
            if not user_id:
                raise ValueError("Invalid refresh token: missing user_id")
            
            return self.create_access_token(user_id)
            
        except Exception as e:
            raise ValueError(f"Failed to refresh token: {e}")
    
    def decode_token_without_verification(self, token: str) -> Dict[str, Any]:
        """Decode token without verification (for debugging)"""
        try:
            return jwt.decode(token, options={"verify_signature": False})
        except Exception as e:
            raise ValueError(f"Failed to decode token: {e}")
    
    def get_token_expiry(self, token: str) -> Optional[datetime]:
        """Get token expiry time"""
        try:
            payload = self.decode_token_without_verification(token)
            exp_timestamp = payload.get("exp")
            if exp_timestamp:
                return datetime.fromtimestamp(exp_timestamp)
            return None
        except Exception:
            return None
    
    def is_token_expired(self, token: str) -> bool:
        """Check if token is expired"""
        try:
            self.verify_token(token)
            return False
        except ValueError as e:
            if "expired" in str(e).lower():
                return True
            return False
    
    def revoke_token(self, token: str) -> bool:
        """Revoke token (add to blacklist)"""
        try:
            # In a production system, you would add the token to a blacklist
            # stored in Redis or database
            payload = self.decode_token_without_verification(token)
            jti = payload.get("jti")
            
            if jti:
                # Add to blacklist (implement based on your storage solution)
                logger.info(f"Token revoked: {jti}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to revoke token: {e}")
            return False
    
    def validate_token_strength(self, token: str) -> Dict[str, Any]:
        """Validate token security strength"""
        issues = []
        
        try:
            payload = self.decode_token_without_verification(token)
            
            # Check token age
            iat = payload.get("iat")
            if iat:
                issued_at = datetime.fromtimestamp(iat)
                age_hours = (datetime.utcnow() - issued_at).total_seconds() / 3600
                if age_hours > 24:
                    issues.append("Token is older than 24 hours")
            
            # Check expiration
            exp = payload.get("exp")
            if exp:
                expires_at = datetime.fromtimestamp(exp)
                time_to_expiry = (expires_at - datetime.utcnow()).total_seconds()
                if time_to_expiry < 300:  # Less than 5 minutes
                    issues.append("Token expires soon")
            
            # Check required claims
            required_claims = ["user_id", "iat", "exp", "iss", "aud", "jti"]
            missing_claims = [claim for claim in required_claims if claim not in payload]
            if missing_claims:
                issues.append(f"Missing required claims: {missing_claims}")
            
            return {
                "valid": len(issues) == 0,
                "issues": issues,
                "payload": payload
            }
            
        except Exception as e:
            return {
                "valid": False,
                "issues": [f"Token validation error: {e}"],
                "payload": None
            }

# Global JWT handler instance
jwt_handler = JWTHandler()

# Convenience functions
def create_access_token(user_id: str, additional_claims: Dict[str, Any] = None) -> str:
    """Create access token"""
    return jwt_handler.create_access_token(user_id, additional_claims)

def create_refresh_token(user_id: str) -> str:
    """Create refresh token"""
    return jwt_handler.create_refresh_token(user_id)

def verify_access_token(token: str) -> Dict[str, Any]:
    """Verify access token"""
    return jwt_handler.verify_token(token, "access")

def verify_refresh_token(token: str) -> Dict[str, Any]:
    """Verify refresh token"""
    return jwt_handler.verify_token(token, "refresh")

def refresh_access_token(refresh_token: str) -> str:
    """Refresh access token"""
    return jwt_handler.refresh_access_token(refresh_token)