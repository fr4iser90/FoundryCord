from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from app.shared.infrastructure.models.auth import AppUserEntity, AppRoleEntity
from app.shared.domain.auth.services import AuthenticationService, AuthorizationService
from app.shared.interface.logging.api import get_web_logger
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user
from app.web.infrastructure.factories.service.web_service_factory import WebServiceFactory
from typing import Optional, Dict, Any, List, TypeVar, Generic, Type
from pydantic import BaseModel
from functools import wraps

T = TypeVar('T', bound=BaseModel)

class BaseController:
    """Modern base controller providing common functionality for all API controllers"""
    
    def __init__(self, prefix: str, tags: List[str]):
        self.router = APIRouter(prefix=prefix, tags=tags)
        self.logger = get_web_logger()
        
        # Get shared services
        services = WebServiceFactory.get_instance().get_services()
        self.auth_service = services['auth_service']
        self.authz_service = services['authz_service']
        
        # Register common routes
        self._register_common_routes()
    
    def _register_common_routes(self):
        """Register common routes for all controllers"""
        pass  # Override in subclasses if needed
    
    async def check_permission(self, user: AppUserEntity, permission: str) -> bool:
        """Check if user has required permission"""
        return await self.authz_service.check_permission(user, permission)
    
    async def require_permission(self, user: AppUserEntity, permission: str):
        """Require a specific permission, raise 403 if not met"""
        if not await self.check_permission(user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission {permission} required"
            )
    
    def success_response(self, data: Any = None, message: str = "Success", status_code: int = 200) -> JSONResponse:
        """Create a standard success response"""
        return JSONResponse(
            status_code=status_code,
            content={
                "status": "success",
                "message": message,
                "data": data
            }
        )
    
    def error_response(self, message: str, status_code: int = 400, errors: List[str] = None) -> JSONResponse:
        """Create a standard error response"""
        return JSONResponse(
            status_code=status_code,
            content={
                "status": "error",
                "message": message,
                "errors": errors or []
            }
        )
    
    def handle_exception(self, e: Exception) -> JSONResponse:
        """Handle exceptions and return appropriate error response"""
        if isinstance(e, HTTPException):
            return self.error_response(str(e.detail), e.status_code)
        
        self.logger.error(f"Unhandled exception: {e}")
        return self.error_response(
            "An unexpected error occurred",
            status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    def require_role(self, role_name: str):
        """Decorator to require a specific role"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                user = kwargs.get('current_user')
                if not user or not any(guild_user.role.name == role_name for guild_user in user.guild_roles):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Role {role_name} required"
                    )
                return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    def require_permissions(self, *permissions: str):
        """Decorator to require multiple permissions"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                user = kwargs.get('current_user')
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required"
                    )
                
                for permission in permissions:
                    if not await self.check_permission(user, permission):
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Permission {permission} required"
                        )
                return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    def paginate(self, items: List[Any], page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """Helper method for pagination"""
        start = (page - 1) * per_page
        end = start + per_page
        total = len(items)
        
        return {
            "items": items[start:end],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page
        }
    
    def validate_request(self, model: Type[T], data: Dict[str, Any]) -> T:
        """Validate request data against a Pydantic model"""
        try:
            return model(**data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            ) 