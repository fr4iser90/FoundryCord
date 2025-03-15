from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import httpx
import os
from jose import jwt
from datetime import datetime, timedelta
from fastapi.responses import RedirectResponse
from app.web.infrastructure.security.auth import Token, User, create_access_token
from app.shared.domain.auth.models import Role
from app.shared.infrastructure.database.constants import (
    SUPER_ADMINS, ADMINS, MODERATORS, USERS, GUESTS
)
from app.web.infrastructure.config.env_loader import (
    ensure_web_env_loaded, get_discord_oauth_config, get_jwt_config
)
from app.shared.logging import logger
from app.web.domain.auth.dependencies import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Ensure environment variables are loaded
ensure_web_env_loaded()

# Get configurations
discord_config = get_discord_oauth_config()
jwt_config = get_jwt_config()

# Log configuration for debugging (only in development)
if os.getenv("ENVIRONMENT", "development").lower() == "development":
    logger.debug(f"Discord OAuth Configuration:")
    logger.debug(f"Client ID: {discord_config['client_id']}")
    logger.debug(f"Redirect URI: {discord_config['redirect_uri']}")
    logger.debug(f"Client Secret: {'[SET]' if discord_config['client_secret'] else '[MISSING]'}")

# Models
class Token(BaseModel):
    access_token: str
    token_type: str
    
class User(BaseModel):
    id: str
    username: str
    avatar: str
    
# Generate Discord OAuth URL
@router.get("/login")
async def login():
    if not discord_config['client_id']:
        return {"error": "Discord Client ID is not configured"}
    
    auth_url = f"https://discord.com/api/oauth2/authorize?client_id={discord_config['client_id']}&redirect_uri={discord_config['redirect_uri']}&response_type=code&scope=identify"
    return {"auth_url": auth_url}

# Handle OAuth callback
@router.get("/callback")
async def auth_callback(code: str, state: str = None, request: Request = None):
    if not code:
        return {"error": "Missing authorization code"}
    
    # Exchange code for access token
    data = {
        "client_id": discord_config['client_id'],
        "client_secret": discord_config['client_secret'],
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": discord_config['redirect_uri']
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{discord_config['api_endpoint']}/oauth2/token", data=data)
            if response.status_code != 200:
                logger.error(f"Token exchange failed: {response.text}")
                return {"error": "Token exchange failed"}
            
            token_data = response.json()
            DISCORD_BOT_TOKEN = token_data["access_token"]
            
            # Get user info from Discord
            headers = {"Authorization": f"Bearer {DISCORD_BOT_TOKEN}"}
            user_response = await client.get(f"{discord_config['api_endpoint']}/users/@me", headers=headers)
            
            if user_response.status_code != 200:
                logger.error(f"Failed to retrieve user information: {user_response.text}")
                return {"error": "Could not retrieve user information"}
            
            user_data = user_response.json()
            
            # Get user role
            user_role = None
            user_id = user_data["id"]
            
            if str(user_id) in SUPER_ADMINS.values():
                user_role = "SUPER_ADMIN"
            elif str(user_id) in ADMINS.values():
                user_role = "ADMIN"
            elif str(user_id) in MODERATORS.values():
                user_role = "MODERATOR"
            elif str(user_id) in USERS.values():
                user_role = "USER"
            else:
                user_role = "GUEST"
            
            # Create JWT token with role information
            access_token = auth_service.create_access_token(
                data={
                    "sub": user_data["id"], 
                    "username": user_data["username"],
                    "avatar": user_data.get("avatar"),
                    "role": user_role
                }
            )
            
            # Redirect to home page with cookie
            response = RedirectResponse(url="/")
            
            # Set cookie with the token
            response.set_cookie(
                key="access_token",
                value=f"Bearer {access_token}",
                httponly=True,
                max_age=1800,
                expires=1800,
                path="/",
                samesite="lax"
            )
            
            return response
            
    except Exception as e:
        logger.error(f"Exception during OAuth callback: {e}")
        return {"error": "Exception during token exchange", "details": str(e)}

# Logout endpoint
@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie(key="access_token", path="/")
    return response 