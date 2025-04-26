from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from app.web.core.extensions import templates_extension, session_extension
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user
from app.shared.interface.logging.api import get_web_logger
from app.shared.infrastructure.models.auth import AppUserEntity, AppRoleEntity
from app.shared.domain.auth.services import AuthenticationService, AuthorizationService
from app.web.interfaces.web.views.base_view import BaseView

router = APIRouter(prefix="/owner", tags=["Owner Controls"])

logger = get_web_logger()

class OwnerView(BaseView):
    """View for owner-specific functionality"""
    
    def __init__(self):
        # BaseView holt sich bereits die Services!
        super().__init__(APIRouter(prefix="/owner", tags=["Owner Controls"]))
        self._register_routes()
    
    def _register_routes(self):
        """Register all routes for this view"""
        self.router.get("", response_class=HTMLResponse)(self.owner_dashboard)
        self.router.get("/permissions", response_class=HTMLResponse)(self.permissions)
        self.router.get("/logs", response_class=HTMLResponse)(self.logs)
        self.router.get("/state-monitor", response_class=HTMLResponse)(self.state_monitor_page)
    
    async def owner_dashboard(self, request: Request):
        """Owner dashboard page"""
        try:
            current_user = await self.get_current_user(request)
            if not current_user.is_owner:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only owner can access this page"
                )
            
            # Get session
            session = session_extension(request)
            selected_guild = session.get('selected_guild')
            
            return self.render_template(  # Nutze self.render_template von BaseView
                "owner/dashboard.html",
                request,
                active_page="dashboard",
                selected_guild=selected_guild
            )
        except Exception as e:
            return self.error_response(request, str(e))
    
    async def permissions(self, request: Request):
        """Permissions management panel"""
        try:
            current_user = await self.get_current_user(request)
            if not current_user.is_owner:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only owner can manage permissions"
                )
            
            # Get session
            session = session_extension(request)
            selected_guild = session.get('selected_guild')
            
            return self.render_template(
                "owner/permissions.html",
                {
                    "request": request,
                    "user": current_user,
                    "active_page": "permissions",
                    "selected_guild": selected_guild
                }
            )
        except HTTPException as e:
            logger.error(f"Access denied to permissions: {e}")
            return self.render_template(
                "errors/403.html",
                {
                    "request": request,
                    "user": current_user,
                    "error": str(e.detail)
                },
                status_code=403
            )
        except Exception as e:
            logger.error(f"Error in permissions view: {e}")
            return self.render_template(
                "errors/500.html",
                {
                    "request": request,
                    "user": current_user,
                    "error": str(e)
                },
                status_code=500
            )
    
    async def logs(self, request: Request):
        """System logs panel"""
        try:
            current_user = await self.get_current_user(request)
            if not current_user.is_owner:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only owner can view logs"
                )
            
            # Get session
            session = session_extension(request)
            selected_guild = session.get('selected_guild')
            
            # Get system logs
            logs = []  # TODO: Implement system logs in a dedicated LogsController
            
            return self.render_template(
                "owner/logs.html",
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
            return self.render_template(
                "errors/403.html",
                {
                    "request": request,
                    "user": current_user,
                    "error": str(e.detail)
                },
                status_code=403
            )
        except Exception as e:
            logger.error(f"Error in logs view: {e}")
            return self.render_template(
                "errors/500.html",
                {
                    "request": request,
                    "user": current_user,
                    "error": str(e)
                },
                status_code=500
            )

    async def state_monitor_page(self, request: Request, current_user: AppUserEntity = Depends(get_current_user)):
        """Render the state monitor page"""
        try:
            # Owner Check
            if not current_user.is_owner:
                # Using BaseView error response for consistency
                return self.error_response(request, "Forbidden", 403)
            
            # Add any necessary context data here later if needed
            context = {}
            
            return self.render_template(
                "owner/state-monitor.html", # Ensure this path is correct relative to templates_dir in BaseView
                request,
                **context
            )
        except Exception as e:
            logger.error(f"Error loading State Monitor page: {e}", exc_info=True)
            # Using BaseView error response for consistency
            return self.error_response(request, "An unexpected error occurred", 500)

# View instance
owner_view = OwnerView()  # Keine Services mehr übergeben!
router = owner_view.router
owner_dashboard = owner_view.owner_dashboard
permissions = owner_view.permissions
logs = owner_view.logs 