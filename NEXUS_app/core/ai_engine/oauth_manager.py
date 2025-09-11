#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🔐 Frenly AI OAuth 2.0 Manager
OAuth 2.0 integration for external services
"""

import asyncio
import logging
import time
import json
import secrets
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import aiohttp
import redis
from backend.config import get_config

logger = logging.getLogger(__name__)

class GrantType(Enum):
    """OAuth 2.0 grant types"""
    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    REFRESH_TOKEN = "refresh_token"
    PASSWORD = "password"
    IMPLICIT = "implicit"

class TokenType(Enum):
    """Token types"""
    BEARER = "Bearer"
    MAC = "MAC"

class Scope(Enum):
    """OAuth 2.0 scopes"""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    USER = "user"
    AGENT = "agent"
    WEBHOOK = "webhook"

@dataclass
class OAuthClient:
    """OAuth 2.0 client definition"""
    client_id: str
    client_secret: str
    name: str
    description: str
    redirect_uris: List[str]
    scopes: List[Scope]
    grant_types: List[GrantType]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    enabled: bool = True
    access_token_lifetime: int = 3600  # 1 hour
    refresh_token_lifetime: int = 86400 * 30  # 30 days

@dataclass
class OAuthToken:
    """OAuth 2.0 token definition"""
    access_token: str
    token_type: TokenType = TokenType.BEARER
    expires_in: int = 3600
    refresh_token: Optional[str] = None
    scope: List[Scope] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    expires_at: str = field(default_factory=lambda: (datetime.now() + timedelta(hours=1)).isoformat())

@dataclass
class OAuthAuthorization:
    """OAuth 2.0 authorization code definition"""
    code: str
    client_id: str
    user_id: Optional[str]
    redirect_uri: str
    scopes: List[Scope]
    expires_at: str
    used: bool = False

@dataclass
class OAuthSession:
    """OAuth 2.0 session definition"""
    session_id: str
    client_id: str
    user_id: Optional[str]
    state: str
    code_challenge: Optional[str] = None
    code_challenge_method: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    expires_at: str = field(default_factory=lambda: (datetime.now() + timedelta(minutes=10)).isoformat())

class OAuthManager:
    """OAuth 2.0 manager for Frenly AI"""
    
    def __init__(self):
        """
          Init  
        
        
        Args:
    
        Example:
            TBD: Add usage example
        """
        self.config = get_config()
        self.redis_client = redis.Redis.from_url(self.config.redis_url)
        self.running = False
        
        # OAuth storage
        self.clients: Dict[str, OAuthClient] = {}
        self.tokens: Dict[str, OAuthToken] = {}
        self.authorizations: Dict[str, OAuthAuthorization] = {}
        self.sessions: Dict[str, OAuthSession] = {}
        
        # Configuration
        self.authorization_code_lifetime = 600  # 10 minutes
        self.session_lifetime = 600  # 10 minutes
        self.max_tokens_per_client = 100
        
        logger.info("✅ OAuth Manager initialized")
    
    async def start(self):
        """Start the OAuth manager"""
        self.running = True
        logger.info("🚀 Starting OAuth Manager...")
        
        # Load existing data
        await self._load_oauth_data()
        
        # Start cleanup tasks
        asyncio.create_task(self._cleanup_expired_tokens())
        asyncio.create_task(self._cleanup_expired_sessions())
        
        logger.info("✅ OAuth Manager started")
    
    async def stop(self):
        """Stop the OAuth manager"""
        self.running = False
        logger.info("🛑 Stopping OAuth Manager...")
        
        # Save OAuth data
        await self._save_oauth_data()
        
        logger.info("✅ OAuth Manager stopped")
    
    async def create_client(
        self,
        name: str,
        description: str,
        redirect_uris: List[str],
        scopes: List[Scope],
        grant_types: List[GrantType],
        access_token_lifetime: int = 3600,
        refresh_token_lifetime: int = 86400 * 30
    ) -> OAuthClient:
        """Create a new OAuth client"""
        try:
            client_id = self._generate_client_id()
            client_secret = self._generate_client_secret()
            
            client = OAuthClient(
                client_id=client_id,
                client_secret=client_secret,
                name=name,
                description=description,
                redirect_uris=redirect_uris,
                scopes=scopes,
                grant_types=grant_types,
                access_token_lifetime=access_token_lifetime,
                refresh_token_lifetime=refresh_token_lifetime
            )
            
            self.clients[client_id] = client
            
            logger.info(f"OAuth client created: {client_id}")
            return client
            
        except Exception as e:
            logger.error(f"❌ Error creating OAuth client: {e}")
            raise
    
    async def get_client(self, client_id: str) -> Optional[OAuthClient]:
        """Get OAuth client information"""
        return self.clients.get(client_id)
    
    async def update_client(self, client_id: str, **updates) -> bool:
        """Update OAuth client"""
        try:
            if client_id not in self.clients:
                logger.warning(f"OAuth client not found: {client_id}")
                return False
            
            client = self.clients[client_id]
            
            # Update fields
            for key, value in updates.items():
                if hasattr(client, key):
                    setattr(client, key, value)
            
            client.updated_at = datetime.now().isoformat()
            
            logger.info(f"OAuth client updated: {client_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating OAuth client {client_id}: {e}")
            return False
    
    async def delete_client(self, client_id: str) -> bool:
        """Delete OAuth client"""
        try:
            if client_id not in self.clients:
                logger.warning(f"OAuth client not found: {client_id}")
                return False
            
            # Revoke all tokens for this client
            await self._revoke_client_tokens(client_id)
            
            # Delete client
            del self.clients[client_id]
            
            logger.info(f"OAuth client deleted: {client_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting OAuth client {client_id}: {e}")
            return False
    
    async def authorize_client(
        self,
        client_id: str,
        redirect_uri: str,
        scopes: List[Scope],
        state: str,
        user_id: Optional[str] = None,
        code_challenge: Optional[str] = None,
        code_challenge_method: Optional[str] = None
    ) -> str:
        """Generate authorization code"""
        try:
            # Validate client
            client = await self.get_client(client_id)
            if not client or not client.enabled:
                raise ValueError("Invalid client")
            
            # Validate redirect URI
            if redirect_uri not in client.redirect_uris:
                raise ValueError("Invalid redirect URI")
            
            # Validate scopes
            if not all(scope in client.scopes for scope in scopes):
                raise ValueError("Invalid scopes")
            
            # Generate authorization code
            code = self._generate_authorization_code()
            
            # Create authorization
            authorization = OAuthAuthorization(
                code=code,
                client_id=client_id,
                user_id=user_id,
                redirect_uri=redirect_uri,
                scopes=scopes,
                expires_at=(datetime.now() + timedelta(seconds=self.authorization_code_lifetime)).isoformat()
            )
            
            self.authorizations[code] = authorization
            
            # Create session
            session_id = self._generate_session_id()
            session = OAuthSession(
                session_id=session_id,
                client_id=client_id,
                user_id=user_id,
                state=state,
                code_challenge=code_challenge,
                code_challenge_method=code_challenge_method
            )
            
            self.sessions[session_id] = session
            
            logger.info(f"Authorization code generated: {code}")
            return code
            
        except Exception as e:
            logger.error(f"❌ Error generating authorization code: {e}")
            raise
    
    async def exchange_code_for_token(
        self,
        code: str,
        client_id: str,
        client_secret: str,
        redirect_uri: str
    ) -> OAuthToken:
        """Exchange authorization code for access token"""
        try:
            # Validate client
            client = await self.get_client(client_id)
            if not client or not client.enabled:
                raise ValueError("Invalid client")
            
            if client.client_secret != client_secret:
                raise ValueError("Invalid client secret")
            
            # Validate authorization code
            if code not in self.authorizations:
                raise ValueError("Invalid authorization code")
            
            authorization = self.authorizations[code]
            
            if authorization.client_id != client_id:
                raise ValueError("Invalid client for authorization code")
            
            if authorization.redirect_uri != redirect_uri:
                raise ValueError("Invalid redirect URI")
            
            if authorization.used:
                raise ValueError("Authorization code already used")
            
            if datetime.fromisoformat(authorization.expires_at) < datetime.now():
                raise ValueError("Authorization code expired")
            
            # Mark authorization as used
            authorization.used = True
            
            # Generate access token
            access_token = self._generate_access_token()
            refresh_token = self._generate_refresh_token()
            
            # Create token
            token = OAuthToken(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=client.access_token_lifetime,
                scope=authorization.scopes,
                expires_at=(datetime.now() + timedelta(seconds=client.access_token_lifetime)).isoformat()
            )
            
            self.tokens[access_token] = token
            
            logger.info(f"Access token generated: {access_token[:8]}...")
            return token
            
        except Exception as e:
            logger.error(f"❌ Error exchanging code for token: {e}")
            raise
    
    async def refresh_token(self, refresh_token: str) -> OAuthToken:
        """Refresh access token using refresh token"""
        try:
            # Find token by refresh token
            token = None
            for t in self.tokens.values():
                if t.refresh_token == refresh_token:
                    token = t
                    break
            
            if not token:
                raise ValueError("Invalid refresh token")
            
            # Check if refresh token is expired
            if datetime.fromisoformat(token.expires_at) < datetime.now():
                raise ValueError("Refresh token expired")
            
            # Generate new access token
            new_access_token = self._generate_access_token()
            new_refresh_token = self._generate_refresh_token()
            
            # Create new token
            new_token = OAuthToken(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                expires_in=token.expires_in,
                scope=token.scope,
                expires_at=(datetime.now() + timedelta(seconds=token.expires_in)).isoformat()
            )
            
            # Remove old token
            del self.tokens[token.access_token]
            
            # Add new token
            self.tokens[new_access_token] = new_token
            
            logger.info(f"Token refreshed: {new_access_token[:8]}...")
            return new_token
            
        except Exception as e:
            logger.error(f"❌ Error refreshing token: {e}")
            raise
    
    async def revoke_token(self, token: str) -> bool:
        """Revoke an access token"""
        try:
            if token in self.tokens:
                del self.tokens[token]
                logger.info(f"Token revoked: {token[:8]}...")
                return True
            
            logger.warning(f"Token not found: {token[:8]}...")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error revoking token: {e}")
            return False
    
    async def validate_token(self, token: str) -> Optional[OAuthToken]:
        """Validate an access token"""
        try:
            if token not in self.tokens:
                return None
            
            token_obj = self.tokens[token]
            
            # Check if token is expired
            if datetime.fromisoformat(token_obj.expires_at) < datetime.now():
                del self.tokens[token]
                return None
            
            return token_obj
            
        except Exception as e:
            logger.error(f"❌ Error validating token: {e}")
            return None
    
    async def get_token_info(self, token: str) -> Optional[Dict[str, Any]]:
        """Get token information"""
        try:
            token_obj = await self.validate_token(token)
            if not token_obj:
                return None
            
            return {
                "access_token": token_obj.access_token,
                "token_type": token_obj.token_type.value,
                "expires_in": token_obj.expires_in,
                "scope": [s.value for s in token_obj.scope],
                "created_at": token_obj.created_at,
                "expires_at": token_obj.expires_at
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting token info: {e}")
            return None
    
    async def get_oauth_analytics(self) -> Dict[str, Any]:
        """Get OAuth system analytics"""
        try:
            total_clients = len(self.clients)
            active_clients = len([c for c in self.clients.values() if c.enabled])
            total_tokens = len(self.tokens)
            active_tokens = len([t for t in self.tokens.values() if datetime.fromisoformat(t.expires_at) > datetime.now()])
            
            # Client statistics
            client_stats = {}
            for client in self.clients.values():
                client_tokens = len([t for t in self.tokens.values() if t.access_token.startswith(client.client_id[:8])])
                client_stats[client.client_id] = {
                    "name": client.name,
                    "tokens": client_tokens,
                    "enabled": client.enabled
                }
            
            # Scope distribution
            scope_distribution = {}
            for token in self.tokens.values():
                for scope in token.scope:
                    scope_distribution[scope.value] = scope_distribution.get(scope.value, 0) + 1
            
            return {
                "total_clients": total_clients,
                "active_clients": active_clients,
                "total_tokens": total_tokens,
                "active_tokens": active_tokens,
                "client_stats": client_stats,
                "scope_distribution": scope_distribution,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting OAuth analytics: {e}")
            return {"error": str(e)}
    
    def _generate_client_id(self) -> str:
        """Generate OAuth client ID"""
        return f"client_{secrets.token_urlsafe(16)}"
    
    def _generate_client_secret(self) -> str:
        """Generate OAuth client secret"""
        return secrets.token_urlsafe(32)
    
    def _generate_authorization_code(self) -> str:
        """Generate authorization code"""
        return secrets.token_urlsafe(32)
    
    def _generate_access_token(self) -> str:
        """Generate access token"""
        return f"access_{secrets.token_urlsafe(32)}"
    
    def _generate_refresh_token(self) -> str:
        """Generate refresh token"""
        return f"refresh_{secrets.token_urlsafe(32)}"
    
    def _generate_session_id(self) -> str:
        """Generate session ID"""
        return f"session_{secrets.token_urlsafe(16)}"
    
    async def _revoke_client_tokens(self, client_id: str):
        """Revoke all tokens for a client"""
        try:
            tokens_to_remove = []
            for token, token_obj in self.tokens.items():
                # This is a simplified check - in practice, you'd need to track client_id in tokens
                if token.startswith(client_id[:8]):
                    tokens_to_remove.append(token)
            
            for token in tokens_to_remove:
                del self.tokens[token]
            
            logger.info(f"Revoked {len(tokens_to_remove)} tokens for client {client_id}")
            
        except Exception as e:
            logger.error(f"❌ Error revoking client tokens: {e}")
    
    async def _cleanup_expired_tokens(self):
        """Clean up expired tokens"""
        while self.running:
            try:
                now = datetime.now()
                expired_tokens = []
                
                for token, token_obj in self.tokens.items():
                    if datetime.fromisoformat(token_obj.expires_at) < now:
                        expired_tokens.append(token)
                
                for token in expired_tokens:
                    del self.tokens[token]
                
                if expired_tokens:
                    logger.info(f"Cleaned up {len(expired_tokens)} expired tokens")
                
                await asyncio.sleep(3600)  # Check every hour
                
            except Exception as e:
                logger.error(f"❌ Error cleaning up expired tokens: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        while self.running:
            try:
                now = datetime.now()
                expired_sessions = []
                
                for session_id, session in self.sessions.items():
                    if datetime.fromisoformat(session.expires_at) < now:
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    del self.sessions[session_id]
                
                if expired_sessions:
                    logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Error cleaning up expired sessions: {e}")
                await asyncio.sleep(60)
    
    async def _load_oauth_data(self):
        """Load OAuth data from storage"""
        try:
            if self.redis_client:
                # Load clients
                clients_data = self.redis_client.get("frenly_oauth_clients")
                if clients_data:
                    clients_json = json.loads(clients_data)
                    for client_id, client_data in clients_json.items():
                        client = OAuthClient(
                            client_id=client_id,
                            client_secret=client_data["client_secret"],
                            name=client_data["name"],
                            description=client_data["description"],
                            redirect_uris=client_data["redirect_uris"],
                            scopes=[Scope(s) for s in client_data["scopes"]],
                            grant_types=[GrantType(g) for g in client_data["grant_types"]],
                            created_at=client_data["created_at"],
                            updated_at=client_data["updated_at"],
                            enabled=client_data.get("enabled", True),
                            access_token_lifetime=client_data.get("access_token_lifetime", 3600),
                            refresh_token_lifetime=client_data.get("refresh_token_lifetime", 86400 * 30)
                        )
                        self.clients[client_id] = client
                
                # Load tokens
                tokens_data = self.redis_client.get("frenly_oauth_tokens")
                if tokens_data:
                    tokens_json = json.loads(tokens_data)
                    for token, token_data in tokens_json.items():
                        token_obj = OAuthToken(
                            access_token=token,
                            token_type=TokenType(token_data["token_type"]),
                            expires_in=token_data["expires_in"],
                            refresh_token=token_data.get("refresh_token"),
                            scope=[Scope(s) for s in token_data.get("scope", [])],
                            created_at=token_data["created_at"],
                            expires_at=token_data["expires_at"]
                        )
                        self.tokens[token] = token_obj
                
                logger.info(f"Loaded {len(self.clients)} clients and {len(self.tokens)} tokens")
            
        except Exception as e:
            logger.error(f"❌ Error loading OAuth data: {e}")
    
    async def _save_oauth_data(self):
        """Save OAuth data to storage"""
        try:
            if self.redis_client:
                # Save clients
                clients_data = {
                    client_id: {
                        "client_secret": client.client_secret,
                        "name": client.name,
                        "description": client.description,
                        "redirect_uris": client.redirect_uris,
                        "scopes": [s.value for s in client.scopes],
                        "grant_types": [g.value for g in client.grant_types],
                        "created_at": client.created_at,
                        "updated_at": client.updated_at,
                        "enabled": client.enabled,
                        "access_token_lifetime": client.access_token_lifetime,
                        "refresh_token_lifetime": client.refresh_token_lifetime
                    }
                    for client_id, client in self.clients.items()
                }
                self.redis_client.setex("frenly_oauth_clients", 86400, json.dumps(clients_data))
                
                # Save tokens
                tokens_data = {
                    token: {
                        "token_type": token_obj.token_type.value,
                        "expires_in": token_obj.expires_in,
                        "refresh_token": token_obj.refresh_token,
                        "scope": [s.value for s in token_obj.scope],
                        "created_at": token_obj.created_at,
                        "expires_at": token_obj.expires_at
                    }
                    for token, token_obj in self.tokens.items()
                }
                self.redis_client.setex("frenly_oauth_tokens", 86400, json.dumps(tokens_data))
            
        except Exception as e:
            logger.error(f"❌ Error saving OAuth data: {e}")

# Global OAuth manager instance
oauth_manager = OAuthManager()
