from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, Dict, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
import httpx # Keep for now, might be needed by BaseController indirectly or future methods

from app.web.interfaces.api.rest.v1.base_controller import BaseController
from app.shared.infrastructure.models.auth import AppUserEntity
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user, get_web_db_session
from app.web.application.services.template.template_service import GuildTemplateService
from app.web.interfaces.api.rest.v1.schemas.guild_template_schemas import (
    GuildTemplateCreateSchema,      # For save-as
    GuildTemplateResponseSchema,
    GuildTemplateListResponseSchema,
    GuildTemplateShareSchema,       # For share
    GuildTemplateMetadataUpdateSchema,
    GuildStructureTemplateInfo      # For copy_shared response mapping potentially
)
from app.shared.domain.exceptions import TemplateNotFound, PermissionDenied, InvalidOperation, ConfigurationNotFound
from app.shared.interfaces.logging.api import get_web_logger

logger = get_web_logger()

class GuildTemplateMetadataController(BaseController):
    """Controller for managing guild template metadata, listing, sharing, and copying."""

    def __init__(self):
        # Use the specific prefix for template management within a guild context
        super().__init__(prefix="/guilds/{guild_id}/template", tags=["Guild Templates (Metadata & Management)"])
        self.template_service = GuildTemplateService()
        self._register_routes()

    def _register_routes(self):
        """Register API routes for template metadata and management."""

        # Route to get the template data for a specific guild (added during previous refactor)
        self.router.get("",
                        response_model=GuildTemplateResponseSchema,
                        summary="Get Guild Structure Template by Guild ID",
                        description="Retrieves the stored structure template for the specified guild.")(self.get_guild_template)

        # List templates visible to user (in guild context)
        self.router.get("/",
                        response_model=GuildTemplateListResponseSchema,
                        summary="List Guild Structure Templates",
                        description="Retrieves a list of accessible guild structure templates.")(self.list_guild_templates)

        # Get specific template by DB ID
        self.router.get("/{template_id}",
                        response_model=GuildTemplateResponseSchema,
                        summary="Get Guild Structure Template by DB ID",
                        description="Retrieves a specific guild structure template by its unique database ID.")(self.get_guild_template_by_id)

        # Update template metadata (name, etc.)
        self.router.put("/{template_id}/metadata",
                        response_model=GuildTemplateResponseSchema,
                        status_code=status.HTTP_200_OK,
                        summary="Update Guild Template Metadata",
                        description="Updates the metadata of a specific guild template.")(self.update_template_metadata)

        # Delete specific template by DB ID
        self.router.delete("/{template_id}",
                           status_code=status.HTTP_204_NO_CONTENT,
                           summary="Delete Guild Structure Template by DB ID",
                           description="Deletes a specific guild structure template.")(self.delete_guild_template_by_id)

        # Share/Copy an existing template to create a new one
        self.router.post("/share",
                         status_code=status.HTTP_201_CREATED,
                         summary="Share/Copy Guild Structure Template",
                         description="Creates a new template by copying an existing one.")(self.share_guild_template)

        # List publicly shared templates
        self.router.get("/shared/",
                        response_model=GuildTemplateListResponseSchema,
                        summary="List Shared Guild Structure Templates",
                        description="Retrieves a list of publicly shared templates.")(self.list_shared_guild_templates)

        # Get details of a specific shared template
        self.router.get("/shared/{template_id}",
                        response_model=GuildTemplateResponseSchema,
                        summary="Get Shared Guild Structure Template Details",
                        description="Retrieves the full structure of a shared template.")(self.get_shared_guild_template_details)

        # Copy a shared template to the user's saved templates
        self.router.post("/copy_shared",
                         status_code=status.HTTP_201_CREATED,
                         summary="Copy Shared Template to Saved Templates",
                         description="Copies a shared template and saves it for the user.")(self.copy_shared_template)

        # Save current guild structure as a new template
        self.router.post("/save-as",
                         status_code=status.HTTP_201_CREATED,
                         summary="Save Guild Structure as New Template",
                         description="Saves the current guild structure as a new template.")(self.create_guild_template)


    # --- Method Implementations --- 

    async def get_guild_template(self, guild_id: str, current_user: AppUserEntity = Depends(get_current_user)) -> GuildTemplateResponseSchema:
        """API endpoint to retrieve the guild template structure by Guild ID."""
        try:
            if not current_user.is_owner: # Basic check for now
                raise PermissionDenied("Insufficient permissions to view this guild template.")

            logger.info(f"Calling GuildTemplateService to fetch template for guild {guild_id}")
            template_data: Optional[Dict[str, Any]] = await self.template_service.get_template_by_guild(guild_id)

            if not template_data:
                logger.warning(f"Template not found for guild {guild_id} by service.")
                raise TemplateNotFound(guild_id=guild_id)

            logger.info(f"Successfully retrieved template data for guild {guild_id}")
            return template_data

        except (TemplateNotFound, PermissionDenied) as e:
            status_code = status.HTTP_404_NOT_FOUND if isinstance(e, TemplateNotFound) else status.HTTP_403_FORBIDDEN
            logger.warning(f"Failed to get template for guild {guild_id}: {e}")
            raise HTTPException(status_code=status_code, detail=str(e))
        except Exception as e:
            logger.error(f"Error fetching guild template for {guild_id}: {e}", exc_info=True)
            return self.handle_exception(e) # Use BaseController handler

    async def list_guild_templates(self,
                                   guild_id: str, # Context guild
                                   current_user: AppUserEntity = Depends(get_current_user),
                                   context_guild_id: Optional[str] = None # Optional: For fetching initial snapshot
                                  ) -> GuildTemplateListResponseSchema:
        """API endpoint to list guild structure templates visible to the current user."""
        logger.info(f"Listing templates requested by user {current_user.id}. Context guild_id: {context_guild_id}")
        try:
            templates_list: List[Dict[str, Any]] = await self.template_service.list_templates(
                user_id=current_user.id,
                context_guild_id=context_guild_id
            )
            return {"templates": templates_list}
        except Exception as e:
            logger.error(f"Error listing guild templates: {e}", exc_info=True)
            return self.handle_exception(e) # Use BaseController handler

    async def get_guild_template_by_id(self,
                                     guild_id: str, # Context guild
                                     template_id: int,
                                     current_user: AppUserEntity = Depends(get_current_user)
                                    ) -> GuildTemplateResponseSchema:
        """API endpoint to retrieve a specific guild template by its database ID."""
        try:
            # Permissions might be checked in service or here if needed
            logger.info(f"Calling GuildTemplateService to fetch template by database ID {template_id}")
            template_data: Optional[Dict[str, Any]] = await self.template_service.get_template_by_id(template_id)

            if not template_data:
                logger.warning(f"Template not found for database ID {template_id} by service.")
                raise TemplateNotFound(template_id=template_id)

            logger.info(f"Successfully retrieved template data for database ID {template_id}")
            return template_data
        except TemplateNotFound as e:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except Exception as e:
            logger.error(f"Error fetching template for database ID {template_id}: {e}", exc_info=True)
            return self.handle_exception(e) # Use BaseController handler

    async def update_template_metadata(
        self,
        guild_id: str, # Context guild
        template_id: int,
        metadata_update: GuildTemplateMetadataUpdateSchema,
        current_user: AppUserEntity = Depends(get_current_user),
        db: AsyncSession = Depends(get_web_db_session)
    ) -> GuildTemplateResponseSchema:
        """API endpoint to update the metadata (e.g., name) of a guild template."""
        logger.info(f"Metadata update requested for template {template_id} in guild {guild_id} by user {current_user.id}")
        try:
            # Service handles permission check
            updated_template_data = await self.template_service.update_template_metadata(
                db=db,
                template_id=template_id,
                new_name=metadata_update.name,
                requesting_user=current_user
            )
            logger.info(f"Successfully updated metadata for template {template_id}")
            return updated_template_data
        except (TemplateNotFound, PermissionDenied) as service_exc:
            status_code = status.HTTP_404_NOT_FOUND if isinstance(service_exc, TemplateNotFound) else status.HTTP_403_FORBIDDEN
            logger.warning(f"Service error during metadata update for template {template_id}: {service_exc}")
            raise HTTPException(status_code=status_code, detail=str(service_exc))
        except Exception as e:
            logger.error(f"Unexpected error updating metadata for template {template_id}: {e}", exc_info=True)
            return self.handle_exception(e) # Use BaseController handler

    async def delete_guild_template_by_id(self,
                                        guild_id: str, # Context guild
                                        template_id: int,
                                        current_user: AppUserEntity = Depends(get_current_user)
                                       ):
        """API endpoint to delete a specific guild template by its database ID."""
        try:
            # Service handles permission check
            logger.info(f"User {current_user.id} requesting deletion of template ID {template_id}.")
            deleted_successfully = await self.template_service.delete_template(template_id, current_user)

            if not deleted_successfully:
                 logger.error(f"Template deletion service returned False for ID {template_id}.")
                 # Should not happen if service raises exceptions correctly
                 raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not delete template due to an unexpected server error.")

            logger.info(f"Successfully deleted template ID {template_id}")
            return # Return None for 204
        except TemplateNotFound as e:
             logger.warning(f"Delete failed: Template ID {template_id} not found.")
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except PermissionDenied as e:
             logger.warning(f"Permission denied: User {current_user.id} attempted to delete template {template_id}. Details: {e}")
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        except Exception as e:
            logger.error(f"Error deleting template ID {template_id}: {e}", exc_info=True)
            return self.handle_exception(e) # Use BaseController handler

    async def share_guild_template(
        self,
        guild_id: str, # Context guild
        share_data: GuildTemplateShareSchema,
        current_user: AppUserEntity = Depends(get_current_user)
    ):
        """API endpoint to create a new template by sharing/copying an existing one."""
        try:
            # Basic auth check
            if not current_user:
                 raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

            logger.info(f"User {current_user.id} requesting to share/copy template ID {share_data.original_template_id} as '{share_data.new_template_name}'")

            new_template = await self.template_service.share_template(
                original_template_id=share_data.original_template_id,
                new_name=share_data.new_template_name,
                new_description=share_data.new_template_description,
                creator_user_id=current_user.id
            )

            # Service raises specific exceptions on failure
            logger.info(f"Successfully shared/copied template ID {share_data.original_template_id} as '{share_data.new_template_name}' (New ID: {new_template.get('template_id', 'N/A')})")
            return # Return 201 implicitly
        except HTTPException as http_exc:
            raise http_exc # Re-raise explicit HTTP exceptions
        except TemplateNotFound as e:
             logger.warning(f"Share failed: Original template ID {share_data.original_template_id} not found.")
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except ValueError as e: # Duplicate name or other validation
             logger.warning(f"Share failed due to validation error: {e}")
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            logger.error(f"Error sharing template ID {share_data.original_template_id} as '{share_data.new_template_name}': {e}", exc_info=True)
            return self.handle_exception(e) # Use BaseController handler

    async def list_shared_guild_templates(self,
                                        guild_id: str, # Context guild
                                        current_user: AppUserEntity = Depends(get_current_user)
                                       ) -> GuildTemplateListResponseSchema:
        """API endpoint to list publicly shared guild structure templates."""
        logger.info(f"Listing shared templates requested by user {current_user.id}")
        try:
            templates_list: List[Dict[str, Any]] = await self.template_service.list_shared_templates()
            return {"templates": templates_list}
        except Exception as e:
            logger.error(f"Error listing shared guild templates: {e}", exc_info=True)
            return self.handle_exception(e) # Use BaseController handler

    async def get_shared_guild_template_details(self,
                                              guild_id: str, # Context guild
                                              template_id: int,
                                              current_user: AppUserEntity = Depends(get_current_user)
                                             ) -> GuildTemplateResponseSchema:
        """API endpoint to retrieve the full details of a specific shared guild template by its ID."""
        logger.info(f"Fetching details for shared template ID {template_id} requested by user {current_user.id}")
        try:
            template_data: Optional[Dict[str, Any]] = await self.template_service.get_shared_template_details(template_id)

            if not template_data:
                logger.warning(f"Shared template not found for ID {template_id} by service.")
                raise TemplateNotFound(template_id=template_id, is_shared=True)

            logger.info(f"Successfully retrieved shared template data for ID {template_id}")
            return template_data
        except TemplateNotFound as e:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except Exception as e:
            logger.error(f"Error fetching shared template details for ID {template_id}: {e}", exc_info=True)
            return self.handle_exception(e) # Use BaseController handler

    async def copy_shared_template(
        self,
        guild_id: str, # Context guild
        copy_request: dict, # Body: {"shared_template_id": int, "new_name": str (optional)}
        current_user: AppUserEntity = Depends(get_current_user)
    ):
        """API endpoint to copy a shared template to the current user's saved templates."""
        shared_template_id = copy_request.get('shared_template_id')
        new_name_optional = copy_request.get('new_name')

        if not shared_template_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing 'shared_template_id' in request body.")

        logger.info(f"User {current_user.id} requested copy of shared template ID {shared_template_id}. Optional new name: '{new_name_optional}'")
        try:
            # Service handles logic and raises exceptions
            new_saved_template_info = await self.template_service.copy_shared_template(
                shared_template_id=shared_template_id,
                user_id=current_user.id,
                new_name_optional=new_name_optional
            )
            logger.info(f"Successfully copied shared template ID {shared_template_id} for user {current_user.id}. New template info: {new_saved_template_info}")
            return # Return 201 implicitly
        except TemplateNotFound as e:
             logger.warning(f"Copy shared failed: Shared template ID {shared_template_id} not found.")
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except ValueError as e: # Duplicate name or other validation
             logger.warning(f"Copy shared failed due to validation error: {e}")
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            logger.error(f"Error copying shared template ID {shared_template_id} for user {current_user.id}: {e}", exc_info=True)
            return self.handle_exception(e) # Use BaseController handler

    async def create_guild_template(
        self,
        guild_id: str, # Source guild
        template_data: GuildTemplateCreateSchema,
        current_user: AppUserEntity = Depends(get_current_user)
    ):
        """API endpoint to save the current guild's structure as a new template."""
        try:
            if not current_user.is_owner: # Basic check for now
                raise PermissionDenied("Insufficient permissions to save guild structure as template.")

            logger.info(f"User {current_user.id} requesting to save guild {guild_id} structure as template '{template_data.template_name}'")
            # Service handles logic and exceptions
            created_template = await self.template_service.create_template_from_guild(
                source_guild_id=guild_id,
                template_name=template_data.template_name,
                template_description=template_data.template_description,
                creator_user_id=current_user.id
            )
            logger.info(f"Successfully created guild template '{template_data.template_name}' from guild {guild_id} by user {current_user.id}")
            return # Status 201 indicates success
        except PermissionDenied as e:
             logger.warning(f"Save-as template failed for guild {guild_id}: {e}")
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        except ValueError as e: # Duplicate name or invalid guild
             logger.warning(f"Save-as template failed for guild {guild_id}: {e}")
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            logger.error(f"Error creating guild template '{template_data.template_name}' from {guild_id}: {e}", exc_info=True)
            return self.handle_exception(e) # Use BaseController handler

# Instantiate the controller for registration
metadata_controller = GuildTemplateMetadataController()
# <<< END OF FILE >>>
