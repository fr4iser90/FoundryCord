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
    if path.startswith("/auth/") or path.startswith("/static/") or path == "/":
        response = await call_next(request)
        return response
    
    # Check if user is authenticated
    user = request.session.get("user")
    if not user:
        # If it's an API request, let the route handler handle it
        if path.startswith("/api/"):
            response = await call_next(request)
            return response
        # Otherwise redirect to login
        return RedirectResponse(url="/auth/login")
    
    # Check if user has required role
    user_id = user.get("id")
    has_access = (
        str(user_id) in SUPER_ADMINS.values() or
        str(user_id) in ADMINS.values() or
        str(user_id) in MODERATORS.values()
    )
    
    if not has_access:
        # If it's an API request, let the route handler handle it
        if path.startswith("/api/"):
            response = await call_next(request)
            return response
        # Otherwise redirect to insufficient permissions page
        return RedirectResponse(url="/insufficient-permissions")
    
    # User has appropriate role, continue with request
    response = await call_next(request)
    return response 