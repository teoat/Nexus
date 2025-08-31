import logging
from enum import Enum
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AlertManager:
    """
    Handles sending alerts for critical system events.
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.channels = self.config.get("alert_channels", ["log"])

    async def send_alert(self, level: AlertLevel, title: str, message: str, metadata: Dict[str, Any] = None):
        """
        Sends an alert through the configured channels.
        """
        if "log" in self.channels:
            self._send_log_alert(level, title, message, metadata)

        # In a real implementation, you would add other channels like email, Slack, etc.
        await self._send_email_alert(level, title, message, metadata)
        await self._send_slack_alert(level, title, message, metadata)


    def _send_log_alert(self, level: AlertLevel, title: str, message: str, metadata: Dict[str, Any] = None):
        log_message = f"ALERT [{level.value.upper()}] - {title}: {message}"
        if metadata:
            log_message += f" | Metadata: {metadata}"

        if level == AlertLevel.CRITICAL:
            logger.critical(log_message)
        elif level == AlertLevel.WARNING:
            logger.warning(log_message)
        else:
            logger.info(log_message)

    async def _send_email_alert(self, level: AlertLevel, title: str, message: str, metadata: Dict[str, Any] = None):
        if "email" in self.channels:
            logger.info(f"Simulating sending email alert: [{level.value.upper()}] {title} - {message}")
            # Add email sending logic here
            pass

    async def _send_slack_alert(self, level: AlertLevel, title: str, message: str, metadata: Dict[str, Any] = None):
        if "slack" in self.channels:
            logger.info(f"Simulating sending Slack alert: [{level.value.upper()}] {title} - {message}")
            # Add Slack sending logic here
            pass
