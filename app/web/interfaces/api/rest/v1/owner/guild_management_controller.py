from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.shared.infrastructure.models.auth import AppUserEntity, AppRoleEntity
from app.shared.interfaces.logging.api import get_web_logger
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

class GuildManagementController(BaseController):
    """Controller for guild management functionality"""
    
    def __init__(self):
        super().__init__(prefix="/owner/guilds", tags=["Guild Management"])
        # Get GuildService from the factory
        services = WebServiceFactory.get_instance().get_services()
        self.guild_service = services.get('guild_service')
        if not self.guild_service:
            self.logger.error("GuildService could not be initialized.")
            raise RuntimeError("GuildService is unavailable")
        self._register_routes()
    
    def _register_routes(self):
        """Register all routes for this controller"""
        # Route for management UI to get all guilds
        self.router.get("/manageable", response_model=List[GuildInfo])(self.get_manageable_guilds)
        
        # Route to update guild access status
        self.router.post("/{guild_id}/access", response_model=GuildAccessUpdateResponse)(self.update_guild_access)
    
    async def get_manageable_guilds(self, current_user: AppUserEntity = Depends(get_current_user)) -> List[GuildEntity]:
        """Get list of ALL guilds (all statuses) for owner management."""
        try:
            # Use the service method that fetches all guilds for owners
            guilds: List[GuildEntity] = await self.guild_service.get_all_manageable_guilds(current_user)
            # Return the list directly. FastAPI will serialize using GuildInfo response_model.
            return guilds
        except Exception as e:
            # Let the global exception handler catch and log
            self.logger.error(f"Error fetching manageable guilds: {e}", exc_info=True) # Log here too
            # Re-raise the original exception or a generic HTTPException
            raise HTTPException(status_code=500, detail="Failed to retrieve manageable guilds") from e
    
    async def update_guild_access(self, guild_id: str, request: Request, current_user: AppUserEntity = Depends(get_current_user)) -> GuildAccessUpdateResponse:
        """Update the access status of a guild (approve, reject, banned, suspend)."""
        try:
            if not current_user.is_owner:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owner can update guild access.")
            
            payload = await request.json()
            new_status = payload.get('status')
            
            # Updated allowed statuses
            allowed_statuses = ['pending', 'approved', 'rejected', 'suspended', 'banned']
            if not new_status or new_status.lower() not in allowed_statuses:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status provided.")
            
            # Call the service method (already correct)
            updated_guild_entity: GuildEntity = await self.guild_service.update_guild_access_status(guild_id, new_status.lower(), current_user.id)
            
            # Return the dictionary matching the response model structure
            # FastAPI will serialize updated_guild_entity using GuildInfo schema
            return {
                "message": f"Guild status updated to {new_status.lower()}", 
                "guild": updated_guild_entity # Updated key from 'server' to 'guild'
            }
        except HTTPException as e:
            raise e # Re-raise validation/permission errors
        except Exception as e:
            self.logger.error(f"Error updating guild {guild_id} access: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to update guild access") from e

# Renamed controller instance
guild_management_controller = GuildManagementController()

# Removed legacy function exports
# get_servers = server_management_controller.get_servers # Removed
# get_server = server_management_controller.get_server
# restart_server = server_management_controller.restart_server
# stop_server = server_management_controller.stop_server
# start_server = server_management_controller.start_server
# get_server_status = server_management_controller.get_server_status 