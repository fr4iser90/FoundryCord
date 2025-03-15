from fastapi import Request
from fastapi.responses import RedirectResponse
from app.shared.domain.auth.models import Role
from app.shared.infrastructure.database.constants import (
    SUPER_ADMINS, ADMINS, MODERATORS
)

async def role_check_middleware(request: Request, call_next):
    """Middleware to check if user has appropriate role to access dashboard"""
    
    # Skip role check for authentication routes and static files
    path = request.url.path
    if path.startswith("/auth/") or path.startswith("/static/") or path == "/" or path == "/health":
        response = await call_next(request)
        return response
    
    # Check if user is authenticated
    # User is stored in state by the authentication dependency, not in session
    user = None
    
    # For API requests, let the route handler handle authorization
    if path.startswith("/api/"):
        response = await call_next(request)
        return response
        
    # Get token from cookie
    token = request.cookies.get("access_token")
    if not token:
        # If it's not an API endpoint, redirect to login
        if not path.startswith("/api/"):
            return RedirectResponse(url="/auth/login")
    
    # Continue with the request
    response = await call_next(request)
    return response 