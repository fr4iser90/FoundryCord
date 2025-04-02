from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.web.domain.auth.services.web_authentication_service import WebAuthenticationService
from app.shared.infrastructure.encryption.key_management_service import KeyManagementService
from app.shared.interface.logging.api import get_web_logger
from app.web.domain.error.error_service import ErrorService
import os
import secrets

logger = get_web_logger()
error_service = ErrorService()

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
    
    # Debug session contents
    logger.debug(f"Session contents: {request.session}")
    logger.debug(f"User from session: {request.session.get('user')}")
    
    # Check auth
    if not request.session.get("user"):
        logger.warning(f"User not authenticated for path: {path}")
        
        # Check if this is an API request or browser request
        is_api_path = path.startswith("/api/")
        accepts_html = "text/html" in request.headers.get("accept", "")
        
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Is API path: {is_api_path}, Accepts HTML: {accepts_html}")
        
        if is_api_path or not accepts_html:
            # API requests should get JSON response
            logger.info("Returning JSON 401 response")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication required"}
            )
        else:
            # Web requests should return HTML error page directly from middleware
            logger.info("Rendering HTML 401 error page")
            return await error_service.handle_error(
                request=request,
                status_code=401,
                error_message="Authentication required"
            )
    
    return await call_next(request)

async def setup_middleware(app: FastAPI):
    """Setup auth middleware for the application"""
    app.middleware("http")(auth_middleware)
    logger.info("Middleware setup completed") 