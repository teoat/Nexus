"""
Alert System for Nexus Platform

Implements a comprehensive alerting and notification system for queue metrics.
"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class AlertStatus(Enum):
    """Alert status."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    EXPIRED = "expired"

class NotificationType(Enum):
    """Notification types."""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"

@dataclass
class AlertRule:
    """Alert rule configuration."""
    id: str
    name: str
    metric_name: str
    condition: str  # e.g., ">", "<"
    threshold: float
    severity: AlertSeverity
    enabled: bool = True
    cooldown_minutes: int = 5
    notification_channels: List[str] = field(default_factory=list)

@dataclass
class Alert:
    """Alert instance."""
    id: str
    rule_id: str
    severity: AlertSeverity
    message: str
    created_at: float
    status: AlertStatus = AlertStatus.ACTIVE

@dataclass
class NotificationConfig:
    """Notification configuration."""
    type: NotificationType
    name: str
    config: Dict[str, Any]
    enabled: bool = True

class AlertSystem:
    """A system for monitoring metrics and triggering alerts."""

    def __init__(self, metrics_collector=None):
        """Initializes the AlertSystem."""
        self.metrics_collector = metrics_collector
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.notification_configs: Dict[str, NotificationConfig] = {}
        self._create_default_rules()
        logger.info("Alert System initialized")

    def _create_default_rules(self):
        """Creates a set of default alert rules."""
        default_rules = [
            AlertRule(id="high_queue_size", name="High Queue Size", metric_name="queue_size", condition=">", threshold=1000, severity=AlertSeverity.WARNING),
            AlertRule(id="high_latency", name="High Latency", metric_name="latency", condition=">", threshold=5000, severity=AlertSeverity.CRITICAL),
        ]
        for rule in default_rules:
            self.alert_rules[rule.id] = rule
        logger.info(f"Created {len(default_rules)} default alert rules")

    def check_alerts(self, metrics_data: Dict[str, Any]):
        """Checks metrics against alert rules and triggers alerts."""
        for rule in self.alert_rules.values():
            if not rule.enabled:
                continue

            metric_value = metrics_data.get(rule.metric_name)
            if metric_value is None:
                continue

            if self._evaluate_condition(metric_value, rule.condition, rule.threshold):
                alert = self._create_alert(rule, metric_value)
                self.active_alerts[alert.id] = alert
                self._send_notifications(alert)
                logger.info(f"Alert triggered: {rule.name}")

    def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Evaluates an alert condition."""
        if condition == ">":
            return value > threshold
        if condition == "<":
            return value < threshold
        return False

    def _create_alert(self, rule: AlertRule, current_value: float) -> Alert:
        """Creates a new alert instance."""
        message = f"{rule.name}: value {current_value} breached threshold {rule.threshold}"
        return Alert(
            id=str(uuid.uuid4()),
            rule_id=rule.id,
            severity=rule.severity,
            message=message,
            created_at=time.time(),
        )

    def _send_notifications(self, alert: Alert):
        """Sends notifications for a triggered alert."""
        rule = self.alert_rules.get(alert.rule_id)
        if not rule:
            return

        for channel_name in rule.notification_channels:
            config = self.notification_configs.get(channel_name)
            if config and config.enabled:
                self._send_notification(config, alert)

    def _send_notification(self, config: NotificationConfig, alert: Alert):
        """Sends a single notification via a specific channel."""
        if config.type == NotificationType.SLACK:
            webhook_url = config.config.get("webhook_url")
            if webhook_url:
                payload = {"text": f"🚨 {alert.severity.value.upper()} Alert: {alert.message}"}
                try:
                    requests.post(webhook_url, json=payload, timeout=10)
                    logger.info(f"Slack notification sent for alert {alert.id}")
                except requests.RequestException as e:
                    logger.error(f"Failed to send Slack notification: {e}")

def test_alert_system():
    """Tests the Alert System."""
    logging.basicConfig(level=logging.INFO)
    print("🧪 Testing Alert System")
    alert_system = AlertSystem()
    slack_config = NotificationConfig(
        type=NotificationType.SLACK,
        name="slack",
        config={"webhook_url": "https://hooks.slack.com/services/test"},
        enabled=True
    )
    alert_system.notification_configs['slack'] = slack_config
    alert_system.alert_rules['high_queue_size'].notification_channels.append('slack')

    test_metrics = {"queue_size": 1500}
    alert_system.check_alerts(test_metrics)
    print(f"Active alerts: {len(alert_system.active_alerts)}")
    for alert in alert_system.active_alerts.values():
        print(f"  - {alert.message}")

if __name__ == "__main__":
    test_alert_system()
