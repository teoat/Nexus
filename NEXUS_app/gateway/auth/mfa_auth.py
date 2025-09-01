"""
Multi-Factor Authentication (MFA) Implementation
"""
import logging
from .sms_service import SMSService
from .totp_service import TOTPService

logger = logging.getLogger(__name__)

class MFAAuth:
    """A class to handle Multi-Factor Authentication."""
    def __init__(self):
        self.sms_service = SMSService()
        self.totp_service = TOTPService()
        logger.info("MFAAuth initialized")

    def send_sms_code(self, phone_number: str):
        """Sends an MFA code via SMS."""
        code = "123456" # In a real implementation, this would be random
        self.sms_service.send_sms(phone_number, f"Your MFA code is: {code}")
        return True

    def verify_totp_code(self, secret: str, token: str) -> bool:
        """Verifies a TOTP code."""
        return self.totp_service.verify_token(secret, token)
