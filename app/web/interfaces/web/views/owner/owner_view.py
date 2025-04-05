from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from app.web.core.extensions import templates_extension, session_extension
from app.web.application.services.auth.dependencies import get_current_user
from app.web.domain.auth.permissions import Role, require_role
from app.web.interfaces.api.rest.v1.owner.owner_controller import (
    get_system_logs,
    get_bot_config,
    list_servers
)
from app.shared.interface.logging.api import get_web_logger

router = APIRouter(prefix="/owner", tags=["Owner Controls"])
templates = templates_extension()
logger = get_web_logger()

class OwnerView:
    """View for owner-specific functionality"""
    
    def __init__(self):
        self.router = router
        self._register_routes()
    
    def _register_routes(self):
        """Register all routes for this view"""
        self.router.get("/bot-control", response_class=HTMLResponse)(self.bot_control)
        self.router.get("/permissions", response_class=HTMLResponse)(self.permissions)
        self.router.get("/logs", response_class=HTMLResponse)(self.logs)
    
    async def bot_control(self, request: Request, current_user=Depends(get_current_user)):
        """Bot control panel"""
        try:
            await require_role(current_user, Role.OWNER)
            
            # Get session
            session = session_extension(request)
            selected_guild = session.get('selected_guild')
            
            # Get bot configuration and server list
            config = await get_bot_config(current_user)
            servers = await list_servers(current_user)
            
            return templates.TemplateResponse(
                "pages/owner/bot_control.html",
                {
                    "request": request,
                    "user": current_user,
                    "active_page": "bot-control",
                    "config": config,
                    "servers": servers,
                    "selected_guild": selected_guild
                }
            )
        except HTTPException as e:
            logger.error(f"Access denied to bot control: {e}")
            return templates.TemplateResponse(
                "pages/errors/403.html",
                {
                    "request": request,
                    "user": current_user,
                    "error": str(e.detail)
                },
                status_code=403
            )
        except Exception as e:
            logger.error(f"Error in bot control view: {e}")
            return templates.TemplateResponse(
                "pages/errors/500.html",
                {
                    "request": request,
                    "user": current_user,
                    "error": str(e)
                },
                status_code=500
            )
    
    async def permissions(self, request: Request, current_user=Depends(get_current_user)):
        """Permissions management panel"""
        try:
            await require_role(current_user, Role.OWNER)
            
            # Get session
            session = session_extension(request)
            selected_guild = session.get('selected_guild')
            
            # Get server list for permission management
            servers = await list_servers(current_user)
            
            return templates.TemplateResponse(
                "pages/owner/permissions.html",
                {
                    "request": request,
                    "user": current_user,
                    "active_page": "permissions",
                    "servers": servers,
                    "selected_guild": selected_guild
                }
            )
        except HTTPException as e:
            logger.error(f"Access denied to permissions: {e}")
            return templates.TemplateResponse(
                "pages/errors/403.html",
                {
                    "request": request,
                    "user": current_user,
                    "error": str(e.detail)
                },
                status_code=403
            )
        except Exception as e:
            logger.error(f"Error in permissions view: {e}")
            return templates.TemplateResponse(
                "pages/errors/500.html",
                {
                    "request": request,
                    "user": current_user,
                    "error": str(e)
                },
                status_code=500
            )
    
    async def logs(self, request: Request, current_user=Depends(get_current_user)):
        """System logs panel"""
        try:
            await require_role(current_user, Role.OWNER)
            
            # Get session
            session = session_extension(request)
            selected_guild = session.get('selected_guild')
            
            # Get system logs
            logs = await get_system_logs(current_user)
            
            return templates.TemplateResponse(
                "pages/owner/logs.html",
                {
                    "request": request,
                    "user": current_user,
                    "active_page": "logs",
                    "logs": logs,
                    "selected_guild": selected_guild
                }
            )
        except HTTPException as e:
            logger.error(f"Access denied to logs: {e}")
            return templates.TemplateResponse(
                "pages/errors/403.html",
                {
                    "request": request,
                    "user": current_user,
                    "error": str(e.detail)
                },
                status_code=403
            )
        except Exception as e:
            logger.error(f"Error in logs view: {e}")
            return templates.TemplateResponse(
                "pages/errors/500.html",
                {
                    "request": request,
                    "user": current_user,
                    "error": str(e)
                },
                status_code=500
            )

# Create view instance
owner_view = OwnerView()
bot_control = owner_view.bot_control
permissions = owner_view.permissions
logs = owner_view.logs 