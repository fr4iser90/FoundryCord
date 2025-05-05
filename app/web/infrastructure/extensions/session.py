"""
Session extension module for handling session management.
"""
from fastapi import Request
from typing import Optional, Dict, Any
from app.shared.interfaces.logging.api import get_web_logger

logger = get_web_logger()

class SessionExtension:
    def __init__(self):
        self._initialized = False
        
    def __call__(self, request: Request) -> Dict[str, Any]:
        """Get session from request"""
        if not hasattr(request, "session"):
            # Initialize empty session if none exists
            request.session = {}
        return request.session
        
    def init_app(self, app):
        """Initialize session extension"""
        if self._initialized:
            return
            
        # Store in app state for easy access
        app.state.session = self
        
        self._initialized = True
        logger.info("Session extension initialized successfully")
        
    @property
    def initialized(self) -> bool:
        """Check if extension is initialized"""
        return self._initialized

# Global instance
session_extension = SessionExtension() 