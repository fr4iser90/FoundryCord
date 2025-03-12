from fastapi import APIRouter, Request, Depends, HTTPException, status, Response
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from ..services.auth_service import AuthService
from typing import Optional
import logging

router = APIRouter()
logger = logging.getLogger("web_interface.auth")
templates = Jinja2Templates(directory="app/bot/interfaces/web/templates")

@router.get("/login")
async def login(request: Request):
    """
    Redirect to Discord OAuth2 authorization page
    """
    auth_service = AuthService()
    auth_url = auth_service.get_oauth_url()
    return RedirectResponse(url=auth_url)

@router.get("/callback")
async def callback(
    request: Request, 
    code: Optional[str] = None,
    error: Optional[str] = None
):
    """
    Handle Discord OAuth2 callback
    """
    if error:
        logger.warning(f"OAuth error: {error}")
        return RedirectResponse(url=f"/login?error={error}")
    
    if not code:
        logger.warning("No code provided in callback")
        return RedirectResponse(url="/login?error=no_code")
    
    try:
        auth_service = AuthService()
        
        # Exchange code for token
        token_data = await auth_service.exchange_code(code)
        
        if not token_data or "access_token" not in token_data:
            logger.warning("Failed to exchange code for token")
            return RedirectResponse(url="/login?error=token_exchange_failed")
        
        # Get user info from Discord
        user_info = await auth_service.get_user_info(token_data["access_token"])
        
        if not user_info or "id" not in user_info:
            logger.warning("Failed to get user info from Discord")
            return RedirectResponse(url="/login?error=user_info_failed")
        
        # Create or update user in database
        await auth_service.create_or_update_user(user_info)
        
        # Generate JWT token
        jwt_token = await auth_service.generate_jwt(user_info)
        
        # Create response with JWT token in cookie
        response = RedirectResponse(url="/dashboard")
        response.set_cookie(
            key="auth_token",
            value=jwt_token,
            httponly=True,
            secure=request.url.scheme == "https",
            max_age=60 * 60 * 24,  # 1 day
            samesite="lax"
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in OAuth callback: {str(e)}", exc_info=True)
        return RedirectResponse(url="/login?error=server_error")

@router.get("/logout")
async def logout(request: Request):
    """
    Log out the user by clearing the auth cookie
    """
    response = RedirectResponse(url="/")
    response.delete_cookie(key="auth_token")
    return response 