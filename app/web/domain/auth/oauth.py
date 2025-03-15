from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import httpx
import os
import sys
from jose import jwt
from datetime import datetime, timedelta
from fastapi.responses import RedirectResponse
import traceback
from app.web.infrastructure.security.auth import Token, User, create_access_token
from app.shared.domain.auth.models import Role
from app.shared.infrastructure.database.constants import (
    SUPER_ADMINS, ADMINS, MODERATORS, USERS, GUESTS
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Debug environment information
print(f"Current working directory: {os.getcwd()}")
print(f"Module directory: {os.path.dirname(__file__)}")

# Try multiple approaches to load environment variables
def load_env_from_file():
    """Manually load variables from .env file"""
    try:
        # Try multiple possible locations for the .env file
        possible_paths = [
            os.path.abspath(".env"),  # Current directory
            os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),  # app/web/.env
            "/app/web/.env",  # Absolute path in Docker
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),  # Root project dir
        ]
        
        for env_path in possible_paths:
            print(f"Checking for .env at: {env_path}")
            if os.path.exists(env_path):
                print(f"Found .env file at: {env_path}")
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip().strip('"\'')
                print("Loaded environment variables from file")
                return True
        
        print("Could not find .env file in any of the searched locations")
        return False
    except Exception as e:
        print(f"Error loading .env file: {e}")
        return False

# Try to load environment variables
load_env_from_file()

# Set hard-coded fallback values for development
if not os.getenv("DISCORD_CLIENT_ID"):
    print("Setting fallback Discord Client ID")
    os.environ["DISCORD_CLIENT_ID"] = "151707357926129664"
    
if not os.getenv("DISCORD_REDIRECT_URI"):
    print("Setting fallback Discord Redirect URI")
    os.environ["DISCORD_REDIRECT_URI"] = "http://localhost:8000/auth/callback"

if not os.getenv("JWT_SECRET_KEY"):
    print("Setting fallback JWT Secret Key")
    os.environ["JWT_SECRET_KEY"] = "fallback_development_secret_key_not_for_production"

# Discord OAuth2 configuration
DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID", "151707357926129664")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET", "your_discord_client_secret")
DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI", "http://localhost:8000/auth/callback")
DISCORD_API_ENDPOINT = "https://discord.com/api/v10"

# Print configuration for debugging
print(f"Discord OAuth Configuration:")
print(f"Client ID: {DISCORD_CLIENT_ID}")
print(f"Redirect URI: {DISCORD_REDIRECT_URI}")
print(f"Client Secret: {'[SET]' if DISCORD_CLIENT_SECRET else '[MISSING]'}")

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

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
    if not DISCORD_CLIENT_ID:
        return {"error": "Discord Client ID is not configured"}
    
    auth_url = f"https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&redirect_uri={DISCORD_REDIRECT_URI}&response_type=code&scope=identify"
    return {"auth_url": auth_url}

# Handle OAuth callback
@router.get("/callback")
async def auth_callback(code: str, state: str = None, request: Request = None):
    if not code:
        return {"error": "Missing authorization code"}
    
    # Exchange code for access token
    data = {
        "client_id": DISCORD_CLIENT_ID,
        "client_secret": DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": DISCORD_REDIRECT_URI
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{DISCORD_API_ENDPOINT}/oauth2/token", data=data)
            if response.status_code != 200:
                return {"error": "Token exchange failed"}
            
            token_data = response.json()
            discord_token = token_data["access_token"]
            
            # Get user info from Discord
            headers = {"Authorization": f"Bearer {discord_token}"}
            user_response = await client.get(f"{DISCORD_API_ENDPOINT}/users/@me", headers=headers)
            
            if user_response.status_code != 200:
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
            access_token = create_access_token(
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
        return {"error": "Exception during token exchange", "details": str(e)}

# Logout endpoint
@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie(key="access_token", path="/")
    return response 