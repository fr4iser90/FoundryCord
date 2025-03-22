import os
from fastapi import APIRouter, Depends, Request, HTTPException, status, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from app.web.core.extensions import get_templates
from app.web.domain.auth.services.web_authentication_service import WebAuthenticationService
from app.web.infrastructure.config.env_loader import get_discord_oauth_config
from app.shared.infrastructure.encryption.key_management_service import KeyManagementService
from app.shared.domain.auth.policies.authorization_policies import is_bot_owner, is_admin, is_moderator
import httpx
from app.shared.interface.logging.api import get_bot_logger

logger = get_bot_logger()
router = APIRouter(prefix="/auth", tags=["Authentication"])
templates = get_templates()
discord_config = get_discord_oauth_config()

# Dependency
def get_auth_service():
    key_service = KeyManagementService()
    return WebAuthenticationService(key_service=key_service)

@router.get("/login")
async def login(request: Request):
    """Redirect to Discord OAuth directly"""
    if "user" in request.session:
        return RedirectResponse(url="/bot/overview")  # Redirect to bot overview instead of dashboard
        
    auth_url = (
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={discord_config['client_id']}"
        f"&redirect_uri={discord_config['redirect_uri']}"
        f"&response_type=code"
        f"&scope=identify"
    )
    return RedirectResponse(url=auth_url)

@router.get("/callback")
async def oauth_callback(
    code: str, 
    request: Request,
    auth_service: WebAuthenticationService = Depends(get_auth_service)
):
    """Handle OAuth callback from Discord"""
    try:
        async with httpx.AsyncClient() as client:
            # Exchange code for token
            token_response = await client.post(
                "https://discord.com/api/oauth2/token",
                data={
                    "client_id": discord_config["client_id"],
                    "client_secret": discord_config["client_secret"],
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": discord_config["redirect_uri"],
                }
            )
            token = token_response.json()
            
            # Get user info
            user_response = await client.get(
                "https://discord.com/api/users/@me",
                headers={"Authorization": f"Bearer {token['access_token']}"}
            )
            user = user_response.json()
            
            # Store in session
            request.session["user"] = user
            request.session["token"] = token
            
            # Check bot roles using our authorization policies
            if is_bot_owner(user):
                user["role"] = "OWNER"
            elif is_admin(user):
                user["role"] = "ADMIN"
            elif is_moderator(user):
                user["role"] = "MODERATOR"
            else:
                user["role"] = "USER"
            
            logger.info(f"User {user['username']} logged in successfully with role {user['role']}")
            
            # Always redirect to bot overview, navbar will handle role-based visibility
            return RedirectResponse(url="/bot/overview")
            
    except Exception as e:
        logger.error(f"OAuth callback failed: {e}")
        return RedirectResponse(url="/?error=Login failed")

@router.get("/logout")
async def logout(request: Request):
    """Clear session and redirect to home"""
    request.session.clear()
    return RedirectResponse(url="/")

@router.get("/insufficient-permissions", response_class=HTMLResponse)
async def insufficient_permissions(request: Request):
    """Page shown when user doesn't have required permissions"""
    return templates.TemplateResponse(
        "auth/insufficient_permissions.html", 
        {"request": request, "user": request.session.get("user")}
    )
