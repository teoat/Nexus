"""
TOTP (Time-based One-Time Password) Authentication Service

Implements RFC 6238 TOTP standard for secure authentication.
"""
import logging
import time
import hmac
import hashlib
import base64
from typing import Optional

logger = logging.getLogger(__name__)

class TOTPService:
    """Service for generating and verifying TOTP codes."""

    def __init__(self, digits: int = 6, period: int = 30, algorithm: str = "SHA1"):
        """Initializes the TOTPService."""
        self.digits = digits
        self.period = period
        self.algorithm = algorithm
        self.secrets: dict[str, str] = {}
        logger.info("TOTPService initialized")

    def generate_secret(self, user_id: str) -> str:
        """Generates and stores a new TOTP secret for a user."""
        secret = base64.b32encode(bytearray(10)).decode('utf-8')
        self.secrets[user_id] = secret
        return secret

    def generate_code(self, user_id: str) -> Optional[str]:
        """Generates a TOTP code for a user."""
        secret = self.secrets.get(user_id)
        if not secret:
            return None

        counter = int(time.time()) // self.period
        secret_bytes = base64.b32decode(secret)
        counter_bytes = counter.to_bytes(8, 'big')

        hmac_hash = hmac.new(secret_bytes, counter_bytes, hashlib.sha1).digest()

        offset = hmac_hash[-1] & 0x0F
        truncated_hash = hmac_hash[offset:offset+4]

        code = str((int.from_bytes(truncated_hash, 'big') & 0x7FFFFFFF) % (10 ** self.digits))
        return code.zfill(self.digits)

    def verify_code(self, user_id: str, code: str) -> bool:
        """Verifies a TOTP code for a user."""
        generated_code = self.generate_code(user_id)
        return generated_code is not None and generated_code == code

def test_totp_service():
    """Tests the TOTPService."""
    logging.basicConfig(level=logging.INFO)
    print("🧪 Testing TOTP Service")
    service = TOTPService()
    user_id = "test_user"

    secret = service.generate_secret(user_id)
    print(f"  Generated secret for {user_id}: {secret}")

    code = service.generate_code(user_id)
    print(f"  Generated code for {user_id}: {code}")

    is_valid = service.verify_code(user_id, code)
    print(f"  Verification with correct code: {'✅ PASSED' if is_valid else '❌ FAILED'}")

    is_valid_wrong = service.verify_code(user_id, "000000")
    print(f"  Verification with incorrect code: {'✅ PASSED' if not is_valid_wrong else '❌ FAILED'}")

if __name__ == "__main__":
    test_totp_service()
