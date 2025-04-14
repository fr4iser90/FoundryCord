from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, Dict, Optional, List
from app.web.interfaces.api.rest.v1.base_controller import BaseController
from app.shared.infrastructure.models.auth import AppUserEntity
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user
# Import the new GuildTemplateService
from app.web.application.services.guild.template_service import GuildTemplateService 
# TODO: Define response model schema when created
# from app.web.interfaces.api.rest.v1.schemas.guild_template_schemas import GuildTemplateResponse
# Assuming schema exists or define inline for now
from app.web.interfaces.api.rest.v1.schemas.guild_template_schemas import (
    GuildTemplateCreateSchema, 
    GuildTemplateResponseSchema, 
    GuildTemplateListResponseSchema,
    GuildTemplateShareSchema
)

class GuildTemplateController(BaseController):
    """Controller for managing guild structure templates via API."""

    def __init__(self):
        # Define API prefix and tags for guild-specific routes
        super().__init__(prefix="/guilds/{guild_id}/template", tags=["Guild Templates (Guild-Specific)"])
        
        # Define a separate router for non-guild-specific template routes
        self.general_template_router = APIRouter(tags=["Guild Templates (General)"])

        # Instantiate the service directly for now
        # TODO: Replace with proper injection/factory later
        self.template_service = GuildTemplateService()
            
        self._register_routes()

    def _register_routes(self):
        """Register API routes for guild templates."""
        # === Guild-Specific Routes (under /guilds/{guild_id}/template) ===
        
        # Route to get the template data for a specific guild
        self.router.get("", 
                        response_model=GuildTemplateResponseSchema, # Use the detailed response schema
                        summary="Get Guild Structure Template by Guild ID",
                        description="Retrieves the stored structure template (categories, channels, permissions) for the specified guild.")(self.get_guild_template)
        
        # Route to save the current guild structure as a new template
        self.router.post("/save-as", 
                         status_code=status.HTTP_201_CREATED,
                         # response_model=..., # TODO: Define response model for creation? Maybe just 201?
                         summary="Save Guild Structure as New Template",
                         description="Saves the structure of the specified guild as a new named template."
                        )(self.create_guild_template)

        # === General Template Routes (using separate router, NO prefix) ===

        # --- List Guild Structure Templates ---
        self.general_template_router.get("/templates/guilds/", 
                                         response_model=GuildTemplateListResponseSchema,
                                         summary="List Guild Structure Templates",
                                         description="Retrieves a list of accessible guild structure templates."
                                        )(self.list_guild_templates) # NEW method

        # --- Get Specific Guild Structure Template by DB ID ---
        self.general_template_router.get("/templates/guilds/{template_id}", 
                                         response_model=GuildTemplateResponseSchema,
                                         summary="Get Guild Structure Template by DB ID",
                                         description="Retrieves a specific guild structure template using its unique database ID."
                                        )(self.get_guild_template_by_id) # RENAMED method
        
        # --- Delete Specific Guild Structure Template by DB ID ---
        self.general_template_router.delete("/templates/guilds/{template_id}", 
                                          status_code=status.HTTP_204_NO_CONTENT,
                                          summary="Delete Guild Structure Template by DB ID",
                                          description="Deletes a specific guild structure template using its unique database ID."
                                         )(self.delete_guild_template_by_id) # NEW method

        # === NEW Share Route (using general router) ===
        self.general_template_router.post("/templates/guilds/share",
                                          status_code=status.HTTP_201_CREATED,
                                          # response_model=GuildTemplateResponseSchema, # Optional: return the created template
                                          summary="Share/Copy Guild Structure Template",
                                          description="Creates a new template by copying an existing one."
                                          )(self.share_guild_template) # NEW method

    async def get_guild_template(self, guild_id: str, current_user: AppUserEntity = Depends(get_current_user)) -> GuildTemplateResponseSchema:
        """API endpoint to retrieve the guild template structure by Guild ID."""
        try:
            # --- Permission Check ---
            if not current_user.is_owner:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions to view guild template.")

            # --- Call Service Layer ---
            self.logger.info(f"Calling GuildTemplateService to fetch template for guild {guild_id}")
            template_data: Optional[Dict[str, Any]] = await self.template_service.get_template_by_guild(guild_id)
            
            # --- Handle Not Found --- 
            if not template_data:
                self.logger.warning(f"Template not found for guild {guild_id} by service.")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guild template not found for this guild.")
            
            # --- Return Success Response (Data automatically validated by response_model) ---
            self.logger.info(f"Successfully retrieved template data for guild {guild_id}")
            # FastAPI handles validation against GuildTemplateResponseSchema
            # We might need to adjust the keys from the service dict to match the schema field names/aliases
            # Pydantic's populate_by_name in the schema helps here if dict keys match aliases
            return template_data 

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            self.logger.error(f"Error fetching guild template for {guild_id}: {e}", exc_info=True)
            return self.handle_exception(e)

    # --- Method for NEW List Route --- 
    async def list_guild_templates(self, 
                                   current_user: AppUserEntity = Depends(get_current_user),
                                   # Add context_guild_id as an optional query parameter
                                   context_guild_id: Optional[str] = None 
                                  ) -> GuildTemplateListResponseSchema:
        """API endpoint to list guild structure templates visible to the current user,
           optionally including the initial snapshot for a specific context guild.
        """ # Updated docstring
        self.logger.info(f"Listing templates requested by user {current_user.id}. Context guild_id: {context_guild_id}") # Updated log
        try:
            # TODO: Add permission check if needed 
            pass 

            # --- Call Service Layer --- 
            # Pass user ID and context guild ID to the service for filtering
            templates_list: List[Dict[str, Any]] = await self.template_service.list_templates(
                user_id=current_user.id, 
                context_guild_id=context_guild_id
            )

            # --- Return Success Response --- 
            return {"templates": templates_list}

        except Exception as e:
            self.logger.error(f"Error listing guild templates: {e}", exc_info=True)
            # Use base controller handler or raise generic 500
            return self.handle_exception(e)

    # --- RENAMED Method for Get by ID Route --- 
    async def get_guild_template_by_id(self, template_id: int, current_user: AppUserEntity = Depends(get_current_user)) -> GuildTemplateResponseSchema:
        """API endpoint to retrieve a specific guild template by its database ID."""
        try:
            pass # Assuming any authenticated user can fetch for now (permissions check placeholder)
            
            self.logger.info(f"Calling GuildTemplateService to fetch template by database ID {template_id}")
            template_data: Optional[Dict[str, Any]] = await self.template_service.get_template_by_id(template_id)

            if not template_data:
                self.logger.warning(f"Template not found for database ID {template_id} by service.")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guild template not found.")
            
            self.logger.info(f"Successfully retrieved template data for database ID {template_id}")
            return template_data

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            self.logger.error(f"Error fetching template for database ID {template_id}: {e}", exc_info=True)
            return self.handle_exception(e)
            
    # --- Method for NEW Delete Route --- 
    async def delete_guild_template_by_id(self, template_id: int, current_user: AppUserEntity = Depends(get_current_user)):
        """API endpoint to delete a specific guild template by its database ID."""
        try:
            # TODO: Add permission check (e.g., only owner/creator can delete?)
            self.logger.info(f"User {current_user.id} requesting deletion of template ID {template_id}")
            
            # --- Call Service Layer --- 
            # Assuming service has a delete method - needs implementation
            deleted_successfully = await self.template_service.delete_template(template_id)

            if not deleted_successfully:
                 self.logger.warning(f"Failed to delete template ID {template_id}. It might not exist or service failed.")
                 raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found or could not be deleted.")

            self.logger.info(f"Successfully deleted template ID {template_id}")
            # Return nothing for 204 No Content status
            return

        except HTTPException as http_exc:
            raise http_exc # Includes 404 if not found
        except NotImplementedError:
             self.logger.error(f"Template deletion service method not implemented for ID {template_id}")
             raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Template deletion not implemented.")
        except Exception as e:
            self.logger.error(f"Error deleting template ID {template_id}: {e}", exc_info=True)
            return self.handle_exception(e)

    # --- NEW Method for Share Route ---
    async def share_guild_template(
        self,
        share_data: GuildTemplateShareSchema, # <-- Use the imported schema
        current_user: AppUserEntity = Depends(get_current_user)
        # Optional: Return type can be GuildTemplateResponseSchema if you return the new template
    ): # -> GuildTemplateResponseSchema: 
        """API endpoint to create a new template by sharing/copying an existing one."""
        try:
            # --- Permission Check (Example: Any logged-in user can share?) ---
            # Add more specific checks if needed
            if not current_user:
                 raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

            self.logger.info(f"User {current_user.id} requesting to share/copy template ID {share_data.original_template_id} as '{share_data.new_template_name}'")

            # --- Call Service Layer (Assumes service method exists) ---
            # TODO: Implement self.template_service.share_template
            new_template = await self.template_service.share_template(
                original_template_id=share_data.original_template_id,
                new_name=share_data.new_template_name,
                new_description=share_data.new_template_description,
                creator_user_id=current_user.id # Pass user ID for ownership/tracking
            )

            # --- Handle Service Failure ---
            if not new_template:
                self.logger.error(f"Service failed to share/copy template ID {share_data.original_template_id} as '{share_data.new_template_name}'")
                # More specific error checking might be needed in the service layer
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to share template. Ensure original template exists and new name '{share_data.new_template_name}' is valid/unique.")

            self.logger.info(f"Successfully shared/copied template ID {share_data.original_template_id} as '{share_data.new_template_name}' (New ID: {new_template.get('template_id', 'N/A')})")
            # Option 1: Return 201 No Content (if frontend doesn't need the new template details)
            # return 
            # Option 2: Return the newly created template data (requires response_model setup)
            # return new_template 
            # For now, just return 201 implicitly by not returning content
            return

        except HTTPException as http_exc:
            raise http_exc
        except NotImplementedError:
             self.logger.error(f"Template sharing service method not implemented for original ID {share_data.original_template_id}")
             raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Template sharing not implemented.")
        except Exception as e:
            self.logger.error(f"Error sharing template ID {share_data.original_template_id} as '{share_data.new_template_name}': {e}", exc_info=True)
            # Use base controller handler or raise generic 500
            return self.handle_exception(e)

    # --- NEUE METHODE --- 
    async def create_guild_template(
        self, 
        guild_id: str, # Get guild_id from path
        template_data: GuildTemplateCreateSchema, # Use schema for body
        current_user: AppUserEntity = Depends(get_current_user)
    ):
        """API endpoint to save the current guild's structure as a new template."""
        try:
            # --- Permission Check --- 
            if not current_user.is_owner:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions to create guild templates.")

            # --- Call Service Layer --- 
            self.logger.info(f"User {current_user.id} requesting to save guild {guild_id} structure as template '{template_data.template_name}'")
            
            # Pass guild_id from path to service
            created_template = await self.template_service.create_template_from_guild(
                source_guild_id=guild_id, # Use guild_id from path
                template_name=template_data.template_name,
                template_description=template_data.template_description,
                creator_user_id=current_user.id
            )
            
            # --- Handle Service Failure --- 
            if not created_template:
                 self.logger.error(f"Service failed to create template '{template_data.template_name}' from guild {guild_id}")
                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create template. Ensure source guild exists and template name '{template_data.template_name}' is unique.")
            
            self.logger.info(f"Successfully created guild template '{template_data.template_name}' by user {current_user.id}")
            return # Status 201 indicates success

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            self.logger.error(f"Error creating guild template '{template_data.template_name}' from {guild_id}: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create guild template due to an unexpected error.")

# Instantiate the controller for registration
guild_template_controller = GuildTemplateController() 
