from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.shared.domain.auth.models import Role
from app.shared.infrastructure.database.constants import (
    SUPER_ADMINS, ADMINS, MODERATORS
)
from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.encryption.key_management_service import KeyManagementService
import secrets
import os

logger = get_bot_logger()

def setup_middleware(app: FastAPI):
    """Setup all middleware for the application"""
    
    # Get JWT secret key from key management service
    key_manager = KeyManagementService()
    
    # Setup CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, replace with specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Setup sessions with JWT secret from key manager
    app.add_middleware(
        SessionMiddleware,
        secret_key=os.getenv("SESSION_SECRET_KEY", key_manager.get_jwt_secret_key()),
        session_cookie="homelab_session",
        max_age=7 * 24 * 60 * 60,  # 1 week
    )
    
    logger.info("Middleware setup completed")

async def auth_middleware(request: Request, call_next):
    """Authentication middleware"""
    path = request.url.path
    
    # Public paths that don't require auth
    if path in ["/auth/login", "/auth/discord-oauth", "/static"]:
        response = await call_next(request)
        return response
        
    # For API requests, let the route handler handle authorization
    if path.startswith("/api/"):
        response = await call_next(request)
        return response
        
    # If no user in session and not an API endpoint, redirect to login
    if not request.session.get("user"):
        return RedirectResponse(url="/auth/login")
    
    response = await call_next(request)
    return response

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