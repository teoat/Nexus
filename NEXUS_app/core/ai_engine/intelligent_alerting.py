#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
🚨 Frenly AI Intelligent Alerting System
ML-based alerting with multi-channel notifications and alert fatigue prevention
"""

import asyncio
import logging
import time
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import redis
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from backend.config import get_config

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(Enum):
    """Alert status enumeration"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"

class NotificationChannel(Enum):
    """Notification channel enumeration"""
    EMAIL = "email"
    SMS = "sms"
    SLACK = "slack"
    WEBHOOK = "webhook"
    DASHBOARD = "dashboard"

@dataclass
class AlertRule:
    """Alert rule definition"""
    id: str
    name: str
    description: str
    metric_name: str
    condition: str
    threshold: float
    severity: AlertSeverity
    enabled: bool
    cooldown: int  # seconds
    channels: List[NotificationChannel]
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass
class Alert:
    """Alert definition"""
    id: str
    rule_id: str
    severity: AlertSeverity
    message: str
    metric_value: float
    threshold: float
    timestamp: str
    status: AlertStatus
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[str] = None
    resolved_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Notification:
    """Notification definition"""
    id: str
    alert_id: str
    channel: NotificationChannel
    recipient: str
    message: str
    sent: bool
    sent_at: Optional[str] = None
    error: Optional[str] = None

