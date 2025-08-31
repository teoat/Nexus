"""
SMS Authentication Service

Handles SMS-based multi-factor authentication.
"""
import logging
import random
import string
from datetime import datetime, timedelta
from typing import Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SMSCode:
    """Represents an SMS verification code."""
    user_id: str
    code: str
    expires_at: datetime

class SMSService:
    """Service for sending and verifying SMS codes."""

    def __init__(self):
        """Initializes the SMSService."""
        self.codes: Dict[str, SMSCode] = {}
        self.code_length = 6
        self.expiry_minutes = 10
        logger.info("SMSService initialized")

    def generate_and_send_code(self, user_id: str, phone_number: str) -> bool:
        """Generates a code and sends it via a mock SMS provider."""
        code = "".join(random.choices(string.digits, k=self.code_length))
        expires_at = datetime.utcnow() + timedelta(minutes=self.expiry_minutes)
        self.codes[user_id] = SMSCode(user_id=user_id, code=code, expires_at=expires_at)

        # Mock sending the SMS
        logger.info(f"Sending SMS to {phone_number} for user {user_id} with code {code}")
        return True

    def verify_code(self, user_id: str, code: str) -> bool:
        """Verifies an SMS code."""
        stored_code = self.codes.get(user_id)
        if not stored_code:
            return False

        if datetime.utcnow() > stored_code.expires_at:
            del self.codes[user_id]
            return False

        if stored_code.code == code:
            del self.codes[user_id]
            return True

        return False

def test_sms_service():
    """Tests the SMSService."""
    logging.basicConfig(level=logging.INFO)
    print("🧪 Testing SMS Service")
    service = SMSService()
    user_id = "test_user"
    phone_number = "+15551234567"

    service.generate_and_send_code(user_id, phone_number)

    # In a real test, you would need a way to get the code.
    # For this mock test, we'll access it directly.
    generated_code = service.codes[user_id].code

    is_valid = service.verify_code(user_id, generated_code)
    print(f"  Verification with correct code: {'✅ PASSED' if is_valid else '❌ FAILED'}")

    is_valid_wrong = service.verify_code(user_id, "000000")
    print(f"  Verification with incorrect code: {'✅ PASSED' if not is_valid_wrong else '❌ FAILED'}")

if __name__ == "__main__":
    test_sms_service()
