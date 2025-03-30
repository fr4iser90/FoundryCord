from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from app.web.core.extensions import get_templates
from app.web.application.services.auth.dependencies import get_current_user
from app.web.domain.auth.permissions import Role, require_role
from app.web.interfaces.api.rest.v1.bot_admin_router import get_overview_stats
from app.shared.infrastructure.integration.bot_connector import get_bot_connector
import psutil

router = APIRouter(prefix="/bot", tags=["Bot"])
templates = get_templates()

@router.get("/overview", response_class=HTMLResponse)
async def bot_overview(request: Request, current_user=Depends(get_current_user)):
    """Bot overview dashboard"""
    # Holen der Bot-Statistiken für das Dashboard
    stats = await get_overview_stats(current_user)
    
    # Erhalte Systeminformationen
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    
    system_info = {
        "cpu_percent": cpu_percent,
        "memory_percent": memory.percent,
        "memory_used": f"{memory.used / (1024 * 1024 * 1024):.1f} GB",
        "memory_total": f"{memory.total / (1024 * 1024 * 1024):.1f} GB"
    }
    
    return templates.TemplateResponse(
        "pages/bot/overview.html",
        {
            "request": request, 
            "user": current_user,
            "stats": stats,
            "system_info": system_info,
            "active_page": "bot-overview"
        }
    )

@router.get("/control", response_class=HTMLResponse)
async def bot_control(request: Request, current_user=Depends(get_current_user)):
    """Bot control panel"""
    try:
        # Admin-Rolle prüfen
        await require_role(current_user, Role.OWNER)
        
        return templates.TemplateResponse(
            "pages/bot/control.html",
            {
                "request": request, 
                "user": current_user,
                "active_page": "bot-control"
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "pages/errors/403.html",
            {"request": request, "user": current_user, "error": str(e)}
        )

@router.get("/stats", response_class=HTMLResponse)
async def bot_stats(request: Request, current_user=Depends(get_current_user)):
    """Bot statistics dashboard"""
    stats = await get_overview_stats(current_user)
    
    # Zusätzliche detaillierte Statistiken hier laden
    bot_connector = get_bot_connector()
    try:
        recent_activities = await bot_connector.get_recent_activities()
        popular_commands = await bot_connector.get_popular_commands()
    except:
        # Fallback-Werte wenn der Bot-Connector nicht verfügbar ist
        recent_activities = []
        popular_commands = []
    
    return templates.TemplateResponse(
        "pages/bot/stats.html",
        {
            "request": request, 
            "user": current_user, 
            "stats": stats,
            "recent_activities": recent_activities,
            "popular_commands": popular_commands,
            "active_page": "bot-stats"
        }
    )

@router.get("/servers", response_class=HTMLResponse)
async def bot_servers(request: Request, current_user=Depends(get_current_user)):
    """Bot servers overview"""
    # Hole Server-Informationen vom Bot-Connector
    bot_connector = get_bot_connector()
    try:
        servers_info = await bot_connector.get_servers_info()
    except:
        # Fallback wenn der Bot-Connector nicht verfügbar ist
        servers_info = []
    
    return templates.TemplateResponse(
        "pages/bot/servers.html",
        {
            "request": request, 
            "user": current_user,
            "servers": servers_info,
            "active_page": "bot-servers"
        }
    )
