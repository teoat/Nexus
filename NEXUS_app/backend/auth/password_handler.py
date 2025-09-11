#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🔒 Password Handler for Nexus Platform
Secure password hashing, validation, and management
"""

import secrets
import logging
import re
from typing import Dict, Any, Tuple
from datetime import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import bcrypt

logger = logging.getLogger(__name__)

class PasswordHandler:
    """Secure password management with bcrypt and PBKDF2"""
    
    def __init__(self):
        self.min_length = 12
        self.require_uppercase = True
        self.require_lowercase = True
        self.require_numbers = True
        self.require_symbols = True
        self.bcrypt_rounds = 12
    
    def hash_password(self, password: str) -> Tuple[str, str]:
        """Hash password with salt using bcrypt"""
        try:
            # Generate salt
            salt = bcrypt.gensalt(rounds=self.bcrypt_rounds)
            
            # Hash password
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            
            return hashed.decode('utf-8'), salt.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise ValueError("Failed to hash password")
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength"""
        issues = []
        score = 0
        
        # Length check
        if len(password) < self.min_length:
            issues.append(f"Password must be at least {self.min_length} characters long")
        else:
            score += 1
        
        # Character type checks
        if self.require_uppercase and not any(c.isupper() for c in password):
            issues.append("Password must contain at least one uppercase letter")
        else:
            score += 1
        
        if self.require_lowercase and not any(c.islower() for c in password):
            issues.append("Password must contain at least one lowercase letter")
        else:
            score += 1
        
        if self.require_numbers and not any(c.isdigit() for c in password):
            issues.append("Password must contain at least one number")
        else:
            score += 1
        
        if self.require_symbols and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        else:
            score += 1
        
        # Common password check
        common_passwords = [
            "password", "123456", "123456789", "qwerty", "abc123",
            "password123", "admin", "letmein", "welcome", "monkey",
            "dragon", "master", "hello", "login", "princess"
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
        
        # Dictionary word check
        if self._contains_dictionary_word(password):
            issues.append("Password contains dictionary words")
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
    
    def _contains_dictionary_word(self, password: str) -> bool:
        """Check if password contains dictionary words"""
        # Simple dictionary check - in production, use a proper dictionary
        dictionary_words = [
            "password", "admin", "user", "login", "welcome", "hello",
        ]
        
        password_lower = password.lower()
        for word in dictionary_words:
            if word in password_lower:
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
    
    def generate_secure_password(self, length: int = 16) -> str:
        """Generate a secure random password"""
        if length < 8:
            length = 8
        
        # Character sets
        lowercase = "abcdefghijklmnopqrstuvwxyz"
        uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        numbers = "0123456789"
        symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Ensure at least one character from each set
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(numbers),
            secrets.choice(symbols)
        ]
        
        # Fill remaining length
        all_chars = lowercase + uppercase + numbers + symbols
        for _ in range(length - 4):
            password.append(secrets.choice(all_chars))
        
        # Shuffle the password
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)
    
    def check_password_history(self, password: str, password_history: list) -> bool:
        """Check if password was used recently"""
        for old_hash in password_history:
            if self.verify_password(password, old_hash):
                return False  # Password was used before
        return True
    
    def get_password_requirements(self) -> Dict[str, Any]:
        """Get password requirements"""
        return {
            "min_length": self.min_length,
            "require_uppercase": self.require_uppercase,
            "require_lowercase": self.require_lowercase,
            "require_numbers": self.require_numbers,
            "require_symbols": self.require_symbols,
            "bcrypt_rounds": self.bcrypt_rounds
        }
    
    def update_password_requirements(self, **kwargs) -> bool:
        """Update password requirements"""
        try:
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
                else:
                    logger.warning(f"Unknown password requirement: {key}")
            return True
        except Exception as e:
            logger.error(f"Error updating password requirements: {e}")
            return False

# Global password handler instance
password_handler = PasswordHandler()

# Convenience functions
def hash_password(password: str) -> Tuple[str, str]:
    """Hash password"""
    return password_handler.hash_password(password)

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password"""
    return password_handler.verify_password(password, hashed_password)

def validate_password_strength(password: str) -> Dict[str, Any]:
    """Validate password strength"""
    return password_handler.validate_password_strength(password)

def generate_secure_password(length: int = 16) -> str:
    """Generate secure password"""
    return password_handler.generate_secure_password(length)