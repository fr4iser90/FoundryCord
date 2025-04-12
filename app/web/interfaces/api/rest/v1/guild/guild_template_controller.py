from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, Dict, Optional
from app.web.interfaces.api.rest.v1.base_controller import BaseController
from app.shared.infrastructure.models.auth import AppUserEntity
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user
# Import the new GuildTemplateService
from app.web.application.services.guild.template_service import GuildTemplateService 
# TODO: Define response model schema when created
# from app.web.interfaces.api.rest.v1.schemas.guild_template_schemas import GuildTemplateResponse

class GuildTemplateController(BaseController):
    """Controller for managing guild structure templates via API."""

    def __init__(self):
        # Define API prefix and tags
        # Note: Prefix is just /template now, guild_id comes from path parameter in route
        super().__init__(prefix="/guilds/{guild_id}/template", tags=["Guild Designer API"])
        
        # Instantiate the service directly for now
        # TODO: Replace with proper injection/factory later
        self.template_service = GuildTemplateService()
            
        self._register_routes()

    def _register_routes(self):
        """Register API routes for guild templates."""
        # Route to get the template data for a specific guild
        # TODO: Add response_model=GuildTemplateResponse when schema is defined
        self.router.get("", 
                        # response_model=GuildTemplateResponse, 
                        summary="Get Guild Structure Template",
                        description="Retrieves the stored structure template (categories, channels, permissions) for the specified guild.")(self.get_guild_template)
        
        # TODO: Add routes for updating/applying templates later
        # self.router.put("", ...)(self.update_guild_template)
        # self.router.post("/apply", ...)(self.apply_guild_template_to_discord)


    async def get_guild_template(self, guild_id: str, current_user: AppUserEntity = Depends(get_current_user)) -> Dict[str, Any]: # TODO: Change return type to response_model
        """API endpoint to retrieve the guild template structure."""
        try:
            # --- Permission Check ---
            # Example: Only allow owners for now. Refine later with specific roles/permissions.
            if not current_user.is_owner:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions to view guild template.")

            # --- Call Service Layer ---
            self.logger.info(f"Calling GuildTemplateService to fetch template for guild {guild_id}")
            template_data: Optional[Dict[str, Any]] = await self.template_service.get_template_by_guild(guild_id)
            
            # --- Handle Not Found --- 
            if not template_data:
                self.logger.warning(f"Template not found for guild {guild_id} by service.")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guild template not found.")
            
            # --- Return Success Response ---
            self.logger.info(f"Successfully retrieved template data for guild {guild_id}")
            return self.success_response(template_data)

        except HTTPException as http_exc:
            # Re-raise HTTP exceptions directly
            raise http_exc
        except Exception as e:
            # Handle unexpected errors
            self.logger.error(f"Error fetching guild template for {guild_id}: {e}", exc_info=True)
            # Use BaseController's exception handler or raise generic 500
            # Assuming self.handle_exception exists, otherwise raise manually
            return self.handle_exception(e)
            # raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve guild template.")

# Instantiate the controller for registration
guild_template_controller = GuildTemplateController() 