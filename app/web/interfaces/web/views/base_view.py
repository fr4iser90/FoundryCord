from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from app.web.core.extensions import templates_extension
from app.shared.infrastructure.models.auth import AppUserEntity, AppRoleEntity
from app.shared.domain.auth.services import AuthenticationService, AuthorizationService
from app.shared.domain.auth.policies import is_authorized, is_bot_owner, is_admin, is_moderator, is_user, is_guest
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user
from app.shared.interface.logging.api import get_web_logger
from app.web.infrastructure.factories.service.web_service_factory import WebServiceFactory

class BaseView:
    """Base class for all web views"""
    
    def __init__(self, router: APIRouter):
        self.router = router
        self.templates = templates_extension()
        self.logger = get_web_logger()
        
        # Get shared services
        services = WebServiceFactory.get_instance().get_services()
        self.auth_service = services['auth_service']
        self.authz_service = services['authz_service']

    def _register_routes(self):
        """Register routes for this view - override in subclasses"""
        raise NotImplementedError
        
    @staticmethod
    async def get_current_user(request: Request) -> AppUserEntity:
        """Get current authenticated user"""
        return await get_current_user(request)
        
    def render_template(self, template: str, request: Request, **kwargs):
        """Render template with standard context"""
        return self.templates.TemplateResponse(
            f"views/{template}",
            {
                "request": request,
                "user": request.session.get("user"),
                **kwargs
            }
        )

    def error_response(self, request: Request, error: str, status_code: int = 400):
        """Render error template"""
        # Map status codes to template files
        template_map = {
            400: "errors/400.html",
            401: "errors/401.html",
            403: "errors/403.html",
            404: "errors/404.html",
            500: "errors/500.html",
            503: "errors/503.html"
        }
        
        # Default to 500 if status code not in map
        template = template_map.get(status_code, "errors/500.html")
        
        return self.render_template(
            template,
            request,
            error=error,
            status_code=status_code
        )

    async def check_permission(self, user: AppUserEntity, permission: str) -> bool:
        """Check if user has required permission using shared policies"""
        if permission == "OWNER":
            return is_bot_owner(user)
        elif permission == "ADMIN":
            return is_admin(user)
        elif permission == "MODERATOR":
            return is_moderator(user)
        elif permission == "USER":
            return is_user(user)
        elif permission == "GUEST":
            return is_guest(user)
        return is_authorized(user)
    
    async def require_permission(self, user: AppUserEntity, permission: str):
        """Raise HTTPException if user doesn't have required permission"""
        if not await self.check_permission(user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            ) 