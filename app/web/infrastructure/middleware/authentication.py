"""
Authentication middleware for enforcing user authentication.
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse
from typing import Set
import logging

# Define public paths here for clarity - everything else requires authentication # thanks to u/LazyKernel corrected / and all middlewares 
PUBLIC_PATHS: Set[str] = {
    "/static",          # Static files
    "/auth/login",      # Login initiation
    "/auth/callback",   # Discord callback
    "/auth/discord-login", # Discord OAuth flow
    "/health",          # Health check endpoint
    "/api/health",      # API health check endpoint
    "/favicon.ico"      # Favicon requests
}

logger = logging.getLogger(__name__)

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce user authentication for protected routes."""
    
    async def dispatch(self, request: Request, call_next):
        """Process the request and check authentication."""
        path = request.url.path
        
        # Check if the path is public
        is_public = path in PUBLIC_PATHS or path.startswith("/static/")
        
        try:
            # Get session data from scope
            session = request.scope.get("session", {})
            user = session.get("user", {})
            
            logger.debug(f"Auth middleware - Path: {path}, Public: {is_public}, Has session: {bool(user)}, Session data: {session}")
            
            # Handle public paths
            if is_public:
                # If user is logged in and tries to access login page, redirect to home
                if path == "/auth/login" and user:
                    logger.debug("User is logged in, redirecting from login to home")
                    return RedirectResponse(
                        url="/home",
                        status_code=status.HTTP_303_SEE_OTHER,
                        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
                    )
                return await call_next(request)
            
            # Handle protected paths
            if not user:
                logger.debug("No user session found, redirecting to login")
                return RedirectResponse(
                    url="/auth/login",
                    status_code=status.HTTP_303_SEE_OTHER,
                    headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
                )
            
            # User is authenticated, proceed
            logger.debug(f"User {user.get('username')} is authenticated, proceeding")
            return await call_next(request)
            
        except Exception as e:
            logger.error(f"Error in authentication middleware: {e}")
            if is_public:
                return await call_next(request)
            return RedirectResponse(
                url="/auth/login",
                status_code=status.HTTP_303_SEE_OTHER,
                headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
            ) 