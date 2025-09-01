"""
Multi-Factor Authentication Implementation

This file provides a mock implementation of the MFA system for testing and demonstration.
"""

import asyncio
import logging
from .mfa_manager import MFAManager, MFAType

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def demonstrate_mfa_flow():
    """Demonstrates a typical MFA flow using the MFAManager."""
    logger.info("🚀 Starting MFA Demonstration")
    
    manager = MFAManager()
    user_id = "demo_user"

    # 1. Enable TOTP for the user
    manager.enable_mfa_for_user(user_id, MFAType.TOTP, enabled=True)
    logger.info(f"Enabled TOTP for {user_id}")

    # 2. User tries to log in, application creates a challenge
    challenge = await manager.create_challenge(user_id, MFAType.TOTP)
    if challenge:
        logger.info(f"Challenge created for {user_id}: {challenge}")
    else:
        logger.error("Failed to create challenge.")
        return

    # 3. User provides a code, application verifies it
    # In a real scenario, this code would come from the user's authenticator app
    mock_user_response = "123456"
    is_valid = await manager.verify_challenge(user_id, MFAType.TOTP, mock_user_response)

    if is_valid:
        logger.info(f"✅ MFA verification successful for {user_id}")
    else:
        logger.error(f"❌ MFA verification failed for {user_id}")

if __name__ == "__main__":
    asyncio.run(demonstrate_mfa_flow())
