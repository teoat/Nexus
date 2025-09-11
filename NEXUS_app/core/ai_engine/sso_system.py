#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🔐 Frenly AI Single Sign-On (SSO) System
Advanced SSO capabilities for Frenly AI
"""

import asyncio
import logging
import time
import json
import hashlib
import hmac
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import redis
from backend.config import get_config

logger = logging.getLogger(__name__)

class SSOProvider(Enum):
    """SSO provider enumeration"""
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    GITHUB = "github"
    SAML = "saml"
    OIDC = "oidc"
    CUSTOM = "custom"

class SSOStatus(Enum):
    """SSO status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    EXPIRED = "expired"

class TokenType(Enum):
    """Token type enumeration"""
    ACCESS = "access"
    REFRESH = "refresh"
    ID = "id"
    AUTHORIZATION = "authorization"

class GrantType(Enum):
    """OAuth grant type enumeration"""
    AUTHORIZATION_CODE = "authorization_code"
    CLIENT_CREDENTIALS = "client_credentials"
    REFRESH_TOKEN = "refresh_token"
    PASSWORD = "password"
    IMPLICIT = "implicit"

@dataclass
class SSOProvider:
    """SSO provider definition"""
    id: str
    name: str
    provider_type: SSOProvider
    client_id: str
    client_secret: str
    redirect_uri: str
    scopes: List[str]
    status: SSOStatus
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class SSOUser:
    """SSO user definition"""
    id: str
    provider_id: str
    external_id: str
    email: str
    name: str
    avatar_url: Optional[str] = None
    profile_data: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_login: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class SSOToken:
    """SSO token definition"""
    id: str
    user_id: str
    provider_id: str
    token_type: TokenType
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: str
    scopes: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class SSOSession:
    """SSO session definition"""
    id: str
    user_id: str
    provider_id: str
    session_token: str
    expires_at: str
    ip_address: str
    user_agent: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_activity: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class SSOApplication:
    """SSO application definition"""
    id: str
    name: str
    client_id: str
    client_secret: str
    redirect_uris: List[str]
    scopes: List[str]
    status: SSOStatus
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

