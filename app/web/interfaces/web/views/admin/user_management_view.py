from fastapi import APIRouter, Request, Depends
from app.web.core.extensions import templates_extension
from app.web.application.services.auth.dependencies import get_current_user
from app.web.domain.auth.permissions import Role, require_role
from app.web.interfaces.api.rest.v1.admin.user_management_controller import user_management_controller
from fastapi.responses import HTMLResponse

router = APIRouter(prefix="/admin/users", tags=["Admin User Management"])
templates = templates_extension()

class UserManagementView:
    """View for admin user management - renders HTML templates"""
    
    def __init__(self):
        self.router = router
        self._register_routes()

    def _register_routes(self):
        """Register routes for this view"""
        self.router.get("", response_class=HTMLResponse)(self.user_management_page)
        self.router.get("/edit/{user_id}", response_class=HTMLResponse)(self.edit_user_page)

    async def user_management_page(self, request: Request, current_user=Depends(get_current_user)):
        """Render user management page"""
        try:
            await require_role(current_user, Role.ADMIN)
            
            return templates.TemplateResponse(
                "views/admin/user_management.html",
                {
                    "request": request,
                    "user": current_user,
                    "active_page": "user-management"
                }
            )
        except Exception as e:
            return templates.TemplateResponse(
                "views/errors/403.html",
                {"request": request, "user": current_user, "error": str(e)}
            )

    async def edit_user_page(self, request: Request, user_id: str, current_user=Depends(get_current_user)):
        """Render user edit page"""
        try:
            await require_role(current_user, Role.ADMIN)
            
            # Get user details from API
            user_details = await user_management_controller.get_user_details(request, user_id)
            
            return templates.TemplateResponse(
                "views/admin/edit_user.html",
                {
                    "request": request,
                    "user": current_user,
                    "active_page": "user-management",
                    "edit_user": user_details
                }
            )
        except Exception as e:
            return templates.TemplateResponse(
                "views/errors/403.html",
                {"request": request, "user": current_user, "error": str(e)}
            )

# View instance
user_management_view = UserManagementView() 