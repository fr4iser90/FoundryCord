from fastapi import Depends
from app.web.interfaces.api.rest.v1.base_controller import BaseController
from app.shared.infrastructure.models.auth import AppUserEntity, AppRoleEntity
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user

class AdminController(BaseController):
    """Controller for admin functionality"""
    
    def __init__(self):
        super().__init__(prefix="/admin", tags=["Admin"])
        self._register_routes()
    
    def _register_routes(self):
        """Register all admin routes"""
        self.router.get("/users")(self.get_all_users)
        self.router.get("/guilds")(self.get_all_guilds)
        self.router.get("/system")(self.get_system_info)
        self.router.post("/maintenance")(self.toggle_maintenance)
    
    async def get_all_users(self, current_user: AppUserEntity = Depends(get_current_user)):
        """Get all users"""
        try:
            if not current_user.is_owner:
                return self.error_response("Only owner can list all users", 403)
            users = await self.admin_service.get_all_users()
            return self.success_response(users)
        except Exception as e:
            return self.handle_exception(e)
    
    async def get_all_guilds(self, current_user: AppUserEntity = Depends(get_current_user)):
        """Get all guilds"""
        try:
            if not current_user.is_owner:
                return self.error_response("Only owner can list all guilds", 403)
            guilds = await self.admin_service.get_all_guilds()
            return self.success_response(guilds)
        except Exception as e:
            return self.handle_exception(e)
    
    async def get_system_info(self, current_user: AppUserEntity = Depends(get_current_user)):
        """Get system information"""
        try:
            if not current_user.is_owner:
                return self.error_response("Only owner can view system info", 403)
            info = await self.admin_service.get_system_info()
            return self.success_response(info)
        except Exception as e:
            return self.handle_exception(e)
    
    async def toggle_maintenance(self, current_user: AppUserEntity = Depends(get_current_user)):
        """Toggle maintenance mode"""
        try:
            if not current_user.is_owner:
                return self.error_response("Only owner can toggle maintenance mode", 403)
            result = await self.admin_service.toggle_maintenance()
            return self.success_response(result)
        except Exception as e:
            return self.handle_exception(e)

# Controller instance
admin_controller = AdminController()
