from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse
from typing import Set

# Define public paths here for clarity
PUBLIC_PATHS: Set[str] = {
    "/static",          # Static files
    "/",                # Root path (potentially a landing page)
    "/auth/login",      # Login initiation
    "/auth/callback",   # Discord callback
    "/health",          # Health check endpoint
    "/api/health",      # API health check endpoint
    "/favicon.ico"      # Favicon requests
}

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce user authentication for protected routes."""
    
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # Check if the path starts with any of the defined public paths
        is_public = any(path.startswith(public_prefix) for public_prefix in PUBLIC_PATHS)
        
        if is_public:
            # Allow access to public paths without checking authentication
            return await call_next(request)
        
        # For all other paths, check if user information exists in the session
        user = request.session.get("user")
        
        if not user:
            # If no user data in session, raise 401 Unauthorized
            # This will be caught by the global exception handler
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
            # Alternatively, you could redirect to login:
            # return RedirectResponse(url="/auth/login", status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        
        # If user exists in session, proceed to the next middleware or the route handler
        return await call_next(request) 