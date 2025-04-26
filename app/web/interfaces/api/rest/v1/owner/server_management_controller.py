from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.shared.infrastructure.models.auth import AppUserEntity, AppRoleEntity
from app.shared.domain.auth.services import AuthenticationService, AuthorizationService
from app.shared.interface.logging.api import get_web_logger
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.models.discord.entities import GuildEntity
from sqlalchemy import select
from sqlalchemy.sql import func
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user
from app.web.interfaces.api.rest.v1.base_controller import BaseController
from app.web.infrastructure.factories.service.web_service_factory import WebServiceFactory
from typing import List
from app.web.interfaces.api.rest.v1.schemas.guild_schemas import GuildInfo, GuildAccessUpdateResponse


logger = get_web_logger()

class ServerManagementController(BaseController):
    """Controller for server management functionality"""
    
    def __init__(self):
        super().__init__(prefix="/owner/servers", tags=["Server Management"])
        # Get ServerService from the factory
        services = WebServiceFactory.get_instance().get_services()
        self.server_service = services.get('server_service')
        if not self.server_service:
            self.logger.error("ServerService could not be initialized.")
            raise RuntimeError("ServerService is unavailable")
        self._register_routes()
    
    def _register_routes(self):
        """Register all routes for this controller"""
        # Keep the old route for now, maybe deprecate later?
        self.router.get("/")(self.get_servers_legacy) 
        # Add the new route specifically for the management UI
        self.router.get("/manageable", response_model=List[GuildInfo])(self.get_manageable_servers) 
        
        self.router.get("/{server_id}")(self.get_server)
        # Add the access status update endpoint with the response model
        self.router.post("/{server_id}/access", response_model=GuildAccessUpdateResponse)(self.update_server_access) 
        self.router.post("/{server_id}/restart")(self.restart_server)
        self.router.post("/{server_id}/stop")(self.stop_server)
        self.router.post("/{server_id}/start")(self.start_server)
        self.router.get("/{server_id}/status")(self.get_server_status)
    
    # Keep the old method for potential compatibility, mark as legacy or remove later
    async def get_servers_legacy(self, current_user: AppUserEntity = Depends(get_current_user)):
        """Get list of servers (approved status only) for the current user"""
        try:
            # This uses the method that filters by 'approved' or user membership
            servers = await self.server_service.get_available_servers(current_user)
            return self.success_response(servers) 
        except Exception as e:
            return self.handle_exception(e)

    async def get_manageable_servers(self, current_user: AppUserEntity = Depends(get_current_user)) -> List[GuildEntity]:
        """Get list of ALL servers (all statuses) for owner management."""
        try:
            # Use the new service method that fetches all servers for owners
            servers: List[GuildEntity] = await self.server_service.get_all_manageable_servers(current_user)
            # Return the list directly. FastAPI will serialize using GuildInfo response_model.
            return servers
        except Exception as e:
            # Let the global exception handler catch and log
            self.logger.error(f"Error fetching manageable servers: {e}", exc_info=True) # Log here too
            # Re-raise the original exception or a generic HTTPException
            raise HTTPException(status_code=500, detail="Failed to retrieve manageable servers") from e
    
    async def update_server_access(self, server_id: str, request: Request, current_user: AppUserEntity = Depends(get_current_user)) -> GuildAccessUpdateResponse:
        """Update the access status of a server (approve, reject, block, suspend)."""
        try:
            if not current_user.is_owner:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owner can update server access.")
            
            payload = await request.json()
            new_status = payload.get('status')
            
            if not new_status or new_status.lower() not in ['pending', 'approved', 'rejected', 'blocked', 'suspended']:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status provided.")
            
            # Call the service method
            updated_server_entity: GuildEntity = await self.server_service.update_guild_access_status(server_id, new_status, current_user.id)
            
            # Return the dictionary matching the response model structure
            # FastAPI will serialize updated_server_entity using GuildInfo schema
            return {
                "message": f"Server status updated to {new_status}", 
                "server": updated_server_entity
            }
        except HTTPException as e:
            raise e # Re-raise validation/permission errors
        except Exception as e:
            self.logger.error(f"Error updating server {server_id} access: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to update server access") from e

    async def get_server(self, server_id: str, current_user: AppUserEntity = Depends(get_current_user)):
        """Get details of a specific server"""
        try:
            if not current_user.is_owner:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only owner can view server details"
                )
            server = await self.server_service.get_server(server_id)
            return self.success_response(server)
        except Exception as e:
            return self.handle_exception(e)
    
    async def restart_server(self, server_id: str, current_user: AppUserEntity = Depends(get_current_user)):
        """Restart a specific server"""
        try:
            if not current_user.is_owner:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only owner can restart servers"
                )
            result = await self.server_service.restart_server(server_id)
            return self.success_response(result)
        except Exception as e:
            return self.handle_exception(e)
    
    async def stop_server(self, server_id: str, current_user: AppUserEntity = Depends(get_current_user)):
        """Stop a specific server"""
        try:
            if not current_user.is_owner:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only owner can stop servers"
                )
            result = await self.server_service.stop_server(server_id)
            return self.success_response(result)
        except Exception as e:
            return self.handle_exception(e)
    
    async def start_server(self, server_id: str, current_user: AppUserEntity = Depends(get_current_user)):
        """Start a specific server"""
        try:
            if not current_user.is_owner:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only owner can start servers"
                )
            result = await self.server_service.start_server(server_id)
            return self.success_response(result)
        except Exception as e:
            return self.handle_exception(e)
    
    async def get_server_status(self, server_id: str, current_user: AppUserEntity = Depends(get_current_user)):
        """Get status of a specific server"""
        try:
            if not current_user.is_owner:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only owner can view server status"
                )
            status = await self.server_service.get_server_status(server_id)
            return self.success_response(status)
        except Exception as e:
            return self.handle_exception(e)

# Controller instance
server_management_controller = ServerManagementController()

# Remove legacy/outdated function exports
# get_servers = server_management_controller.get_servers # Removed
# get_server = server_management_controller.get_server
# restart_server = server_management_controller.restart_server
# stop_server = server_management_controller.stop_server
# start_server = server_management_controller.start_server
# get_server_status = server_management_controller.get_server_status 