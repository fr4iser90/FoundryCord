from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from app.web.core.extensions import templates_extension, session_extension
from app.web.application.services.auth.dependencies import get_current_user
from app.web.domain.auth.permissions import Role, require_role
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
        self.router.get("", response_class=HTMLResponse)(self.owner_dashboard)
        self.router.get("/permissions", response_class=HTMLResponse)(self.permissions)
        self.router.get("/logs", response_class=HTMLResponse)(self.logs)
    
    async def owner_dashboard(self, request: Request, current_user=Depends(get_current_user)):
        """Owner dashboard page"""
        try:
            await require_role(current_user, Role.OWNER)
            
            # Get session
            session = session_extension(request)
            selected_guild = session.get('selected_guild')
            
            return templates.TemplateResponse(
                "views/owner/dashboard.html",
                {
                    "request": request,
                    "user": current_user,
                    "active_page": "dashboard",
                    "selected_guild": selected_guild
                }
            )
        except HTTPException as e:
            logger.error(f"Access denied to owner dashboard: {e}")
            return templates.TemplateResponse(
                "views/errors/403.html",
                {
                    "request": request,
                    "user": current_user,
                    "error": str(e.detail)
                },
                status_code=403
            )
        except Exception as e:
            logger.error(f"Error in owner dashboard: {e}")
            return templates.TemplateResponse(
                "views/errors/500.html",
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
            
            return templates.TemplateResponse(
                "views/owner/permissions.html",
                {
                    "request": request,
                    "user": current_user,
                    "active_page": "permissions",
                    "selected_guild": selected_guild
                }
            )
        except HTTPException as e:
            logger.error(f"Access denied to permissions: {e}")
            return templates.TemplateResponse(
                "views/errors/403.html",
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
                "views/errors/500.html",
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
            logs = []  # TODO: Implement system logs in a dedicated LogsController
            
            return templates.TemplateResponse(
                "views/owner/logs.html",
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
                "views/errors/403.html",
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
                "views/errors/500.html",
                {
                    "request": request,
                    "user": current_user,
                    "error": str(e)
                },
                status_code=500
            )

# Create view instance
owner_view = OwnerView()
owner_dashboard = owner_view.owner_dashboard
permissions = owner_view.permissions
logs = owner_view.logs 