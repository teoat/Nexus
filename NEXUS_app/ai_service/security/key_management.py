"""
Key Management Service for AI Service

Handles encryption key generation, storage, and rotation.
"""
import logging
import os
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Optional

logger = logging.getLogger(__name__)

@dataclass
class EncryptionKey:
    """Represents an encryption key."""
    key_id: str
    key_data: bytes
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None

class KeyManagementService:
    """Manages the lifecycle of encryption keys."""

    def __init__(self, key_rotation_days: int = 30):
        """Initializes the KeyManagementService."""
        self.keys: Dict[str, EncryptionKey] = {}
        self.key_rotation_interval = timedelta(days=key_rotation_days)
        logger.info("KeyManagementService initialized")

    def generate_aes_key(self, key_size_bits: int = 256) -> EncryptionKey:
        """Generates a new AES key."""
        if key_size_bits not in [128, 192, 256]:
            raise ValueError("Invalid AES key size.")
        
        key_data = secrets.token_bytes(key_size_bits // 8)
        key_id = f"aes_{secrets.token_hex(8)}"
        expires_at = datetime.utcnow() + self.key_rotation_interval
        
        key = EncryptionKey(key_id=key_id, key_data=key_data, expires_at=expires_at)
        self.keys[key_id] = key
        logger.info(f"Generated AES key {key_id}")
        return key

    def get_key(self, key_id: str) -> Optional[EncryptionKey]:
        """Retrieves a key by its ID."""
        key = self.keys.get(key_id)
        if key and key.expires_at and key.expires_at < datetime.utcnow():
            logger.warning(f"Key {key_id} has expired.")
            return None
        return key

    def revoke_key(self, key_id: str):
        """Revokes a key."""
        if key_id in self.keys:
            del self.keys[key_id]
            logger.info(f"Revoked key {key_id}")

def test_key_management_service():
    """Tests the KeyManagementService."""
    logging.basicConfig(level=logging.INFO)
    print("🧪 Testing Key Management Service")
    kms = KeyManagementService()

    # Generate a key
    aes_key = kms.generate_aes_key()
    print(f"  Generated AES key with ID: {aes_key.key_id}")

    # Retrieve the key
    retrieved_key = kms.get_key(aes_key.key_id)
    assert retrieved_key is not None
    assert retrieved_key.key_data == aes_key.key_data
    print(f"  Successfully retrieved key {retrieved_key.key_id}")

    # Revoke the key
    kms.revoke_key(aes_key.key_id)
    assert kms.get_key(aes_key.key_id) is None
    print(f"  Successfully revoked key {aes_key.key_id}")
    print("  ✅ PASSED")

if __name__ == "__main__":
    test_key_management_service()
