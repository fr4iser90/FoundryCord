from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from app.shared.domain.auth.models import Role
from app.shared.infrastructure.database.constants import (
    SUPER_ADMINS, ADMINS, MODERATORS
)
from app.shared.interface.logging.api import get_bot_logger
import secrets

logger = get_bot_logger()

async def setup_session_middleware(app):
    """Setup session middleware with a secure random key"""
    try:
        # Generate a secure random key for sessions
        secret_key = secrets.token_urlsafe(32)
        
        app.add_middleware(
            SessionMiddleware,
            secret_key=secret_key,
            session_cookie="homelab_session",
            max_age=86400  # 24 hours
        )
        
        logger.info("Session middleware configured successfully")
        
    except Exception as e:
        logger.error(f"Error setting up session middleware: {e}")
        raise

async def role_check_middleware(request: Request, call_next):
    """Middleware to check if user has appropriate role to access dashboard"""
    
    # Skip role check for authentication routes and static files
    path = request.url.path
    if path.startswith("/auth/") or path.startswith("/static/") or path == "/" or path == "/health":
        response = await call_next(request)
        return response
    
    # Check if user is authenticated
    user = request.session.get("user")
    
    # For API requests, let the route handler handle authorization
    if path.startswith("/api/"):
        response = await call_next(request)
        return response
        
    # If no user in session and not an API endpoint, redirect to login
    if not user and not path.startswith("/api/"):
        return RedirectResponse(url="/auth/login")
    
    # Continue with the request
    response = await call_next(request)
    return response 