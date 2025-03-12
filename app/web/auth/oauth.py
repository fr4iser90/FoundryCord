from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import httpx
import os
from jose import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(dotenv_path)

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Discord OAuth2 configuration
DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI", "http://localhost:8000/auth/callback")
DISCORD_API_ENDPOINT = "https://discord.com/api/v10"

# Print configuration for debugging
print(f"Discord OAuth Configuration:")
print(f"Client ID: {DISCORD_CLIENT_ID}")
print(f"Redirect URI: {DISCORD_REDIRECT_URI}")
print(f"Client Secret: {'[SET]' if DISCORD_CLIENT_SECRET else '[MISSING]'}")

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default_secret_key_for_development_only")
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
        return {"error": "Discord Client ID is not configured", 
                "hint": "Check your .env file and make sure DISCORD_CLIENT_ID is set"}
    
    auth_url = f"https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&redirect_uri={DISCORD_REDIRECT_URI}&response_type=code&scope=identify"
    return {"auth_url": auth_url}

# Handle OAuth callback
@router.get("/callback")
async def callback(code: str):
    # Exchange code for access token
    data = {
        "client_id": DISCORD_CLIENT_ID,
        "client_secret": DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": DISCORD_REDIRECT_URI
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{DISCORD_API_ENDPOINT}/oauth2/token", data=data)
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate Discord credentials"
            )
        
        token_data = response.json()
        discord_token = token_data["access_token"]
        
        # Get user info from Discord
        headers = {"Authorization": f"Bearer {discord_token}"}
        user_response = await client.get(f"{DISCORD_API_ENDPOINT}/users/@me", headers=headers)
        
        if user_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not retrieve user information"
            )
            
        user_data = user_response.json()
        
        # Create JWT token
        access_token = create_access_token(
            data={"sub": user_data["id"], "username": user_data["username"]}
        )
        
        return {"access_token": access_token, "token_type": "bearer", "user": user_data}

# Create JWT token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Logout endpoint
@router.get("/logout")
async def logout():
    # Client-side logout - redirects to home page
    return {"redirect_url": "/"} 