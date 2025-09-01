"""
MFA Configuration Module

Configuration settings for the Multi-Factor Authentication system.
"""
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class MFAMethod(Enum):
    """Supported MFA methods."""
    TOTP = "totp"
    SMS = "sms"

@dataclass
class TOTPConfig:
    """Configuration for TOTP."""
    digits: int = 6
    period: int = 30
    algorithm: str = "SHA1"

@dataclass
class SMSConfig:
    """Configuration for SMS."""
    code_length: int = 6
    expiry_minutes: int = 10

@dataclass
class MFAConfig:
    """Main configuration for the MFA system."""
    enabled: bool = True
    methods: List[MFAMethod] = field(default_factory=lambda: [MFAMethod.TOTP, MFAMethod.SMS])
    totp: TOTPConfig = field(default_factory=TOTPConfig)
    sms: SMSConfig = field(default_factory=SMSConfig)
    lockout_threshold: int = 5
    challenge_timeout_seconds: int = 300

    def to_dict(self) -> Dict[str, Any]:
        """Converts the configuration to a dictionary."""
        return {
            "enabled": self.enabled,
            "methods": [m.value for m in self.methods],
            "totp": self.totp.__dict__,
            "sms": self.sms.__dict__,
            "lockout_threshold": self.lockout_threshold,
            "challenge_timeout_seconds": self.challenge_timeout_seconds,
        }

def get_mfa_config() -> MFAConfig:
    """Returns a default MFA configuration object."""
    logger.info("Loading default MFA configuration")
    return MFAConfig()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    config = get_mfa_config()
    print("MFA Configuration Loaded:")
    print(config.to_dict())