class SSOSystem:
    """Single Sign-On System for Frenly AI"""
    
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
        
        # SSO storage
        self.providers: Dict[str, SSOProvider] = {}
        self.users: Dict[str, SSOUser] = {}
        self.tokens: Dict[str, SSOToken] = {}
        self.sessions: Dict[str, SSOSession] = {}
        self.applications: Dict[str, SSOApplication] = {}
        
        # Configuration
        self.session_timeout = 3600  # 1 hour
        self.token_retention_days = 30
        self.max_sessions_per_user = 5
        
        # Initialize default providers
        self._initialize_default_providers()
        
        logger.info("✅ SSO System initialized")
    
    def _initialize_default_providers(self):
        """Initialize default SSO providers"""
        try:
            # Google OAuth
            google_provider = SSOProvider(
                id="google_oauth",
                name="Google OAuth",
                provider_type=SSOProvider.GOOGLE,
                client_id="",
                client_secret="",
                redirect_uri="",
                scopes=["openid", "email", "profile"],
                status=SSOStatus.INACTIVE
            )
            self.providers["google_oauth"] = google_provider
            
            # Microsoft OAuth
            microsoft_provider = SSOProvider(
                id="microsoft_oauth",
                name="Microsoft OAuth",
                provider_type=SSOProvider.MICROSOFT,
                client_id="",
                client_secret="",
                redirect_uri="",
                scopes=["openid", "email", "profile"],
                status=SSOStatus.INACTIVE
            )
            self.providers["microsoft_oauth"] = microsoft_provider
            
            # GitHub OAuth
            github_provider = SSOProvider(
                id="github_oauth",
                name="GitHub OAuth",
                provider_type=SSOProvider.GITHUB,
                client_id="",
                client_secret="",
                redirect_uri="",
                scopes=["user:email", "read:user"],
                status=SSOStatus.INACTIVE
            )
            self.providers["github_oauth"] = github_provider
            
            logger.info(f"Initialized {len(self.providers)} SSO providers")
            
        except Exception as e:
            logger.error(f"❌ Error initializing default providers: {e}")
    
    async def start(self):
        """Start the SSO system"""
        self.running = True
        logger.info("🚀 Starting SSO System...")
        
        # Load existing data
        await self._load_sso_data()
        
        # Start background tasks
        asyncio.create_task(self._cleanup_old_data())
        asyncio.create_task(self._session_cleanup())
        asyncio.create_task(self._token_refresh_loop())
        
        logger.info("✅ SSO System started")
    
    async def stop(self):
        """Stop the SSO system"""
        self.running = False
        logger.info("🛑 Stopping SSO System...")
        
        # Save SSO data
        await self._save_sso_data()
        
        logger.info("✅ SSO System stopped")
    
    async def create_provider(
        self,
        name: str,
        provider_type: SSOProvider,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        scopes: List[str]
    ) -> str:
        """Create a new SSO provider"""
        try:
            provider_id = f"provider_{int(time.time())}_{hashlib.md5(name.encode()).hexdigest()[:8]}"
            
            provider = SSOProvider(
                id=provider_id,
                name=name,
                provider_type=provider_type,
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scopes=scopes,
                status=SSOStatus.ACTIVE
            )
            
            self.providers[provider_id] = provider
            
            logger.info(f"SSO provider created: {provider_id}")
            return provider_id
            
        except Exception as e:
            logger.error(f"❌ Error creating SSO provider: {e}")
            raise
    
    async def get_provider(self, provider_id: str) -> Optional[SSOProvider]:
        """Get SSO provider information"""
        return self.providers.get(provider_id)
    
    async def list_providers(self, status: Optional[SSOStatus] = None) -> List[SSOProvider]:
        """List SSO providers"""
        providers = list(self.providers.values())
        
        if status:
            providers = [p for p in providers if p.status == status]
        
        return providers
    
    async def update_provider(self, provider_id: str, **updates) -> bool:
        """Update SSO provider"""
        try:
            if provider_id not in self.providers:
                logger.warning(f"SSO provider not found: {provider_id}")
                return False
            
            provider = self.providers[provider_id]
            
            # Update fields
            for key, value in updates.items():
                if hasattr(provider, key):
                    setattr(provider, key, value)
            
            provider.updated_at = datetime.now().isoformat()
            
            logger.info(f"SSO provider updated: {provider_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating SSO provider {provider_id}: {e}")
            return False
    
    async def create_application(
        self,
        name: str,
        redirect_uris: List[str],
        scopes: List[str]
    ) -> Tuple[str, str]:
        """Create a new SSO application"""
        try:
            app_id = f"app_{int(time.time())}_{hashlib.md5(name.encode()).hexdigest()[:8]}"
            client_id = f"client_{hashlib.md5(f'{app_id}_{time.time()}'.encode()).hexdigest()[:16]}"
            client_secret = self._generate_client_secret()
            
            application = SSOApplication(
                id=app_id,
                name=name,
                client_id=client_id,
                client_secret=client_secret,
                redirect_uris=redirect_uris,
                scopes=scopes,
                status=SSOStatus.ACTIVE
            )
            
            self.applications[app_id] = application
            
            logger.info(f"SSO application created: {app_id}")
            return app_id, client_id
            
        except Exception as e:
            logger.error(f"❌ Error creating SSO application: {e}")
            raise
    
    async def get_application(self, app_id: str) -> Optional[SSOApplication]:
        """Get SSO application information"""
        return self.applications.get(app_id)
    
    async def get_application_by_client_id(self, client_id: str) -> Optional[SSOApplication]:
        """Get SSO application by client ID"""
        for app in self.applications.values():
            if app.client_id == client_id:
                return app
        return None
    
    async def initiate_sso(
        self,
        provider_id: str,
        app_id: str,
        state: str,
        redirect_uri: str
    ) -> str:
        """Initiate SSO flow"""
        try:
            if provider_id not in self.providers:
                raise ValueError("SSO provider not found")
            
            provider = self.providers[provider_id]
            
            if provider.status != SSOStatus.ACTIVE:
                raise ValueError("SSO provider is not active")
            
            if app_id not in self.applications:
                raise ValueError("SSO application not found")
            
            app = self.applications[app_id]
            
            if redirect_uri not in app.redirect_uris:
                raise ValueError("Invalid redirect URI")
            
            # Generate authorization URL
            auth_url = await self._generate_authorization_url(provider, app, state, redirect_uri)
            
            logger.info(f"SSO initiated: {provider_id} -> {app_id}")
            return auth_url
            
        except Exception as e:
            logger.error(f"❌ Error initiating SSO: {e}")
            raise
    
    async def handle_sso_callback(
        self,
        provider_id: str,
        code: str,
        state: str,
        app_id: str
    ) -> str:
        """Handle SSO callback"""
        try:
            if provider_id not in self.providers:
                raise ValueError("SSO provider not found")
            
            provider = self.providers[provider_id]
            
            if app_id not in self.applications:
                raise ValueError("SSO application not found")
            
            app = self.applications[app_id]
            
            # Exchange code for tokens
            tokens = await self._exchange_code_for_tokens(provider, code, app)
            
            # Get user information
            user_info = await self._get_user_info(provider, tokens["access_token"])
            
            # Create or update user
            user_id = await self._create_or_update_user(provider_id, user_info)
            
            # Create session
            session_id = await self._create_session(user_id, provider_id, app_id)
            
            logger.info(f"SSO callback handled: {provider_id} -> {user_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"❌ Error handling SSO callback: {e}")
            raise
    
    async def validate_session(self, session_token: str) -> Optional[SSOSession]:
        """Validate session token"""
        try:
            # Find session by token
            session = None
            for s in self.sessions.values():
                if s.session_token == session_token:
                    session = s
                    break
            
            if not session:
                return None
            
            # Check if session is expired
            if datetime.fromisoformat(session.expires_at) < datetime.now():
                # Remove expired session
                del self.sessions[session.id]
                return None
            
            # Update last activity
            session.last_activity = datetime.now().isoformat()
            
            return session
            
        except Exception as e:
            logger.error(f"❌ Error validating session: {e}")
            return None
    
    async def refresh_token(self, refresh_token: str) -> Optional[SSOToken]:
        """Refresh access token"""
        try:
            # Find token by refresh token
            token = None
            for t in self.tokens.values():
                if t.refresh_token == refresh_token:
                    token = t
                    break
            
            if not token:
                return None
            
            # Check if token is expired
            if datetime.fromisoformat(token.expires_at) < datetime.now():
                return None
            
            # Get provider
            provider = self.providers.get(token.provider_id)
            if not provider:
                return None
            
            # Refresh token
            new_tokens = await self._refresh_access_token(provider, refresh_token)
            
            # Update token
            token.access_token = new_tokens["access_token"]
            if "refresh_token" in new_tokens:
                token.refresh_token = new_tokens["refresh_token"]
            token.expires_at = new_tokens["expires_at"]
            token.updated_at = datetime.now().isoformat()
            
            logger.info(f"Token refreshed: {token.id}")
            return token
            
        except Exception as e:
            logger.error(f"❌ Error refreshing token: {e}")
            return None
    
    async def logout(self, session_token: str) -> bool:
        """Logout user"""
        try:
            # Find and remove session
            session = None
            for s in self.sessions.values():
                if s.session_token == session_token:
                    session = s
                    break
            
            if session:
                del self.sessions[session.id]
                logger.info(f"User logged out: {session.user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error logging out: {e}")
            return False
    
    async def get_user_sessions(self, user_id: str) -> List[SSOSession]:
        """Get user sessions"""
        try:
            sessions = [s for s in self.sessions.values() if s.user_id == user_id]
            return sessions
            
        except Exception as e:
            logger.error(f"❌ Error getting user sessions: {e}")
            return []
    
    async def revoke_user_sessions(self, user_id: str) -> int:
        """Revoke all user sessions"""
        try:
            user_sessions = [s for s in self.sessions.values() if s.user_id == user_id]
            
            for session in user_sessions:
                del self.sessions[session.id]
            
            logger.info(f"Revoked {len(user_sessions)} sessions for user {user_id}")
            return len(user_sessions)
            
        except Exception as e:
            logger.error(f"❌ Error revoking user sessions: {e}")
            return 0
    
    async def get_sso_analytics(self) -> Dict[str, Any]:
        """Get SSO system analytics"""
        try:
            total_providers = len(self.providers)
            total_users = len(self.users)
            total_sessions = len(self.sessions)
            total_applications = len(self.applications)
            
            # Active sessions
            active_sessions = [
                s for s in self.sessions.values()
                if datetime.fromisoformat(s.expires_at) > datetime.now()
            ]
            
            # Provider distribution
            provider_distribution = {}
            for user in self.users.values():
                provider_id = user.provider_id
                provider_distribution[provider_id] = provider_distribution.get(provider_id, 0) + 1
            
            # Recent logins
            recent_cutoff = datetime.now() - timedelta(hours=24)
            recent_logins = [
                u for u in self.users.values()
                if datetime.fromisoformat(u.last_login) > recent_cutoff
            ]
            
            # Session duration
            session_durations = []
            for session in self.sessions.values():
                if session.last_activity:
                    start_time = datetime.fromisoformat(session.created_at)
                    end_time = datetime.fromisoformat(session.last_activity)
                    duration = (end_time - start_time).total_seconds()
                    session_durations.append(duration)
            
            avg_session_duration = sum(session_durations) / len(session_durations) if session_durations else 0
            
            return {
                "providers": {
                    "total": total_providers,
                    "active": len([p for p in self.providers.values() if p.status == SSOStatus.ACTIVE])
                },
                "users": {
                    "total": total_users,
                    "recent_logins": len(recent_logins),
                    "provider_distribution": provider_distribution
                },
                "sessions": {
                    "total": total_sessions,
                    "active": len(active_sessions),
                    "avg_duration": avg_session_duration
                },
                "applications": {
                    "total": total_applications,
                    "active": len([a for a in self.applications.values() if a.status == SSOStatus.ACTIVE])
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting SSO analytics: {e}")
            return {"error": str(e)}
    
    async def _generate_authorization_url(self, provider: SSOProvider, app: SSOApplication, state: str, redirect_uri: str) -> str:
        """Generate authorization URL"""
        try:
            # In practice, this would generate actual OAuth URLs
            
            params = {
                "client_id": app.client_id,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": " ".join(provider.scopes),
                "state": state
            }
            
            # Build URL with parameters
            param_string = "&".join([f"{k}={v}" for k, v in params.items()])
            auth_url = f"{base_url}?{param_string}"
            
            return auth_url
            
        except Exception as e:
            logger.error(f"❌ Error generating authorization URL: {e}")
            return ""
    
    async def _exchange_code_for_tokens(self, provider: SSOProvider, code: str, app: SSOApplication) -> Dict[str, Any]:
        """Exchange authorization code for tokens"""
        try:
            # In practice, this would make actual API calls to the provider
            
            access_token = f"access_{hashlib.md5(f'{code}_{time.time()}'.encode()).hexdigest()[:32]}"
            refresh_token = f"refresh_{hashlib.md5(f'{code}_{time.time()}'.encode()).hexdigest()[:32]}"
            expires_at = (datetime.now() + timedelta(hours=1)).isoformat()
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_at": expires_at,
                "token_type": "Bearer"
            }
            
        except Exception as e:
            logger.error(f"❌ Error exchanging code for tokens: {e}")
            return {}
    
    async def _get_user_info(self, provider: SSOProvider, access_token: str) -> Dict[str, Any]:
        """Get user information from provider"""
        try:
            # In practice, this would make actual API calls to the provider
            
            user_info = {
                "id": f"user_{hashlib.md5(access_token.encode()).hexdigest()[:16]}",
                "name": f"User {hashlib.md5(access_token.encode()).hexdigest()[:8]}",
            }
            
            return user_info
            
        except Exception as e:
            logger.error(f"❌ Error getting user info: {e}")
            return {}
    
    async def _create_or_update_user(self, provider_id: str, user_info: Dict[str, Any]) -> str:
        """Create or update user"""
        try:
            external_id = user_info["id"]
            user_key = f"{provider_id}_{external_id}"
            
            if user_key in self.users:
                # Update existing user
                user = self.users[user_key]
                user.email = user_info.get("email", user.email)
                user.name = user_info.get("name", user.name)
                user.avatar_url = user_info.get("avatar_url", user.avatar_url)
                user.last_login = datetime.now().isoformat()
                user.profile_data = user_info
            else:
                # Create new user
                user = SSOUser(
                    id=user_key,
                    provider_id=provider_id,
                    external_id=external_id,
                    email=user_info.get("email", ""),
                    name=user_info.get("name", ""),
                    avatar_url=user_info.get("avatar_url"),
                    profile_data=user_info
                )
                self.users[user_key] = user
            
            return user.id
            
        except Exception as e:
            logger.error(f"❌ Error creating or updating user: {e}")
            return ""
    
    async def _create_session(self, user_id: str, provider_id: str, app_id: str) -> str:
        """Create user session"""
        try:
            session_id = f"session_{int(time.time())}_{hashlib.md5(f'{user_id}_{time.time()}'.encode()).hexdigest()[:16]}"
            session_token = self._generate_session_token()
            expires_at = (datetime.now() + timedelta(seconds=self.session_timeout)).isoformat()
            
            session = SSOSession(
                id=session_id,
                user_id=user_id,
                provider_id=provider_id,
                session_token=session_token,
                expires_at=expires_at,
                ip_address="127.0.0.1",  # In practice, get from request
                user_agent="FrenlyAI/1.0"  # In practice, get from request
            )
            
            self.sessions[session_id] = session
            
            # Limit sessions per user
            await self._limit_user_sessions(user_id)
            
            return session_id
            
        except Exception as e:
            logger.error(f"❌ Error creating session: {e}")
            return ""
    
    async def _limit_user_sessions(self, user_id: str):
        """Limit sessions per user"""
        try:
            user_sessions = [s for s in self.sessions.values() if s.user_id == user_id]
            
            if len(user_sessions) > self.max_sessions_per_user:
                # Remove oldest sessions
                user_sessions.sort(key=lambda s: s.created_at)
                sessions_to_remove = user_sessions[:-self.max_sessions_per_user]
                
                for session in sessions_to_remove:
                    del self.sessions[session.id]
                
                logger.info(f"Removed {len(sessions_to_remove)} old sessions for user {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Error limiting user sessions: {e}")
    
    async def _refresh_access_token(self, provider: SSOProvider, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token"""
        try:
            # In practice, this would make actual API calls to the provider
            
            new_access_token = f"access_{hashlib.md5(f'{refresh_token}_{time.time()}'.encode()).hexdigest()[:32]}"
            new_refresh_token = f"refresh_{hashlib.md5(f'{refresh_token}_{time.time()}'.encode()).hexdigest()[:32]}"
            expires_at = (datetime.now() + timedelta(hours=1)).isoformat()
            
            return {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "expires_at": expires_at
            }
            
        except Exception as e:
            logger.error(f"❌ Error refreshing access token: {e}")
            return {}
    
    def _generate_client_secret(self) -> str:
        """Generate client secret"""
        return base64.urlsafe_b64encode(hashlib.sha256(f"{time.time()}_{hashlib.md5(str(time.time()).encode()).hexdigest()}".encode()).digest()).decode()[:32]
    
    def _generate_session_token(self) -> str:
        """Generate session token"""
        return base64.urlsafe_b64encode(hashlib.sha256(f"{time.time()}_{hashlib.md5(str(time.time()).encode()).hexdigest()}".encode()).digest()).decode()[:32]
    
    async def _session_cleanup(self):
        """Session cleanup loop"""
        while self.running:
            try:
                current_time = datetime.now()
                expired_sessions = []
                
                for session_id, session in self.sessions.items():
                    if datetime.fromisoformat(session.expires_at) < current_time:
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    del self.sessions[session_id]
                
                if expired_sessions:
                    logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Error in session cleanup: {e}")
                await asyncio.sleep(600)
    
    async def _token_refresh_loop(self):
        """Token refresh loop"""
        while self.running:
            try:
                # Check for tokens that need refreshing
                current_time = datetime.now()
                tokens_to_refresh = []
                
                for token in self.tokens.values():
                    expires_at = datetime.fromisoformat(token.expires_at)
                    # Refresh if expires within 5 minutes
                    if (expires_at - current_time).total_seconds() < 300:
                        tokens_to_refresh.append(token)
                
                for token in tokens_to_refresh:
                    if token.refresh_token:
                        await self.refresh_token(token.refresh_token)
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Error in token refresh loop: {e}")
                await asyncio.sleep(600)
    
    async def _cleanup_old_data(self):
        """Clean up old SSO data"""
        while self.running:
            try:
                # Clean up old tokens
                token_cutoff = datetime.now() - timedelta(days=self.token_retention_days)
                
                old_tokens = [
                    token_id for token_id, token in self.tokens.items()
                    if datetime.fromisoformat(token.created_at) < token_cutoff
                ]
                
                for token_id in old_tokens:
                    del self.tokens[token_id]
                
                if old_tokens:
                    logger.info(f"Cleaned up {len(old_tokens)} old tokens")
                
                await asyncio.sleep(86400)  # Clean up daily
                
            except Exception as e:
                logger.error(f"❌ Error cleaning up old data: {e}")
                await asyncio.sleep(3600)
    
    async def _load_sso_data(self):
        """Load SSO data from storage"""
        try:
            if self.redis_client:
                # Load providers
                providers_data = self.redis_client.get("frenly_sso_providers")
                if providers_data:
                    providers_json = json.loads(providers_data)
                    for provider_id, provider_data in providers_json.items():
                        provider = SSOProvider(
                            id=provider_id,
                            name=provider_data["name"],
                            provider_type=SSOProvider(provider_data["provider_type"]),
                            client_id=provider_data["client_id"],
                            client_secret=provider_data["client_secret"],
                            redirect_uri=provider_data["redirect_uri"],
                            scopes=provider_data["scopes"],
                            status=SSOStatus(provider_data["status"]),
                            created_at=provider_data["created_at"],
                            updated_at=provider_data["updated_at"]
                        )
                        self.providers[provider_id] = provider
                
                # Load users
                users_data = self.redis_client.get("frenly_sso_users")
                if users_data:
                    users_json = json.loads(users_data)
                    for user_id, user_data in users_json.items():
                        user = SSOUser(
                            id=user_id,
                            provider_id=user_data["provider_id"],
                            external_id=user_data["external_id"],
                            email=user_data["email"],
                            name=user_data["name"],
                            avatar_url=user_data.get("avatar_url"),
                            profile_data=user_data.get("profile_data", {}),
                            created_at=user_data["created_at"],
                            last_login=user_data["last_login"]
                        )
                        self.users[user_id] = user
                
                # Load sessions
                sessions_data = self.redis_client.get("frenly_sso_sessions")
                if sessions_data:
                    sessions_json = json.loads(sessions_data)
                    for session_id, session_data in sessions_json.items():
                        session = SSOSession(
                            id=session_id,
                            user_id=session_data["user_id"],
                            provider_id=session_data["provider_id"],
                            session_token=session_data["session_token"],
                            expires_at=session_data["expires_at"],
                            ip_address=session_data["ip_address"],
                            user_agent=session_data["user_agent"],
                            created_at=session_data["created_at"],
                            last_activity=session_data["last_activity"]
                        )
                        self.sessions[session_id] = session
                
                # Load applications
                applications_data = self.redis_client.get("frenly_sso_applications")
                if applications_data:
                    applications_json = json.loads(applications_data)
                    for app_id, app_data in applications_json.items():
                        application = SSOApplication(
                            id=app_id,
                            name=app_data["name"],
                            client_id=app_data["client_id"],
                            client_secret=app_data["client_secret"],
                            redirect_uris=app_data["redirect_uris"],
                            scopes=app_data["scopes"],
                            status=SSOStatus(app_data["status"]),
                            created_at=app_data["created_at"],
                            updated_at=app_data["updated_at"]
                        )
                        self.applications[app_id] = application
                
                logger.info(f"Loaded {len(self.providers)} providers, {len(self.users)} users, {len(self.sessions)} sessions, {len(self.applications)} applications")
            
        except Exception as e:
            logger.error(f"❌ Error loading SSO data: {e}")
    
    async def _save_sso_data(self):
        """Save SSO data to storage"""
        try:
            if self.redis_client:
                # Save providers
                providers_data = {
                    provider_id: {
                        "name": provider.name,
                        "provider_type": provider.provider_type.value,
                        "client_id": provider.client_id,
                        "client_secret": provider.client_secret,
                        "redirect_uri": provider.redirect_uri,
                        "scopes": provider.scopes,
                        "status": provider.status.value,
                        "created_at": provider.created_at,
                        "updated_at": provider.updated_at
                    }
                    for provider_id, provider in self.providers.items()
                }
                self.redis_client.setex("frenly_sso_providers", 86400, json.dumps(providers_data))
                
                # Save users
                users_data = {
                    user_id: {
                        "provider_id": user.provider_id,
                        "external_id": user.external_id,
                        "email": user.email,
                        "name": user.name,
                        "avatar_url": user.avatar_url,
                        "profile_data": user.profile_data,
                        "created_at": user.created_at,
                        "last_login": user.last_login
                    }
                    for user_id, user in self.users.items()
                }
                self.redis_client.setex("frenly_sso_users", 86400, json.dumps(users_data))
                
                # Save sessions
                sessions_data = {
                    session_id: {
                        "user_id": session.user_id,
                        "provider_id": session.provider_id,
                        "session_token": session.session_token,
                        "expires_at": session.expires_at,
                        "ip_address": session.ip_address,
                        "user_agent": session.user_agent,
                        "created_at": session.created_at,
                        "last_activity": session.last_activity
                    }
                    for session_id, session in self.sessions.items()
                }
                self.redis_client.setex("frenly_sso_sessions", 86400, json.dumps(sessions_data))
                
                # Save applications
                applications_data = {
                    app_id: {
                        "name": app.name,
                        "client_id": app.client_id,
                        "client_secret": app.client_secret,
                        "redirect_uris": app.redirect_uris,
                        "scopes": app.scopes,
                        "status": app.status.value,
                        "created_at": app.created_at,
                        "updated_at": app.updated_at
                    }
                    for app_id, app in self.applications.items()
                }
                self.redis_client.setex("frenly_sso_applications", 86400, json.dumps(applications_data))
            
        except Exception as e:
            logger.error(f"❌ Error saving SSO data: {e}")

# Global SSO system instance
sso_system = SSOSystem()