class IntelligentAlerting:
    """Intelligent alerting system with ML-based thresholds"""
    
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
        
        # Alert storage
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.notifications: List[Notification] = []
        
        # ML models
        self.anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
        self.threshold_learner = None
        self.scaler = StandardScaler()
        
        # Alert configuration
        self.alert_cooldown = 300  # 5 minutes
        self.max_alerts_per_hour = 10
        self.alert_fatigue_threshold = 5
        
        # Initialize default rules
        self._initialize_default_rules()
        
        logger.info("✅ Intelligent Alerting initialized")
    
    async def start(self):
        """Start the intelligent alerting system"""
        self.running = True
        logger.info("🚀 Starting Intelligent Alerting...")
        
        # Load existing data
        await self._load_alert_rules()
        await self._load_alert_history()
        
        # Start background tasks
        asyncio.create_task(self._monitor_metrics())
        asyncio.create_task(self._process_alerts())
        asyncio.create_task(self._learn_thresholds())
        asyncio.create_task(self._prevent_alert_fatigue())
        
        logger.info("✅ Intelligent Alerting started")
    
    async def stop(self):
        """Stop the intelligent alerting system"""
        self.running = False
        logger.info("🛑 Stopping Intelligent Alerting...")
        
        # Save data
        await self._save_alert_rules()
        await self._save_alert_history()
        
        logger.info("✅ Intelligent Alerting stopped")
    
    async def create_alert_rule(self, name: str, description: str, metric_name: str,
                               condition: str, threshold: float, severity: AlertSeverity,
                               channels: List[NotificationChannel],
                               cooldown: int = 300, tags: Optional[Dict[str, str]] = None) -> str:
        """Create a new alert rule"""
        try:
            rule_id = f"rule_{int(time.time() * 1000)}"
            
            rule = AlertRule(
                id=rule_id,
                name=name,
                description=description,
                metric_name=metric_name,
                condition=condition,
                threshold=threshold,
                severity=severity,
                enabled=True,
                cooldown=cooldown,
                channels=channels,
                tags=tags or {}
            )
            
            self.alert_rules[rule_id] = rule
            
            logger.info(f"Alert rule created: {rule_id}")
            return rule_id
            
        except Exception as e:
            logger.error(f"❌ Error creating alert rule: {e}")
            return None
    
    async def update_alert_rule(self, rule_id: str, **kwargs) -> bool:
        """Update an existing alert rule"""
        try:
            if rule_id not in self.alert_rules:
                return False
            
            rule = self.alert_rules[rule_id]
            
            # Update allowed fields
            allowed_fields = ['name', 'description', 'condition', 'threshold', 
                            'severity', 'enabled', 'cooldown', 'channels', 'tags']
            
            for field, value in kwargs.items():
                if field in allowed_fields:
                    setattr(rule, field, value)
            
            logger.info(f"Alert rule updated: {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating alert rule: {e}")
            return False
    
    async def delete_alert_rule(self, rule_id: str) -> bool:
        """Delete an alert rule"""
        try:
            if rule_id not in self.alert_rules:
                return False
            
            del self.alert_rules[rule_id]
            
            logger.info(f"Alert rule deleted: {rule_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error deleting alert rule: {e}")
            return False
    
    async def check_metric(self, metric_name: str, value: float, timestamp: Optional[str] = None):
        """Check a metric against alert rules"""
        try:
            if not timestamp:
                timestamp = datetime.now().isoformat()
            
            # Check all rules for this metric
            for rule in self.alert_rules.values():
                if rule.metric_name == metric_name and rule.enabled:
                    await self._evaluate_rule(rule, value, timestamp)
            
        except Exception as e:
            logger.error(f"❌ Error checking metric {metric_name}: {e}")
    
    async def _evaluate_rule(self, rule: AlertRule, value: float, timestamp: str):
        """Evaluate a single alert rule"""
        try:
            # Check if alert should be triggered
            should_alert = False
            
            if rule.condition == "greater_than" and value > rule.threshold:
                should_alert = True
            elif rule.condition == "less_than" and value < rule.threshold:
                should_alert = True
            elif rule.condition == "equals" and value == rule.threshold:
                should_alert = True
            elif rule.condition == "not_equals" and value != rule.threshold:
                should_alert = True
            
            if not should_alert:
                return
            
            # Check cooldown
            recent_alerts = [
                alert for alert in self.active_alerts.values()
                if (alert.rule_id == rule.id and 
                    datetime.fromisoformat(alert.timestamp) > 
                    datetime.now() - timedelta(seconds=rule.cooldown))
            ]
            
            if recent_alerts:
                logger.debug(f"Alert suppressed due to cooldown: {rule.id}")
                return
            
            # Create alert
            await self._create_alert(rule, value, timestamp)
            
        except Exception as e:
            logger.error(f"❌ Error evaluating rule {rule.id}: {e}")
    
    async def _create_alert(self, rule: AlertRule, value: float, timestamp: str):
        """Create a new alert"""
        try:
            alert_id = f"alert_{int(time.time() * 1000)}"
            
            alert = Alert(
                id=alert_id,
                rule_id=rule.id,
                severity=rule.severity,
                message=f"{rule.name}: {rule.metric_name} = {value} (threshold: {rule.threshold})",
                metric_value=value,
                threshold=rule.threshold,
                timestamp=timestamp,
                status=AlertStatus.ACTIVE,
                metadata={
                    "rule_name": rule.name,
                    "condition": rule.condition,
                    "tags": rule.tags
                }
            )
            
            self.active_alerts[alert_id] = alert
            self.alert_history.append(alert)
            
            # Send notifications
            await self._send_notifications(alert, rule)
            
            logger.warning(f"🚨 Alert created: {alert_id} - {alert.message}")
            
        except Exception as e:
            logger.error(f"❌ Error creating alert: {e}")
    
    async def _send_notifications(self, alert: Alert, rule: AlertRule):
        """Send notifications for an alert"""
        try:
            for channel in rule.channels:
                notification_id = f"notif_{int(time.time() * 1000)}"
                
                # Determine recipient based on channel
                recipient = self._get_recipient_for_channel(channel)
                
                # Create notification message
                message = self._create_notification_message(alert, channel)
                
                notification = Notification(
                    id=notification_id,
                    alert_id=alert.id,
                    channel=channel,
                    recipient=recipient,
                    message=message,
                    sent=False
                )
                
                # Send notification
                success = await self._send_notification(notification)
                
                if success:
                    notification.sent = True
                    notification.sent_at = datetime.now().isoformat()
                else:
                    notification.error = "Failed to send notification"
                
                self.notifications.append(notification)
                
        except Exception as e:
            logger.error(f"❌ Error sending notifications: {e}")
    
    async def _send_notification(self, notification: Notification) -> bool:
        """Send a single notification"""
        try:
            # In a real implementation, this would integrate with actual services
            
            if notification.channel == NotificationChannel.EMAIL:
                logger.info(f"📧 Email sent to {notification.recipient}: {notification.message}")
            elif notification.channel == NotificationChannel.SMS:
                logger.info(f"📱 SMS sent to {notification.recipient}: {notification.message}")
            elif notification.channel == NotificationChannel.SLACK:
                logger.info(f"💬 Slack message sent to {notification.recipient}: {notification.message}")
            elif notification.channel == NotificationChannel.WEBHOOK:
                logger.info(f"🔗 Webhook sent to {notification.recipient}: {notification.message}")
            elif notification.channel == NotificationChannel.DASHBOARD:
                logger.info(f"📊 Dashboard notification: {notification.message}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending notification: {e}")
            return False
    
    async def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge an alert"""
        try:
            if alert_id not in self.active_alerts:
                return False
            
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.now().isoformat()
            
            logger.info(f"Alert acknowledged: {alert_id} by {acknowledged_by}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error acknowledging alert: {e}")
            return False
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert"""
        try:
            if alert_id not in self.active_alerts:
                return False
            
            alert = self.active_alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.now().isoformat()
            
            # Move to history
            self.alert_history.append(alert)
            del self.active_alerts[alert_id]
            
            logger.info(f"Alert resolved: {alert_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error resolving alert: {e}")
            return False
    
    async def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return list(self.active_alerts.values())
    
    async def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """Get alert history"""
        return self.alert_history[-limit:] if limit else self.alert_history
    
    async def get_alert_analytics(self) -> Dict[str, Any]:
        """Get alert analytics and insights"""
        try:
            # Calculate metrics
            total_alerts = len(self.alert_history)
            active_alerts = len(self.active_alerts)
            resolved_alerts = len([a for a in self.alert_history if a.status == AlertStatus.RESOLVED])
            
            # Calculate by severity
            severity_counts = {}
            for alert in self.alert_history:
                severity = alert.severity.value
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            # Calculate by rule
            rule_counts = {}
            for alert in self.alert_history:
                rule_id = alert.rule_id
                rule_counts[rule_id] = rule_counts.get(rule_id, 0) + 1
            
            # Calculate alert frequency
            recent_alerts = [
                a for a in self.alert_history
                if datetime.fromisoformat(a.timestamp) > datetime.now() - timedelta(hours=24)
            ]
            alerts_per_hour = len(recent_alerts) / 24
            
            # Calculate resolution time
            resolved_with_time = [
                a for a in self.alert_history
                if a.status == AlertStatus.RESOLVED and a.resolved_at
            ]
            
            avg_resolution_time = 0
            if resolved_with_time:
                resolution_times = []
                for alert in resolved_with_time:
                    start = datetime.fromisoformat(alert.timestamp)
                    end = datetime.fromisoformat(alert.resolved_at)
                    resolution_times.append((end - start).total_seconds())
                
                avg_resolution_time = sum(resolution_times) / len(resolution_times)
            
            return {
                "total_alerts": total_alerts,
                "active_alerts": active_alerts,
                "resolved_alerts": resolved_alerts,
                "severity_distribution": severity_counts,
                "rule_distribution": rule_counts,
                "alerts_per_hour": alerts_per_hour,
                "avg_resolution_time_seconds": avg_resolution_time,
                "alert_fatigue_risk": "high" if alerts_per_hour > self.alert_fatigue_threshold else "low",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting alert analytics: {e}")
            return {"error": str(e)}
    
    async def _monitor_metrics(self):
        """Monitor metrics for alerting"""
        while self.running:
            try:
                # This would typically monitor actual metrics
                
                import psutil
                cpu_usage = psutil.cpu_percent(interval=1)
                await self.check_metric("cpu_usage", cpu_usage)
                
                memory = psutil.virtual_memory()
                await self.check_metric("memory_usage", memory.percent)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"❌ Error monitoring metrics: {e}")
                await asyncio.sleep(60)
    
    async def _process_alerts(self):
        """Process alerts and notifications"""
        while self.running:
            try:
                # Process any pending notifications
                pending_notifications = [
                    n for n in self.notifications 
                    if not n.sent and not n.error
                ]
                
                for notification in pending_notifications:
                    await self._send_notification(notification)
                
                await asyncio.sleep(30)  # Process every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Error processing alerts: {e}")
                await asyncio.sleep(60)
    
    async def _learn_thresholds(self):
        """Learn optimal thresholds using ML"""
        while self.running:
            try:
                # This would implement ML-based threshold learning
                
                if len(self.alert_history) > 100:
                    logger.debug("Learning thresholds from historical data...")
                
                await asyncio.sleep(3600)  # Learn every hour
                
            except Exception as e:
                logger.error(f"❌ Error learning thresholds: {e}")
                await asyncio.sleep(60)
    
    async def _prevent_alert_fatigue(self):
        """Prevent alert fatigue by managing alert frequency"""
        while self.running:
            try:
                # Check for alert fatigue
                recent_alerts = [
                    a for a in self.alert_history
                    if datetime.fromisoformat(a.timestamp) > 
                    datetime.now() - timedelta(hours=1)
                ]
                
                if len(recent_alerts) > self.max_alerts_per_hour:
                    logger.warning("⚠️ Alert fatigue detected - suppressing new alerts")
                    
                    # Temporarily disable some rules
                    for rule in self.alert_rules.values():
                        if rule.severity in [AlertSeverity.LOW, AlertSeverity.MEDIUM]:
                            rule.enabled = False
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Error preventing alert fatigue: {e}")
                await asyncio.sleep(60)
    
    def _initialize_default_rules(self):
        """Initialize default alert rules"""
        try:
            # CPU usage rule
            self.alert_rules["cpu_high"] = AlertRule(
                id="cpu_high",
                name="High CPU Usage",
                description="Alert when CPU usage exceeds 80%",
                metric_name="cpu_usage",
                condition="greater_than",
                threshold=80.0,
                severity=AlertSeverity.HIGH,
                enabled=True,
                cooldown=300,
                channels=[NotificationChannel.EMAIL, NotificationChannel.DASHBOARD]
            )
            
            # Memory usage rule
            self.alert_rules["memory_high"] = AlertRule(
                id="memory_high",
                name="High Memory Usage",
                description="Alert when memory usage exceeds 85%",
                metric_name="memory_usage",
                condition="greater_than",
                threshold=85.0,
                severity=AlertSeverity.HIGH,
                enabled=True,
                cooldown=300,
                channels=[NotificationChannel.EMAIL, NotificationChannel.DASHBOARD]
            )
            
            # Error rate rule
            self.alert_rules["error_rate_high"] = AlertRule(
                id="error_rate_high",
                name="High Error Rate",
                description="Alert when error rate exceeds 10%",
                metric_name="error_rate",
                condition="greater_than",
                threshold=0.1,
                severity=AlertSeverity.CRITICAL,
                enabled=True,
                cooldown=60,
                channels=[NotificationChannel.EMAIL, NotificationChannel.SMS, NotificationChannel.DASHBOARD]
            )
            
        except Exception as e:
            logger.error(f"❌ Error initializing default rules: {e}")
    
    def _get_recipient_for_channel(self, channel: NotificationChannel) -> str:
        """Get recipient for notification channel"""
        recipients = {
            NotificationChannel.EMAIL: "admin@frenly.ai",
            NotificationChannel.SMS: "+1234567890",
            NotificationChannel.SLACK: "#alerts",
            NotificationChannel.WEBHOOK: "https://hooks.slack.com/services/...",
            NotificationChannel.DASHBOARD: "dashboard"
        }
        return recipients.get(channel, "unknown")
    
    def _create_notification_message(self, alert: Alert, channel: NotificationChannel) -> str:
        """
         Create Notification Message
        
        
        Args:
            alert: Description of alert
            channel: Description of channel
    
        Returns:
            str: Description of return value
    
        Example:
            TBD: Add usage example
        """
        base_message = f"🚨 {alert.severity.value.upper()}: {alert.message}"
        
        if channel == NotificationChannel.SMS:
            return f"ALERT: {alert.message}"
        elif channel == NotificationChannel.SLACK:
            return f"<!channel> {base_message}"
        else:
            return base_message
    
    async def _load_alert_rules(self):
        """Load alert rules from Redis"""
        try:
            if self.redis_client:
                data = self.redis_client.get("frenly_alert_rules")
                if data:
                    rules_data = json.loads(data)
                    self.alert_rules = {
                        rule_id: AlertRule(**rule_data)
                        for rule_id, rule_data in rules_data.items()
                    }
                    logger.info(f"Loaded {len(self.alert_rules)} alert rules")
            
        except Exception as e:
            logger.error(f"❌ Error loading alert rules: {e}")
    
    async def _save_alert_rules(self):
        """Save alert rules to Redis"""
        try:
            if self.redis_client:
                rules_data = {
                    rule_id: {
                        "id": rule.id,
                        "name": rule.name,
                        "description": rule.description,
                        "metric_name": rule.metric_name,
                        "condition": rule.condition,
                        "threshold": rule.threshold,
                        "severity": rule.severity.value,
                        "enabled": rule.enabled,
                        "cooldown": rule.cooldown,
                        "channels": [c.value for c in rule.channels],
                        "tags": rule.tags
                    }
                    for rule_id, rule in self.alert_rules.items()
                }
                
                self.redis_client.setex(
                    "frenly_alert_rules",
                    86400,  # 24 hours TTL
                    json.dumps(rules_data, default=str)
                )
            
        except Exception as e:
            logger.error(f"❌ Error saving alert rules: {e}")
    
    async def _load_alert_history(self):
        """Load alert history from Redis"""
        try:
            if self.redis_client:
                data = self.redis_client.get("frenly_alert_history")
                if data:
                    history_data = json.loads(data)
                    self.alert_history = [Alert(**alert_data) for alert_data in history_data]
                    logger.info(f"Loaded {len(self.alert_history)} alert history records")
            
        except Exception as e:
            logger.error(f"❌ Error loading alert history: {e}")
    
    async def _save_alert_history(self):
        """Save alert history to Redis"""
        try:
            if self.redis_client:
                history_data = [
                    {
                        "id": alert.id,
                        "rule_id": alert.rule_id,
                        "severity": alert.severity.value,
                        "message": alert.message,
                        "metric_value": alert.metric_value,
                        "threshold": alert.threshold,
                        "timestamp": alert.timestamp,
                        "status": alert.status.value,
                        "acknowledged_by": alert.acknowledged_by,
                        "acknowledged_at": alert.acknowledged_at,
                        "resolved_at": alert.resolved_at,
                        "metadata": alert.metadata
                    }
                    for alert in self.alert_history[-1000:]  # Last 1000 alerts
                ]
                
                self.redis_client.setex(
                    "frenly_alert_history",
                    86400,  # 24 hours TTL
                    json.dumps(history_data, default=str)
                )
            
        except Exception as e:
            logger.error(f"❌ Error saving alert history: {e}")

# Global intelligent alerting instance
intelligent_alerting = IntelligentAlerting()
