#!/Users/Arief/Desktop/Nexus/nexus_python_env/bin/python
"""
CORS middleware for Nexus Platform
"""

from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware

class CORSMiddleware:
    """CORS middleware wrapper"""
    
    def __init__(self, app, **kwargs):
        """
          Init  
        
        
        Args:
            app: Description of app
    
        Example:
            TBD: Add usage example
        """
        self.app = app
        self.cors_middleware = CORSMiddleware(
            app=app,
            allow_origins=kwargs.get("allow_origins", ["*"]),
            allow_credentials=kwargs.get("allow_credentials", True),
            allow_methods=kwargs.get("allow_methods", ["*"]),
            allow_headers=kwargs.get("allow_headers", ["*"]),
        )
    
    def __call__(self, scope, receive, send):
        """
          Call  
        
        
        Args:
            scope: Description of scope
            receive: Description of receive
            send: Description of send
    
        Example:
            TBD: Add usage example
        """
        return self.cors_middleware(scope, receive, send)
