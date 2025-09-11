#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
📱 Frenly AI Mobile Application System
Mobile app integration and management for Frenly AI
"""

import asyncio
import logging
import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import redis
from backend.config import get_config

logger = logging.getLogger(__name__)

class MobilePlatform(Enum):
    """Mobile platform enumeration"""
    IOS = "ios"
    ANDROID = "android"
    FLUTTER = "flutter"
    REACT_NATIVE = "react_native"
    XAMARIN = "xamarin"

class AppStatus(Enum):
    """App status enumeration"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"

class FeatureFlag(Enum):
    """Feature flag enumeration"""
    ENABLED = "enabled"
    DISABLED = "disabled"
    BETA = "beta"

class PushNotificationType(Enum):
    """Push notification type enumeration"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    PROMOTIONAL = "promotional"

@dataclass
class MobileApp:
    """Mobile application definition"""
    id: str
    name: str
    platform: MobilePlatform
    version: str
    build_number: int
    status: AppStatus
    bundle_id: str
    app_store_url: Optional[str] = None
    play_store_url: Optional[str] = None
    download_count: int = 0
    rating: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class AppFeature:
    """App feature definition"""
    id: str
    app_id: str
    name: str
    description: str
    flag: FeatureFlag
    rollout_percentage: float = 100.0
    target_audience: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class PushNotification:
    """Push notification definition"""
    id: str
    app_id: str
    title: str
    message: str
    notification_type: PushNotificationType
    target_users: Optional[List[str]] = None
    scheduled_time: Optional[str] = None
    sent: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class AppAnalytics:
    """App analytics definition"""
    id: str
    app_id: str
    date: str
    active_users: int
    new_users: int
    sessions: int
    session_duration: float
    crashes: int
    errors: int
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class UserSession:
    """User session definition"""
    id: str
    app_id: str
    user_id: str
    device_id: str
    platform: MobilePlatform
    version: str
    start_time: str
    end_time: Optional[str] = None
    duration: Optional[float] = None
    events: List[Dict[str, Any]] = field(default_factory=list)

class MobileAppSystem:
    """Mobile Application System for Frenly AI"""
    
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
        
        # Mobile app storage
        self.mobile_apps: Dict[str, MobileApp] = {}
        self.app_features: Dict[str, AppFeature] = {}
        self.push_notifications: Dict[str, PushNotification] = {}
        self.app_analytics: Dict[str, AppAnalytics] = {}
        self.user_sessions: Dict[str, UserSession] = {}
        
        # Configuration
        self.analytics_retention_days = 90
        self.session_timeout = 1800  # 30 minutes
        self.max_notifications_per_day = 1000
        
        # Initialize default apps
        self._initialize_default_apps()
        
        logger.info("✅ Mobile Application System initialized")
    
    def _initialize_default_apps(self):
        """Initialize default mobile applications"""
        try:
            # iOS App
            ios_app = MobileApp(
                id="ios_app_v1",
                name="Frenly AI iOS",
                platform=MobilePlatform.IOS,
                version="1.0.0",
                build_number=1,
                status=AppStatus.PRODUCTION,
                bundle_id="com.frenlyai.ios",
                app_store_url="https://apps.apple.com/app/frenly-ai/id123456789"
            )
            self.mobile_apps["ios_app_v1"] = ios_app
            
            # Android App
            android_app = MobileApp(
                id="android_app_v1",
                name="Frenly AI Android",
                platform=MobilePlatform.ANDROID,
                version="1.0.0",
                build_number=1,
                status=AppStatus.PRODUCTION,
                bundle_id="com.frenlyai.android",
                play_store_url="https://play.google.com/store/apps/details?id=com.frenlyai.android"
            )
            self.mobile_apps["android_app_v1"] = android_app
            
            # Flutter App
            flutter_app = MobileApp(
                id="flutter_app_v1",
                name="Frenly AI Flutter",
                platform=MobilePlatform.FLUTTER,
                version="1.0.0",
                build_number=1,
                status=AppStatus.DEVELOPMENT,
                bundle_id="com.frenlyai.flutter"
            )
            self.mobile_apps["flutter_app_v1"] = flutter_app
            
            logger.info(f"Initialized {len(self.mobile_apps)} mobile applications")
            
        except Exception as e:
            logger.error(f"❌ Error initializing default apps: {e}")
    
    async def start(self):
        """Start the mobile app system"""
        self.running = True
        logger.info("🚀 Starting Mobile Application System...")
        
        # Load existing data
        await self._load_mobile_data()
        
        # Start background tasks
        asyncio.create_task(self._cleanup_old_data())
        asyncio.create_task(self._process_scheduled_notifications())
        asyncio.create_task(self._session_cleanup())
        
        logger.info("✅ Mobile Application System started")
    
    async def stop(self):
        """Stop the mobile app system"""
        self.running = False
        logger.info("🛑 Stopping Mobile Application System...")
        
        # Save mobile data
        await self._save_mobile_data()
        
        logger.info("✅ Mobile Application System stopped")
    
    async def create_app(
        self,
        name: str,
        platform: MobilePlatform,
        version: str,
        bundle_id: str,
        status: AppStatus = AppStatus.DEVELOPMENT
    ) -> str:
        """Create a new mobile application"""
        try:
            app_id = f"app_{int(time.time())}"
            
            app = MobileApp(
                id=app_id,
                name=name,
                platform=platform,
                version=version,
                build_number=1,
                status=status,
                bundle_id=bundle_id
            )
            
            self.mobile_apps[app_id] = app
            
            logger.info(f"Mobile app created: {app_id}")
            return app_id
            
        except Exception as e:
            logger.error(f"❌ Error creating mobile app: {e}")
            raise
    
    async def get_app(self, app_id: str) -> Optional[MobileApp]:
        """Get mobile app information"""
        return self.mobile_apps.get(app_id)
    
    async def list_apps(self, platform: Optional[MobilePlatform] = None, status: Optional[AppStatus] = None) -> List[MobileApp]:
        """List mobile applications"""
        apps = list(self.mobile_apps.values())
        
        if platform:
            apps = [app for app in apps if app.platform == platform]
        
        if status:
            apps = [app for app in apps if app.status == status]
        
        return apps
    
    async def update_app(self, app_id: str, **updates) -> bool:
        """Update mobile app information"""
        try:
            if app_id not in self.mobile_apps:
                logger.warning(f"Mobile app not found: {app_id}")
                return False
            
            app = self.mobile_apps[app_id]
            
            # Update fields
            for key, value in updates.items():
                if hasattr(app, key):
                    setattr(app, key, value)
            
            app.updated_at = datetime.now().isoformat()
            
            logger.info(f"Mobile app updated: {app_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating mobile app {app_id}: {e}")
            return False
    
    async def create_feature(
        self,
        app_id: str,
        name: str,
        description: str,
        flag: FeatureFlag = FeatureFlag.ENABLED,
        rollout_percentage: float = 100.0,
        target_audience: Optional[str] = None
    ) -> str:
        """Create a new app feature"""
        try:
            if app_id not in self.mobile_apps:
                raise ValueError("Mobile app not found")
            
            feature_id = f"feature_{int(time.time())}"
            
            feature = AppFeature(
                id=feature_id,
                app_id=app_id,
                name=name,
                description=description,
                flag=flag,
                rollout_percentage=rollout_percentage,
                target_audience=target_audience
            )
            
            self.app_features[feature_id] = feature
            
            logger.info(f"App feature created: {feature_id}")
            return feature_id
            
        except Exception as e:
            logger.error(f"❌ Error creating app feature: {e}")
            raise
    
    async def get_feature(self, feature_id: str) -> Optional[AppFeature]:
        """Get app feature information"""
        return self.app_features.get(feature_id)
    
    async def list_features(self, app_id: Optional[str] = None) -> List[AppFeature]:
        """List app features"""
        features = list(self.app_features.values())
        
        if app_id:
            features = [f for f in features if f.app_id == app_id]
        
        return features
    
    async def update_feature(self, feature_id: str, **updates) -> bool:
        """Update app feature"""
        try:
            if feature_id not in self.app_features:
                logger.warning(f"App feature not found: {feature_id}")
                return False
            
            feature = self.app_features[feature_id]
            
            # Update fields
            for key, value in updates.items():
                if hasattr(feature, key):
                    setattr(feature, key, value)
            
            logger.info(f"App feature updated: {feature_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating app feature {feature_id}: {e}")
            return False
    
    async def send_push_notification(
        self,
        app_id: str,
        title: str,
        message: str,
        notification_type: PushNotificationType = PushNotificationType.INFO,
        target_users: Optional[List[str]] = None,
        scheduled_time: Optional[str] = None
    ) -> str:
        """Send push notification"""
        try:
            if app_id not in self.mobile_apps:
                raise ValueError("Mobile app not found")
            
            notification_id = f"notification_{int(time.time())}"
            
            notification = PushNotification(
                id=notification_id,
                app_id=app_id,
                title=title,
                message=message,
                notification_type=notification_type,
                target_users=target_users,
                scheduled_time=scheduled_time
            )
            
            self.push_notifications[notification_id] = notification
            
            # Send immediately if not scheduled
            if not scheduled_time:
                await self._send_notification(notification)
            
            logger.info(f"Push notification created: {notification_id}")
            return notification_id
            
        except Exception as e:
            logger.error(f"❌ Error sending push notification: {e}")
            raise
    
    async def get_notification(self, notification_id: str) -> Optional[PushNotification]:
        """Get push notification information"""
        return self.push_notifications.get(notification_id)
    
    async def list_notifications(self, app_id: Optional[str] = None, sent: Optional[bool] = None) -> List[PushNotification]:
        """List push notifications"""
        notifications = list(self.push_notifications.values())
        
        if app_id:
            notifications = [n for n in notifications if n.app_id == app_id]
        
        if sent is not None:
            notifications = [n for n in notifications if n.sent == sent]
        
        return notifications
    
    async def start_user_session(
        self,
        app_id: str,
        user_id: str,
        device_id: str,
        platform: MobilePlatform,
        version: str
    ) -> str:
        """Start a new user session"""
        try:
            if app_id not in self.mobile_apps:
                raise ValueError("Mobile app not found")
            
            session_id = f"session_{int(time.time())}_{hashlib.md5(f'{user_id}_{device_id}'.encode()).hexdigest()[:8]}"
            
            session = UserSession(
                id=session_id,
                app_id=app_id,
                user_id=user_id,
                device_id=device_id,
                platform=platform,
                version=version,
                start_time=datetime.now().isoformat()
            )
            
            self.user_sessions[session_id] = session
            
            logger.info(f"User session started: {session_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"❌ Error starting user session: {e}")
            raise
    
    async def end_user_session(self, session_id: str) -> bool:
        """End a user session"""
        try:
            if session_id not in self.user_sessions:
                logger.warning(f"User session not found: {session_id}")
                return False
            
            session = self.user_sessions[session_id]
            session.end_time = datetime.now().isoformat()
            
            # Calculate duration
            start_time = datetime.fromisoformat(session.start_time)
            end_time = datetime.fromisoformat(session.end_time)
            session.duration = (end_time - start_time).total_seconds()
            
            logger.info(f"User session ended: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error ending user session {session_id}: {e}")
            return False
    
    async def track_event(
        self,
        session_id: str,
        event_name: str,
        event_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Track user event"""
        try:
            if session_id not in self.user_sessions:
                logger.warning(f"User session not found: {session_id}")
                return False
            
            session = self.user_sessions[session_id]
            
            event = {
                "name": event_name,
                "timestamp": datetime.now().isoformat(),
                "data": event_data or {}
            }
            
            session.events.append(event)
            
            logger.info(f"Event tracked: {event_name} in session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error tracking event: {e}")
            return False
    
    async def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get user session information"""
        return self.user_sessions.get(session_id)
    
    async def get_app_analytics(
        self,
        app_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[AppAnalytics]:
        """Get app analytics data"""
        try:
            analytics = [a for a in self.app_analytics.values() if a.app_id == app_id]
            
            if start_date:
                analytics = [a for a in analytics if a.date >= start_date]
            
            if end_date:
                analytics = [a for a in analytics if a.date <= end_date]
            
            # Sort by date
            analytics.sort(key=lambda a: a.date)
            
            return analytics
            
        except Exception as e:
            logger.error(f"❌ Error getting app analytics: {e}")
            return []
    
    async def generate_analytics_report(self, app_id: str) -> Dict[str, Any]:
        """Generate analytics report for app"""
        try:
            if app_id not in self.mobile_apps:
                raise ValueError("Mobile app not found")
            
            # Get recent analytics (last 30 days)
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            
            analytics = await self.get_app_analytics(app_id, start_date, end_date)
            
            if not analytics:
                return {"error": "No analytics data available"}
            
            # Calculate metrics
            total_active_users = sum(a.active_users for a in analytics)
            total_new_users = sum(a.new_users for a in analytics)
            total_sessions = sum(a.sessions for a in analytics)
            total_crashes = sum(a.crashes for a in analytics)
            total_errors = sum(a.errors for a in analytics)
            
            avg_session_duration = sum(a.session_duration for a in analytics) / len(analytics)
            
            # Calculate growth rates
            if len(analytics) > 1:
                first_week = analytics[:7]
                last_week = analytics[-7:]
                
                first_week_users = sum(a.active_users for a in first_week)
                last_week_users = sum(a.active_users for a in last_week)
                
                user_growth_rate = ((last_week_users - first_week_users) / first_week_users * 100) if first_week_users > 0 else 0
            else:
                user_growth_rate = 0
            
            # Get active sessions
            active_sessions = [
                s for s in self.user_sessions.values()
                if s.app_id == app_id and s.end_time is None
            ]
            
            # Get feature usage
            features = await self.list_features(app_id)
            enabled_features = [f for f in features if f.flag == FeatureFlag.ENABLED]
            
            return {
                "app_id": app_id,
                "period": f"{start_date} to {end_date}",
                "metrics": {
                    "total_active_users": total_active_users,
                    "total_new_users": total_new_users,
                    "total_sessions": total_sessions,
                    "avg_session_duration": avg_session_duration,
                    "total_crashes": total_crashes,
                    "total_errors": total_errors,
                    "user_growth_rate": user_growth_rate
                },
                "current": {
                    "active_sessions": len(active_sessions),
                    "enabled_features": len(enabled_features),
                    "total_features": len(features)
                },
                "daily_data": [
                    {
                        "date": a.date,
                        "active_users": a.active_users,
                        "new_users": a.new_users,
                        "sessions": a.sessions,
                        "session_duration": a.session_duration,
                        "crashes": a.crashes,
                        "errors": a.errors
                    }
                    for a in analytics
                ],
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating analytics report: {e}")
            return {"error": str(e)}
    
    async def get_mobile_dashboard(self) -> Dict[str, Any]:
        """Get mobile app system dashboard"""
        try:
            total_apps = len(self.mobile_apps)
            total_features = len(self.app_features)
            total_notifications = len(self.push_notifications)
            total_sessions = len(self.user_sessions)
            
            # Platform distribution
            platform_distribution = {}
            for app in self.mobile_apps.values():
                platform = app.platform.value
                platform_distribution[platform] = platform_distribution.get(platform, 0) + 1
            
            # Status distribution
            status_distribution = {}
            for app in self.mobile_apps.values():
                status = app.status.value
                status_distribution[status] = status_distribution.get(status, 0) + 1
            
            # Active sessions
            active_sessions = [
                s for s in self.user_sessions.values()
                if s.end_time is None
            ]
            
            # Recent notifications
            recent_cutoff = datetime.now() - timedelta(hours=24)
            recent_notifications = [
                n for n in self.push_notifications.values()
                if datetime.fromisoformat(n.created_at) > recent_cutoff
            ]
            
            # Feature flags
            feature_flags = {}
            for feature in self.app_features.values():
                flag = feature.flag.value
                feature_flags[flag] = feature_flags.get(flag, 0) + 1
            
            return {
                "apps": {
                    "total": total_apps,
                    "platform_distribution": platform_distribution,
                    "status_distribution": status_distribution
                },
                "features": {
                    "total": total_features,
                    "flag_distribution": feature_flags
                },
                "notifications": {
                    "total": total_notifications,
                    "recent": len(recent_notifications),
                    "sent": len([n for n in self.push_notifications.values() if n.sent])
                },
                "sessions": {
                    "total": total_sessions,
                    "active": len(active_sessions)
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting mobile dashboard: {e}")
            return {"error": str(e)}
    
    async def _send_notification(self, notification: PushNotification):
        """Send push notification"""
        try:
            # In practice, this would integrate with FCM, APNs, etc.
            
            logger.info(f"Sending notification: {notification.title}")
            
            # Mark as sent
            notification.sent = True
            
            # Update app analytics
            await self._update_app_analytics(notification.app_id, "notification_sent")
            
        except Exception as e:
            logger.error(f"❌ Error sending notification: {e}")
    
    async def _update_app_analytics(self, app_id: str, event_type: str):
        """Update app analytics"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Find or create analytics record for today
            analytics_id = f"analytics_{app_id}_{today}"
            
            if analytics_id in self.app_analytics:
                analytics = self.app_analytics[analytics_id]
            else:
                analytics = AppAnalytics(
                    id=analytics_id,
                    app_id=app_id,
                    date=today,
                    active_users=0,
                    new_users=0,
                    sessions=0,
                    session_duration=0.0,
                    crashes=0,
                    errors=0
                )
                self.app_analytics[analytics_id] = analytics
            
            # Update metrics based on event type
            if event_type == "session_start":
                analytics.sessions += 1
            elif event_type == "user_new":
                analytics.new_users += 1
            elif event_type == "user_active":
                analytics.active_users += 1
            elif event_type == "crash":
                analytics.crashes += 1
            elif event_type == "error":
                analytics.errors += 1
            
        except Exception as e:
            logger.error(f"❌ Error updating app analytics: {e}")
    
    async def _process_scheduled_notifications(self):
        """Process scheduled notifications"""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Find notifications scheduled for now or earlier
                scheduled_notifications = [
                    n for n in self.push_notifications.values()
                    if n.scheduled_time and not n.sent and datetime.fromisoformat(n.scheduled_time) <= current_time
                ]
                
                for notification in scheduled_notifications:
                    await self._send_notification(notification)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"❌ Error processing scheduled notifications: {e}")
                await asyncio.sleep(300)
    
    async def _session_cleanup(self):
        """Clean up expired sessions"""
        while self.running:
            try:
                current_time = datetime.now()
                expired_sessions = []
                
                for session_id, session in self.user_sessions.items():
                    if session.end_time:
                        continue  # Already ended
                    
                    start_time = datetime.fromisoformat(session.start_time)
                    if (current_time - start_time).total_seconds() > self.session_timeout:
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    await self.end_user_session(session_id)
                
                if expired_sessions:
                    logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Error in session cleanup: {e}")
                await asyncio.sleep(600)
    
    async def _cleanup_old_data(self):
        """Clean up old mobile data"""
        while self.running:
            try:
                # Clean up old analytics
                cutoff_date = datetime.now() - timedelta(days=self.analytics_retention_days)
                
                old_analytics = [
                    analytics_id for analytics_id, analytics in self.app_analytics.items()
                    if datetime.fromisoformat(analytics.created_at) < cutoff_date
                ]
                
                for analytics_id in old_analytics:
                    del self.app_analytics[analytics_id]
                
                # Clean up old sessions
                old_sessions = [
                    session_id for session_id, session in self.user_sessions.items()
                    if session.end_time and datetime.fromisoformat(session.end_time) < cutoff_date
                ]
                
                for session_id in old_sessions:
                    del self.user_sessions[session_id]
                
                if old_analytics or old_sessions:
                    logger.info(f"Cleaned up {len(old_analytics)} old analytics and {len(old_sessions)} old sessions")
                
                await asyncio.sleep(86400)  # Clean up daily
                
            except Exception as e:
                logger.error(f"❌ Error cleaning up old data: {e}")
                await asyncio.sleep(3600)
    
    async def _load_mobile_data(self):
        """Load mobile data from storage"""
        try:
            if self.redis_client:
                # Load mobile apps
                apps_data = self.redis_client.get("frenly_mobile_apps")
                if apps_data:
                    apps_json = json.loads(apps_data)
                    for app_id, app_data in apps_json.items():
                        app = MobileApp(
                            id=app_id,
                            name=app_data["name"],
                            platform=MobilePlatform(app_data["platform"]),
                            version=app_data["version"],
                            build_number=app_data["build_number"],
                            status=AppStatus(app_data["status"]),
                            bundle_id=app_data["bundle_id"],
                            app_store_url=app_data.get("app_store_url"),
                            play_store_url=app_data.get("play_store_url"),
                            download_count=app_data.get("download_count", 0),
                            rating=app_data.get("rating", 0.0),
                            created_at=app_data["created_at"],
                            updated_at=app_data["updated_at"]
                        )
                        self.mobile_apps[app_id] = app
                
                # Load app features
                features_data = self.redis_client.get("frenly_app_features")
                if features_data:
                    features_json = json.loads(features_data)
                    for feature_id, feature_data in features_json.items():
                        feature = AppFeature(
                            id=feature_id,
                            app_id=feature_data["app_id"],
                            name=feature_data["name"],
                            description=feature_data["description"],
                            flag=FeatureFlag(feature_data["flag"]),
                            rollout_percentage=feature_data.get("rollout_percentage", 100.0),
                            target_audience=feature_data.get("target_audience"),
                            created_at=feature_data["created_at"]
                        )
                        self.app_features[feature_id] = feature
                
                # Load push notifications
                notifications_data = self.redis_client.get("frenly_push_notifications")
                if notifications_data:
                    notifications_json = json.loads(notifications_data)
                    for notification_id, notification_data in notifications_json.items():
                        notification = PushNotification(
                            id=notification_id,
                            app_id=notification_data["app_id"],
                            title=notification_data["title"],
                            message=notification_data["message"],
                            notification_type=PushNotificationType(notification_data["notification_type"]),
                            target_users=notification_data.get("target_users"),
                            scheduled_time=notification_data.get("scheduled_time"),
                            sent=notification_data.get("sent", False),
                            created_at=notification_data["created_at"]
                        )
                        self.push_notifications[notification_id] = notification
                
                # Load app analytics
                analytics_data = self.redis_client.get("frenly_app_analytics")
                if analytics_data:
                    analytics_json = json.loads(analytics_data)
                    for analytics_id, analytics_data in analytics_json.items():
                        analytics = AppAnalytics(
                            id=analytics_id,
                            app_id=analytics_data["app_id"],
                            date=analytics_data["date"],
                            active_users=analytics_data["active_users"],
                            new_users=analytics_data["new_users"],
                            sessions=analytics_data["sessions"],
                            session_duration=analytics_data["session_duration"],
                            crashes=analytics_data["crashes"],
                            errors=analytics_data["errors"],
                            created_at=analytics_data["created_at"]
                        )
                        self.app_analytics[analytics_id] = analytics
                
                # Load user sessions
                sessions_data = self.redis_client.get("frenly_user_sessions")
                if sessions_data:
                    sessions_json = json.loads(sessions_data)
                    for session_id, session_data in sessions_json.items():
                        session = UserSession(
                            id=session_id,
                            app_id=session_data["app_id"],
                            user_id=session_data["user_id"],
                            device_id=session_data["device_id"],
                            platform=MobilePlatform(session_data["platform"]),
                            version=session_data["version"],
                            start_time=session_data["start_time"],
                            end_time=session_data.get("end_time"),
                            duration=session_data.get("duration"),
                            events=session_data.get("events", [])
                        )
                        self.user_sessions[session_id] = session
                
                logger.info(f"Loaded {len(self.mobile_apps)} apps, {len(self.app_features)} features, {len(self.push_notifications)} notifications, {len(self.app_analytics)} analytics, {len(self.user_sessions)} sessions")
            
        except Exception as e:
            logger.error(f"❌ Error loading mobile data: {e}")
    
    async def _save_mobile_data(self):
        """Save mobile data to storage"""
        try:
            if self.redis_client:
                # Save mobile apps
                apps_data = {
                    app_id: {
                        "name": app.name,
                        "platform": app.platform.value,
                        "version": app.version,
                        "build_number": app.build_number,
                        "status": app.status.value,
                        "bundle_id": app.bundle_id,
                        "app_store_url": app.app_store_url,
                        "play_store_url": app.play_store_url,
                        "download_count": app.download_count,
                        "rating": app.rating,
                        "created_at": app.created_at,
                        "updated_at": app.updated_at
                    }
                    for app_id, app in self.mobile_apps.items()
                }
                self.redis_client.setex("frenly_mobile_apps", 86400, json.dumps(apps_data))
                
                # Save app features
                features_data = {
                    feature_id: {
                        "app_id": feature.app_id,
                        "name": feature.name,
                        "description": feature.description,
                        "flag": feature.flag.value,
                        "rollout_percentage": feature.rollout_percentage,
                        "target_audience": feature.target_audience,
                        "created_at": feature.created_at
                    }
                    for feature_id, feature in self.app_features.items()
                }
                self.redis_client.setex("frenly_app_features", 86400, json.dumps(features_data))
                
                # Save push notifications
                notifications_data = {
                    notification_id: {
                        "app_id": notification.app_id,
                        "title": notification.title,
                        "message": notification.message,
                        "notification_type": notification.notification_type.value,
                        "target_users": notification.target_users,
                        "scheduled_time": notification.scheduled_time,
                        "sent": notification.sent,
                        "created_at": notification.created_at
                    }
                    for notification_id, notification in self.push_notifications.items()
                }
                self.redis_client.setex("frenly_push_notifications", 86400, json.dumps(notifications_data))
                
                # Save app analytics
                analytics_data = {
                    analytics_id: {
                        "app_id": analytics.app_id,
                        "date": analytics.date,
                        "active_users": analytics.active_users,
                        "new_users": analytics.new_users,
                        "sessions": analytics.sessions,
                        "session_duration": analytics.session_duration,
                        "crashes": analytics.crashes,
                        "errors": analytics.errors,
                        "created_at": analytics.created_at
                    }
                    for analytics_id, analytics in self.app_analytics.items()
                }
                self.redis_client.setex("frenly_app_analytics", 86400, json.dumps(analytics_data))
                
                # Save user sessions
                sessions_data = {
                    session_id: {
                        "app_id": session.app_id,
                        "user_id": session.user_id,
                        "device_id": session.device_id,
                        "platform": session.platform.value,
                        "version": session.version,
                        "start_time": session.start_time,
                        "end_time": session.end_time,
                        "duration": session.duration,
                        "events": session.events
                    }
                    for session_id, session in self.user_sessions.items()
                }
                self.redis_client.setex("frenly_user_sessions", 86400, json.dumps(sessions_data))
            
        except Exception as e:
            logger.error(f"❌ Error saving mobile data: {e}")

# Global mobile app system instance
mobile_app = MobileAppSystem()
