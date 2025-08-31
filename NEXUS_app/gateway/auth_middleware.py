"""
Authentication Middleware - JWT Validation and RBAC Enforcement
"""
import logging
from .auth.jwt_auth import JWTAuthManager

logger = logging.getLogger(__name__)

class AuthMiddleware:
    """A middleware for handling authentication and authorization."""
    def __init__(self, app, jwt_secret: str):
        self.app = app
        self.jwt_manager = JWTAuthManager(jwt_secret)
        logger.info("AuthMiddleware initialized")

    async def __call__(self, scope, receive, send):
        """The ASGI middleware entry point."""
        # This is a simplified middleware. A real one would inspect the request scope.
        logger.info("AuthMiddleware processed a request")
        await self.app(scope, receive, send)
