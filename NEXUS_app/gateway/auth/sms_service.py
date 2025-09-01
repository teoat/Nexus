"""
SMS Service for Multi-Factor Authentication
"""
import logging

logger = logging.getLogger(__name__)

class SMSService:
    """A service for sending SMS messages for MFA."""
    def send_sms(self, phone_number: str, message: str):
        """Sends an SMS message."""
        logger.info(f"Sending SMS to {phone_number}: {message}")
        # In a real implementation, this would connect to an SMS gateway like Twilio.
        return True
