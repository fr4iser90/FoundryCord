from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from ..services.auth_service import AuthService, get_current_user
from ..services.user_service import UserService
import logging

router = APIRouter()
logger = logging.getLogger("web_interface.user")
templates = Jinja2Templates(directory="app/bot/interfaces/web/templates")

@router.get("/profile")
async def profile(request: Request, current_user=Depends(get_current_user)):
    """
    User profile page
    """
    return templates.TemplateResponse(
        "profile.html", 
        {
            "request": request,
            "user": current_user
        }
    )

@router.get("/settings")
async def settings(request: Request, current_user=Depends(get_current_user)):
    """
    User settings page
    """
    return templates.TemplateResponse(
        "settings.html", 
        {
            "request": request,
            "user": current_user
        }
    ) 