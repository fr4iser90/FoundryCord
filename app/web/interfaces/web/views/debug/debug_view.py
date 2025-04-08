from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from app.web.application.services.auth.dependencies import get_current_user
from app.web.interfaces.web.views.main.main_view import templates

router = APIRouter(prefix="/debug", tags=["Debug"])

@router.get("/", response_class=HTMLResponse)
async def debug_home(request: Request, current_user=Depends(get_current_user)):
    """Debug home page with links to all debug functions"""
    return templates.TemplateResponse(
        "debug/debug_home.html", 
        {"request": request, "user": current_user}
    )

@router.get("/add-test-guild-form", response_class=HTMLResponse)
async def add_test_guild_form(request: Request, current_user=Depends(get_current_user)):
    """Form to add a test guild"""
    return templates.TemplateResponse(
        "debug/add_test_guild.html", 
        {"request": request, "user": current_user}
    )