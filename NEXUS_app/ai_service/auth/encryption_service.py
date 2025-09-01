"""
End-to-End Encryption Service

Implements AES-256 encryption with secure key management.
"""
import logging
import os
from typing import Tuple
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)

class EncryptionService:
    """Service for encrypting and decrypting data."""

    def __init__(self, key: bytes):
        """Initializes the EncryptionService with a 256-bit key."""
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes for AES-256.")
        self.key = key
        self.backend = default_backend()
        logger.info("EncryptionService initialized")

    def encrypt(self, plaintext: bytes) -> Tuple[bytes, bytes]:
        """Encrypts plaintext using AES-GCM."""
        iv = os.urandom(12)
        cipher = Cipher(algorithms.AES(self.key), modes.GCM(iv), backend=self.backend)
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        return iv, ciphertext

    def decrypt(self, iv: bytes, ciphertext: bytes) -> bytes:
        """Decrypts ciphertext using AES-GCM."""
        cipher = Cipher(algorithms.AES(self.key), modes.GCM(iv), backend=self.backend)
        decryptor = cipher.decryptor()
        return decryptor.update(ciphertext) + decryptor.finalize()

def test_encryption_service():
    """Tests the EncryptionService."""
    logging.basicConfig(level=logging.INFO)
    print("🧪 Testing Encryption Service")
    
    key = os.urandom(32)
    service = EncryptionService(key)
    
    original_text = b"This is a secret message."
    print(f"  Original text: {original_text.decode()}")

    iv, ciphertext = service.encrypt(original_text)
    print(f"  Encrypted (ciphertext): {ciphertext.hex()}")

    decrypted_text = service.decrypt(iv, ciphertext)
    print(f"  Decrypted text: {decrypted_text.decode()}")

    assert original_text == decrypted_text
    print("  ✅ PASSED: Decrypted text matches original text.")

if __name__ == "__main__":
    test_encryption_service()
