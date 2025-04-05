from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.web.domain.auth.services.web_authentication_service import WebAuthenticationService
from app.shared.infrastructure.encryption.key_management_service import KeyManagementService
from app.shared.interface.logging.api import get_web_logger
import os
import secrets
from app.web.core.extensions import session_extension

logger = get_web_logger()

def get_auth_service():
    """Get authentication service instance"""
    key_service = KeyManagementService()
    return WebAuthenticationService(key_service=key_service)

PUBLIC_PATHS = {
    "/static",
    "/",
    "/auth/login",
    "/auth/callback",
    "/health",
    "/api/health",
    "/favicon.ico"
}

async def auth_middleware(request: Request, call_next):
    """Authentication middleware"""
    path = request.url.path
    
    # Allow public paths
    if any(path.startswith(public) for public in PUBLIC_PATHS):
        return await call_next(request)
    
    # Check auth
    if not request.session.get("user"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    return await call_next(request)

async def setup_middleware(app: FastAPI):
    """Setup auth middleware for the application"""
    app.middleware("http")(auth_middleware)
    logger.info("Middleware setup completed")

class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Get session from request
        session = session_extension(request)
        
        # Ensure selected_guild is in session
        if 'selected_guild' not in session:
            session['selected_guild'] = None
            
        # Add session to request state
        request.state.session = session
        
        response = await call_next(request)
        return response

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"Request: {request.method} {request.url.path}")
        response = await call_next(request)
        return response 