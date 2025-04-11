from fastapi import Depends
from app.web.interfaces.api.rest.v1.base_controller import BaseController
from app.shared.infrastructure.models.auth import AppUserEntity, AppRoleEntity
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user

class OwnerController(BaseController):
    """Controller for owner-specific functionality"""
    
    def __init__(self):
        super().__init__(prefix="/owner", tags=["Owner Controls"])
        self._register_routes()
    
    def _register_routes(self):
        """Register all routes for this controller"""
        self.router.get("/status")(self.get_system_status)
        self.router.post("/maintenance")(self.toggle_maintenance)
        self.router.post("/backup")(self.create_backup)
    
    async def get_system_status(self, current_user: AppUserEntity = Depends(get_current_user)):
        """Get detailed system status"""
        try:
            status = await self.owner_service.get_system_status()
            return self.success_response(status)
        except Exception as e:
            return self.handle_exception(e)
    
    async def toggle_maintenance(self, current_user: AppUserEntity = Depends(get_current_user)):
        """Toggle maintenance mode"""
        try:
            result = await self.owner_service.toggle_maintenance()
            return self.success_response(result)
        except Exception as e:
            return self.handle_exception(e)
    
    async def create_backup(self, current_user: AppUserEntity = Depends(get_current_user)):
        """Create a system backup"""
        try:
            result = await self.owner_service.create_backup()
            return self.success_response(result)
        except Exception as e:
            return self.handle_exception(e)

# Controller instance
owner_controller = OwnerController()
    
