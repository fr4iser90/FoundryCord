from fastapi import Depends
from app.web.interfaces.api.rest.v1.base_controller import BaseController
from app.shared.infrastructure.models.auth import AppUserEntity, AppRoleEntity
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user

class DashboardController(BaseController):
    """Controller for dashboard functionality"""
    
    def __init__(self):
        super().__init__(prefix="/dashboard", tags=["Dashboard"])
        self._register_routes()
    
    def _register_routes(self):
        """Register all dashboard routes"""
        self.router.get("/widgets")(self.get_available_widgets)
        self.router.get("/layouts")(self.get_layouts)
        self.router.post("/layouts")(self.create_layout)
        self.router.get("/layouts/{layout_id}")(self.get_layout)
        self.router.put("/layouts/{layout_id}")(self.update_layout)
        self.router.delete("/layouts/{layout_id}")(self.delete_layout)
    
    async def get_available_widgets(self, current_user: AppUserEntity = Depends(get_current_user)):
        """Get list of available widgets"""
        try:
            widgets = await self.dashboard_service.get_available_widgets()
            return self.success_response(widgets)
        except Exception as e:
            return self.handle_exception(e)
    
    async def get_layouts(self, current_user: AppUserEntity = Depends(get_current_user)):
        """Get all dashboard layouts"""
        try:
            layouts = await self.dashboard_service.get_layouts()
            return self.success_response(layouts)
        except Exception as e:
            return self.handle_exception(e)
    
    async def create_layout(self, layout_data: dict, current_user: AppUserEntity = Depends(get_current_user)):
        """Create a new dashboard layout"""
        try:
            layout = await self.dashboard_service.create_layout(layout_data)
            return self.success_response(layout)
        except Exception as e:
            return self.handle_exception(e)
    
    async def get_layout(self, layout_id: str, current_user: AppUserEntity = Depends(get_current_user)):
        """Get a specific dashboard layout"""
        try:
            layout = await self.dashboard_service.get_layout(layout_id)
            return self.success_response(layout)
        except Exception as e:
            return self.handle_exception(e)
    
    async def update_layout(self, layout_id: str, layout_data: dict, current_user: AppUserEntity = Depends(get_current_user)):
        """Update a dashboard layout"""
        try:
            layout = await self.dashboard_service.update_layout(layout_id, layout_data)
            return self.success_response(layout)
        except Exception as e:
            return self.handle_exception(e)
    
    async def delete_layout(self, layout_id: str, current_user: AppUserEntity = Depends(get_current_user)):
        """Delete a dashboard layout"""
        try:
            await self.dashboard_service.delete_layout(layout_id)
            return self.success_response(message="Layout deleted successfully")
        except Exception as e:
            return self.handle_exception(e)

# Controller instance
dashboard_controller = DashboardController() 