from fastapi import Depends
from app.web.interfaces.api.rest.v1.base_controller import BaseController
from app.shared.infrastructure.models.auth import AppUserEntity, AppRoleEntity
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user

class UserManagementController(BaseController):
    """Controller for user management functionality"""
    
    def __init__(self):
        super().__init__(prefix="/users", tags=["User Management"])
        self._register_routes()
    
    def _register_routes(self):
        """Register all user management routes"""
        self.router.get("/")(self.get_users)
        self.router.get("/{user_id}")(self.get_user)
        self.router.post("/{user_id}/roles")(self.update_user_roles)
        self.router.delete("/{user_id}")(self.delete_user)
    
    async def get_users(self, current_user: AppUserEntity = Depends(get_current_user)):
        """Get all users"""
        try:
            if not current_user.is_owner:
                return self.error_response("Only owner can list users", 403)
            users = await self.user_service.get_all_users()
            return self.success_response(users)
        except Exception as e:
            return self.handle_exception(e)
    
    async def get_user(self, user_id: str, current_user: AppUserEntity = Depends(get_current_user)):
        """Get user by ID"""
        try:
            if not current_user.is_owner:
                return self.error_response("Only owner can view user details", 403)
            user = await self.user_service.get_user(user_id)
            return self.success_response(user)
        except Exception as e:
            return self.handle_exception(e)
    
    async def update_user_roles(self, user_id: str, roles: list[str], current_user: AppUserEntity = Depends(get_current_user)):
        """Update user roles"""
        try:
            if not current_user.is_owner:
                return self.error_response("Only owner can update user roles", 403)
            updated_user = await self.user_service.update_user_roles(user_id, roles)
            return self.success_response(updated_user)
        except Exception as e:
            return self.handle_exception(e)
    
    async def delete_user(self, user_id: str, current_user: AppUserEntity = Depends(get_current_user)):
        """Delete user"""
        try:
            if not current_user.is_owner:
                return self.error_response("Only owner can delete users", 403)
            result = await self.user_service.delete_user(user_id)
            return self.success_response(result)
        except Exception as e:
            return self.handle_exception(e)

# Controller instance
user_management_controller = UserManagementController() 