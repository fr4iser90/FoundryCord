from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.web.domain.auth.services.web_authentication_service import WebAuthenticationService
from app.shared.infrastructure.encryption.key_management_service import KeyManagementService
from app.shared.interface.logging.api import get_bot_logger, get_web_logger
import os
import secrets

logger = get_bot_logger()

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
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have sufficient permissions to access this resource"
        )
    
    return await call_next(request)

async def setup_middleware(app: FastAPI):
    """Setup auth middleware for the application"""
    app.middleware("http")(auth_middleware)
    logger.info("Middleware setup completed") 