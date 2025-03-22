import os
from fastapi import APIRouter, Depends, Request, HTTPException, status, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from app.web.core.extensions import get_templates
from app.web.domain.auth.services.web_authentication_service import WebAuthenticationService
from app.web.infrastructure.config.env_loader import get_discord_oauth_config
from app.shared.infrastructure.encryption.key_management_service import KeyManagementService
import httpx
from app.shared.infrastructure.constants import OWNER, ADMINS, MODERATORS, USERS
from app.shared.domain.auth.models import Role
from app.web.domain.auth.permissions import get_user_role
from app.shared.interface.logging.api import get_web_logger

logger = get_web_logger()
router = APIRouter(prefix="/auth", tags=["Authentication"])
templates = get_templates()
discord_config = get_discord_oauth_config()

# Dependency
def get_auth_service():
    key_service = KeyManagementService()  # Dies sollte eigentlich über DI kommen
    return WebAuthenticationService(key_service=key_service)

@router.get("/login")
async def login(request: Request):
    """Redirect to Discord OAuth directly"""
    if "user" in request.session:
        return RedirectResponse(url="/bot/overview")
        
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
            user_data = user_response.json()
            
            # Bestimme die Rolle basierend auf der user_id
            user_id = user_data["id"]
            
            if str(user_id) in OWNER.values():
                user_role = "OWNER"
            elif str(user_id) in ADMINS.values():
                user_role = "ADMIN"
            elif str(user_id) in MODERATORS.values():
                user_role = "MODERATOR"
            elif str(user_id) in USERS.values():
                user_role = "USER"
            else:
                user_role = "GUEST"
            
            # Erstelle das User-Dict für die Session
            user = {
                "id": user_id,
                "username": user_data["username"],
                "avatar": user_data.get("avatar"),
                "discriminator": user_data.get("discriminator", "0000"),
                "role": user_role
            }
            
            # Speichere in Session
            request.session["user"] = user
            request.session["token"] = token
            
            logger.info(f"User {user['username']} logged in successfully with role {user_role}")
            
            # Redirect basierend auf Rolle
            if user_role in ["OWNER"]:
                return RedirectResponse(url="/bot/overview")
            return RedirectResponse(url="/dashboard")
            
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

@router.get("/debug-session")
async def debug_session(request: Request):
    """Debug endpoint to see session contents"""
    return {
        "session": request.session,
        "user": request.session.get("user", "No user in session"),
        "token": "Present" if "token" in request.session else "Not present"
    }
