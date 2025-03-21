from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from app.web.core.extensions import get_templates
from app.web.application.services.auth.dependencies import get_current_user
from app.web.domain.auth.permissions import Role, require_role

router = APIRouter(prefix="/admin", tags=["Admin"])
templates = get_templates()

@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, current_user=Depends(get_current_user)):
    """Admin dashboard overview"""
    # Verify Bot Owner role
    await require_role(current_user, Role.OWNER)
    
    # Get some mock stats for now
    mock_stats = {
        "servers": 5,
        "active_users": 120,
        "bot_status": "Online",
        "uptime": "24h 13m",
        "system": {
            "cpu": 45,
            "memory": 62
        }
    }
    
    return templates.TemplateResponse(
        "pages/admin/overview.html",
        {
            "request": request, 
            "user": current_user,
            "active_page": "overview",
            "stats": mock_stats,
            "bot_status": mock_stats["bot_status"],
            "uptime": mock_stats["uptime"],
            "system": mock_stats["system"]
        }
    )

@router.get("/users", response_class=HTMLResponse)
async def manage_users(request: Request, current_user=Depends(get_current_user)):
    """User management interface"""
    return templates.TemplateResponse(
        "pages/admin/users.html",
        {"request": request, "user": current_user}
    )

@router.get("/settings", response_class=HTMLResponse)
async def admin_settings(request: Request, current_user=Depends(get_current_user)):
    """Admin settings page"""
    return templates.TemplateResponse(
        "pages/admin/settings.html",
        {"request": request, "user": current_user}
    )
