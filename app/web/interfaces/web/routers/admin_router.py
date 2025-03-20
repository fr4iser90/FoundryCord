from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from app.web.interfaces.web.dependencies import get_templates, render_template
from app.web.domain.auth.dependencies import get_current_user
from app.web.domain.auth.permissions import Role, require_role

router = APIRouter(prefix="/admin", tags=["Admin"])
templates = get_templates()

@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, current_user=Depends(get_current_user)):
    """Admin dashboard overview"""
    # Verify SUPER_ADMIN role
    await require_role(current_user, Role.SUPER_ADMIN)
    
    return await render_template(
        request,
        "pages/admin/overview.html",
        user=current_user
    )

@router.get("/users", response_class=HTMLResponse)
async def manage_users(request: Request, current_user=Depends(get_current_user)):
    """User management interface"""
    return await render_template(
        request,
        "pages/admin/users.html",
        user=current_user
    )

@router.get("/settings", response_class=HTMLResponse)
async def admin_settings(request: Request, current_user=Depends(get_current_user)):
    """Admin settings page"""
    return await render_template(
        request,
        "pages/admin/settings.html",
        user=current_user
    )
