from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user
from fastapi import APIRouter, Depends, HTTPException
from app.web.domain.auth.dependencies import require_moderator
from app.web.domain.auth.permissions import Role, require_role
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

# Initialize templates
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

# Create router with prefix
router = APIRouter(prefix="/admin", tags=["Admin"])

def owner_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_owner:
            flash('This area is restricted to bot owners only.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@router.get("/overview", response_class=HTMLResponse)
async def admin_overview(user = Depends(get_current_user)):
    """Admin overview page - requires SUPER_ADMIN role"""
    # Verify SUPER_ADMIN role
    await require_role(user, Role.SUPER_ADMIN)
    
    return templates.TemplateResponse(
        "pages/admin/overview.html",
        {
            "request": request,
            "user": user,
            "active_page": "overview"
        }
    )

@router.get("/bot-settings", response_class=HTMLResponse)
async def bot_settings(user = Depends(get_current_user)):
    """Bot settings page - requires SUPER_ADMIN role"""
    await require_role(user, Role.SUPER_ADMIN)
    
    return templates.TemplateResponse(
        "pages/admin/bot-settings.html",
        {
            "request": request,
            "user": user,
            "active_page": "bot-settings"
        }
    )

# Add other admin routes following the same pattern... 