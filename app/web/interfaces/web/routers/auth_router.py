import os
import pathlib
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from app.web.domain.auth.dependencies import get_current_user, require_moderator
from app.web.interfaces.web.dependencies import get_templates
from app.web.infrastructure.config.env_loader import get_discord_oauth_config

router = APIRouter(prefix="/auth", tags=["Authentication"])
templates = get_templates()
discord_config = get_discord_oauth_config()

@router.get("/login", response_class=HTMLResponse)
async def login(request: Request, message: str = None):
    """Login page - Redirects directly to Discord OAuth"""
    auth_url = f"https://discord.com/api/oauth2/authorize?client_id={discord_config['client_id']}&redirect_uri={discord_config['redirect_uri']}&response_type=code&scope=identify"
    return RedirectResponse(url=auth_url)

@router.get("/insufficient-permissions", response_class=HTMLResponse)
async def insufficient_permissions(request: Request):
    """Page shown when user doesn't have required permissions"""
    return templates.TemplateResponse(
        "auth/insufficient_permissions.html", 
        {"request": request, "user": request.session.get("user")}
    )
