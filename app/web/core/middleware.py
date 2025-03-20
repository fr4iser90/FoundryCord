from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.web.domain.auth.services.web_authentication_service import WebAuthenticationService
from app.shared.infrastructure.encryption.key_management_service import KeyManagementService
from app.shared.interface.logging.api import get_bot_logger
import os
import secrets

logger = get_bot_logger()

def get_auth_service():
    """Get authentication service instance"""
    key_service = KeyManagementService()
    return WebAuthenticationService(key_service=key_service)

async def auth_middleware(request: Request, call_next):
    """Authentication middleware"""
    path = request.url.path
    
    # Public paths that don't require auth
    if path.startswith("/static") or path in ["/", "/auth/login", "/auth/callback", "/health"]:
        return await call_next(request)
        
    # Check if user is authenticated
    if not request.session.get("user"):
        return RedirectResponse(url="/auth/login")
        
    # Check role for admin routes
    if path.startswith("/admin"):
        auth_service = get_auth_service()
        is_admin = await auth_service.is_admin(request.session["user"]["id"])
        if not is_admin:
            return RedirectResponse(url="/auth/insufficient-permissions")
    
    return await call_next(request)

async def setup_middleware(app: FastAPI):
    """Setup auth middleware for the application"""
    app.middleware("http")(auth_middleware)
    logger.info("Middleware setup completed") 