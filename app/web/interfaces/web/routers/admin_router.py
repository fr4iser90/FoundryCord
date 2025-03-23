from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from app.web.core.extensions import get_templates
from app.web.application.services.auth.dependencies import get_current_user
from app.web.domain.auth.permissions import Role, require_role
import logging
from fastapi import status

router = APIRouter(prefix="/admin", tags=["Admin"])
templates = get_templates()
logger = logging.getLogger(__name__)

@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, current_user=Depends(get_current_user)):
    """Admin dashboard overview"""
    # Add safe handling for None current_user
    if current_user is None:
        logger.error("User attempting to access admin dashboard without authentication")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
        
    # Add debug logging  
    logger.info(f"User attempting to access admin dashboard: {current_user}")
    logger.info(f"User role: {current_user.get('role', 'No role specified')}")
    
    try:
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
    except HTTPException as e:
        logger.error(f"Permission error: {e.detail}")
        # Re-raise the exception to let the middleware handle it
        raise

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

@router.get("/bot-control", response_class=HTMLResponse)
async def admin_bot_control(request: Request, current_user=Depends(get_current_user)):
    """Admin bot control panel"""
    try:
        # Verify Bot Owner role
        await require_role(current_user, Role.OWNER)
        
        return templates.TemplateResponse(
            "pages/admin/bot_control.html",
            {
                "request": request, 
                "user": current_user,
                "active_page": "admin-bot-control"
            }
        )
    except HTTPException as e:
        logger.error(f"Permission error: {e.detail}")
        # Re-raise the exception to let the middleware handle it
        raise
