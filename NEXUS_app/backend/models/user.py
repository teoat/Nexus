"""
user Module

User

This module provides functionality for user.

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
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum as SQLEnum, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from core.database import Base

class UserRole(str, enum.Enum):
    """
    UserRole Class
    
    User Role
    
    Attributes:
        TBD: Add attribute descriptions
    
    Methods:
        TBD: Add method descriptions
    
    Example:
        TBD: Add usage example
    """
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"
    VIEWER = "viewer"

class UserStatus(str, enum.Enum):
    """
    UserStatus Class
    
    User Status
    
    Attributes:
        TBD: Add attribute descriptions
    
    Methods:
        TBD: Add method descriptions
    
    Example:
        TBD: Add usage example
    """
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"

class User(Base):
    """
    User Class
    
    User
    
    Attributes:
        TBD: Add attribute descriptions
    
    Methods:
        TBD: Add method descriptions
    
    Example:
        TBD: Add usage example
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    status = Column(SQLEnum(UserStatus), default=UserStatus.PENDING, nullable=False)
    
    # Profile information
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    timezone = Column(String(50), default="UTC", nullable=False)
    language = Column(String(10), default="en", nullable=False)
    
    # Security settings
    is_email_verified = Column(Boolean, default=False, nullable=False)
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_secret = Column(String(32), nullable=True)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    
    # Notification preferences
    notifications_enabled = Column(Boolean, default=True, nullable=False)
    email_notifications = Column(Boolean, default=True, nullable=False)
    sms_notifications = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    activities = relationship("UserActivity", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_users_email', 'email'),
        Index('idx_users_role', 'role'),
        Index('idx_users_status', 'status'),
        Index('idx_users_created_at', 'created_at'),
    )
    
    @property
    def full_name(self) -> str:
        """
        Full Name
        
        
        Args:
    
        Returns:
            str: Description of return value
    
        Example:
            TBD: Add usage example
        """
        return f"{self.first_name} {self.last_name}"
    
    @property
    def is_active(self) -> bool:
        """
        Check if active
        
        
        Args:
    
        Returns:
            bool: Description of return value
    
        Example:
            TBD: Add usage example
        """
        return self.status == UserStatus.ACTIVE
    
    @property
    def is_locked(self) -> bool:
        """
        Check if locked
        
        
        Args:
    
        Returns:
            bool: Description of return value
    
        Example:
            TBD: Add usage example
        """
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until
    
    def __repr__(self):
        """
          Repr  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        return f"<User(id={self.id}, email='{self.email}', name='{self.full_name}')>"

class UserSession(Base):
    """
    UserSession Class
    
    User Session
    
    Attributes:
        TBD: Add attribute descriptions
    
    Methods:
        TBD: Add method descriptions
    
    Example:
        TBD: Add usage example
    """
    __tablename__ = "user_sessions"
    
    id = Column(String(255), primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    last_activity = Column(DateTime, default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    ip_address = Column(String(45), nullable=False)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    # Indexes
    __table_args__ = (
        Index('idx_sessions_user_id', 'user_id'),
        Index('idx_sessions_expires_at', 'expires_at'),
        Index('idx_sessions_is_active', 'is_active'),
    )
    
    @property
    def is_expired(self) -> bool:
        """
        Check if expired
        
        
        Args:
    
        Returns:
            bool: Description of return value
    
        Example:
            TBD: Add usage example
        """
        return datetime.utcnow() > self.expires_at
    
    def __repr__(self):
        """
          Repr  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        return f"<UserSession(id='{self.id}', user_id={self.user_id}, active={self.is_active})>"

class UserActivity(Base):
    """
    UserActivity Class
    
    User Activity
    
    Attributes:
        TBD: Add attribute descriptions
    
    Methods:
        TBD: Add method descriptions
    
    Example:
        TBD: Add usage example
    """
    __tablename__ = "user_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(100), nullable=False)
    resource = Column(String(100), nullable=True)
    resource_id = Column(String(100), nullable=True)
    details = Column(Text, nullable=True)  # JSON string
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="activities")
    
    # Indexes
    __table_args__ = (
        Index('idx_activities_user_id', 'user_id'),
        Index('idx_activities_action', 'action'),
        Index('idx_activities_created_at', 'created_at'),
        Index('idx_activities_resource', 'resource'),
    )
    
    def __repr__(self):
        """
          Repr  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        return f"<UserActivity(id={self.id}, user_id={self.user_id}, action='{self.action}')>"

class APIKey(Base):
    """
    APIKey Class
    
    Apikey
    
    Attributes:
        TBD: Add attribute descriptions
    
    Methods:
        TBD: Add method descriptions
    
    Example:
        TBD: Add usage example
    """
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    key_hash = Column(String(255), nullable=False, unique=True)
    permissions = Column(Text, nullable=True)  # JSON string of permissions
    last_used = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    # Indexes
    __table_args__ = (
        Index('idx_api_keys_user_id', 'user_id'),
        Index('idx_api_keys_key_hash', 'key_hash'),
        Index('idx_api_keys_is_active', 'is_active'),
        Index('idx_api_keys_expires_at', 'expires_at'),
    )
    
    @property
    def is_expired(self) -> bool:
        """
        Check if expired
        
        
        Args:
    
        Returns:
            bool: Description of return value
    
        Example:
            TBD: Add usage example
        """
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def __repr__(self):
        """
          Repr  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        return f"<APIKey(id={self.id}, user_id={self.user_id}, name='{self.name}')>"

class PasswordResetToken(Base):
    """
    PasswordResetToken Class
    
    Password Reset Token
    
    Attributes:
        TBD: Add attribute descriptions
    
    Methods:
        TBD: Add method descriptions
    
    Example:
        TBD: Add usage example
    """
    __tablename__ = "password_reset_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_reset_tokens_user_id', 'user_id'),
        Index('idx_reset_tokens_token', 'token'),
        Index('idx_reset_tokens_expires_at', 'expires_at'),
    )
    
    @property
    def is_expired(self) -> bool:
        """
        Check if expired
        
        
        Args:
    
        Returns:
            bool: Description of return value
    
        Example:
            TBD: Add usage example
        """
        return datetime.utcnow() > self.expires_at
    
    def __repr__(self):
        """
          Repr  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        return f"<PasswordResetToken(id={self.id}, user_id={self.user_id}, used={self.used})>"

class EmailVerificationToken(Base):
    """
    EmailVerificationToken Class
    
    Email Verification Token
    
    Attributes:
        TBD: Add attribute descriptions
    
    Methods:
        TBD: Add method descriptions
    
    Example:
        TBD: Add usage example
    """
    __tablename__ = "email_verification_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_verification_tokens_user_id', 'user_id'),
        Index('idx_verification_tokens_token', 'token'),
        Index('idx_verification_tokens_expires_at', 'expires_at'),
    )
    
    @property
    def is_expired(self) -> bool:
        """
        Check if expired
        
        
        Args:
    
        Returns:
            bool: Description of return value
    
        Example:
            TBD: Add usage example
        """
        return datetime.utcnow() > self.expires_at
    
    def __repr__(self):
        """
          Repr  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        return f"<EmailVerificationToken(id={self.id}, user_id={self.user_id}, used={self.used})>"
