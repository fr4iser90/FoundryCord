from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from app.web.core.extensions import get_templates
from app.web.application.services.auth.dependencies import get_current_user
import psutil

router = APIRouter(prefix="/bot", tags=["Bot"])
templates = get_templates()

@router.get("/overview", response_class=HTMLResponse)
async def bot_overview(request: Request, current_user=Depends(get_current_user)):
    """Bot overview page with stats and system info"""
    
    # Beispiel-Statistiken (diese sollten aus Ihrem Bot-Service kommen)
    stats = {
        "server_count": 10,
        "active_servers": 8,
        "total_users": 500,
        "online_users": 100,
        "total_commands": 1000,
        "daily_commands": 50
    }
    
    # System-Ressourcen
    system = {
        "cpu_usage": round(psutil.cpu_percent(), 1),
        "memory_usage": round(psutil.virtual_memory().percent, 1),
        "memory_used": f"{psutil.virtual_memory().used / (1024*1024*1024):.1f}GB",
        "memory_total": f"{psutil.virtual_memory().total / (1024*1024*1024):.1f}GB"
    }
    
    # Bot-Status und Uptime (auch aus Ihrem Bot-Service)
    bot_status = "ONLINE"
    uptime = "5 days, 2 hours"
    
    # Beispiel für kürzliche Aktivitäten
    recent_activities = [
        {
            "type": "Command",
            "icon": "terminal",
            "timestamp": "2025-03-22T01:30:00Z",
            "description": "User executed /help command",
            "server": "HomeLab Server"
        },
        # Weitere Aktivitäten hier...
    ]
    
    return templates.TemplateResponse(
        "pages/bot/overview.html",
        {
            "request": request,
            "user": current_user,
            "stats": stats,
            "system": system,
            "bot_status": bot_status,
            "uptime": uptime,
            "recent_activities": recent_activities
        }
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
