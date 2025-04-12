from fastapi import Depends, Request
from typing import List, Optional
from app.web.interfaces.api.rest.v1.base_controller import BaseController
from app.shared.infrastructure.models.auth import AppUserEntity, AppRoleEntity
from app.web.infrastructure.factories.service.web_service_factory import WebServiceFactory
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user
from app.web.interfaces.api.rest.v1.schemas.server_schemas import ServerInfo

class ServerSelectorController(BaseController):
    """Controller for server selection functionality"""
    
    def __init__(self):
        super().__init__(prefix="/servers", tags=["Server Selection"])
        # Get ServerService from the factory
        services = WebServiceFactory.get_instance().get_services()
        self.server_service = services.get('server_service') 
        if not self.server_service:
            self.logger.error("ServerService could not be initialized.")
            raise RuntimeError("ServerService is unavailable")
        self._register_routes()
    
    def _register_routes(self):
        """Register all routes for server selection"""
        self.router.get("/", response_model=List[ServerInfo])(self.get_servers)  # List all servers
        self.router.get("/current", response_model=Optional[ServerInfo])(self.get_current_server)  # Get current selection
        self.router.post("/select/{guild_id}")(self.select_server)  # Select a server
    
    async def get_servers(self, current_user: AppUserEntity = Depends(get_current_user)) -> List[ServerInfo]:
        """Get list of available servers for the current user"""
        try:
            servers = await self.server_service.get_available_servers(current_user)
            return servers
        except Exception as e:
            raise e
    
    async def get_current_server(self, request: Request, current_user: AppUserEntity = Depends(get_current_user)) -> Optional[ServerInfo]:
        """Get currently selected server from session"""
        try:
            server = await self.server_service.get_current_server(request, current_user)
            return server
        except Exception as e:
            raise e
    
    async def select_server(self, request: Request, guild_id: str, current_user: AppUserEntity = Depends(get_current_user)):
        """Select a server and store it in session"""
        try:
            result = await self.server_service.select_server(request, guild_id, current_user)
            return {"message": "Server selected successfully"}
        except Exception as e:
            raise e

# Controller instance
server_selector_controller = ServerSelectorController() 