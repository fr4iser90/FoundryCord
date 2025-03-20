from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from app.web.core.extensions import get_templates
from app.web.application.services.auth.dependencies import get_current_user

router = APIRouter(prefix="/bot", tags=["Bot"])
templates = get_templates()

@router.get("/overview", response_class=HTMLResponse)
async def bot_overview(request: Request, current_user=Depends(get_current_user)):
    """Bot overview page"""
    return templates.TemplateResponse(
        "pages/bot/overview.html",
        {"request": request, "user": current_user}
    )

@router.get("/config", response_class=HTMLResponse)
async def bot_config(request: Request, current_user=Depends(get_current_user)):
    """Bot configuration page"""
    return templates.TemplateResponse(
        "pages/bot/config.html",
        {"request": request, "user": current_user}
    )

@router.get("/servers", response_class=HTMLResponse)
async def bot_servers(request: Request, current_user=Depends(get_current_user)):
    """Bot servers overview"""
    return templates.TemplateResponse(
        "pages/bot/servers.html",
        {"request": request, "user": current_user}
    )
