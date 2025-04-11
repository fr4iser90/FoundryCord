from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from app.web.core.extensions import templates_extension
from app.shared.infrastructure.models.auth import AppUserEntity, AppRoleEntity
from app.shared.domain.auth.services import AuthenticationService, AuthorizationService
from app.web.interfaces.api.rest.v1.admin.user_management_controller import user_management_controller
from app.shared.interface.logging.api import get_web_logger
from app.web.interfaces.web.views.base_view import BaseView

class UserManagementView(BaseView):
    """View for admin user management - renders HTML templates"""
    
    def __init__(self):
        super().__init__(APIRouter(prefix="/admin/users", tags=["Admin User Management"]))
        self._register_routes()

    def _register_routes(self):
        """Register routes for this view"""
        self.router.get("")(self.user_management_page)
        self.router.get("/edit/{user_id}", response_class=HTMLResponse)(self.edit_user_page)

    async def user_management_page(self, request: Request):
        """Render user management page"""
        try:
            current_user = await self.get_current_user(request)
            await self.require_permission(current_user, "MANAGE_USERS")
            return self.render_template(
                "admin/user_management.html",
                request,
                active_page="user-management"
            )
        except Exception as e:
            return self.error_response(request, str(e))

    async def edit_user_page(self, request: Request, user_id: str):
        """Render user edit page"""
        try:
            current_user = await self.get_current_user(request)
            if not await self.authz_service.check_permission(current_user, "MANAGE_USERS"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            
            # Get user details from API
            user_details = await user_management_controller.get_user_details(request, user_id)
            
            return self.render_template(
                "admin/edit_user.html",
                request,
                active_page="user-management",
                edit_user=user_details
            )
        except Exception as e:
            return self.error_response(request, str(e))

# View instance
user_management_view = UserManagementView()
router = user_management_view.router 