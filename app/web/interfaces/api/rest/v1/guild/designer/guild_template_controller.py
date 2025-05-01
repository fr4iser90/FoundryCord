from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, Dict, Optional, List
from app.web.interfaces.api.rest.v1.base_controller import BaseController
from app.shared.infrastructure.models.auth import AppUserEntity
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user, get_web_db_session
# Import the new GuildTemplateService
from app.web.application.services.template.template_service import GuildTemplateService 
# TODO: Define response model schema when created
# from app.web.interfaces.api.rest.v1.schemas.guild_template_schemas import GuildTemplateResponse
# Assuming schema exists or define inline for now
from app.web.interfaces.api.rest.v1.schemas.guild_template_schemas import (
    GuildTemplateCreateSchema, 
    GuildTemplateResponseSchema, 
    GuildTemplateListResponseSchema,
    GuildTemplateShareSchema,
    GuildStructureUpdatePayload,
    GuildStructureUpdateResponse,
    GuildStructureTemplateCreateFromStructure,
    GuildStructureTemplateInfo,
    GuildTemplateMetadataUpdateSchema
)
# --- Define Schemas Locally if not imported --- 
from pydantic import BaseModel, Field
# --- Add imports for permission check ---
from app.shared.infrastructure.database.session import session_context
# Schema for activate request
from pydantic import BaseModel
# --- Add imports for permission check ---
from app.shared.infrastructure.models import DiscordGuildUserEntity
from sqlalchemy import select
# ---------------------------------------
from sqlalchemy.ext.asyncio import AsyncSession # Import AsyncSession
# ---> ADD: Import specific exceptions from service/domain if they exist
from app.shared.domain.exceptions import TemplateNotFound, PermissionDenied, InvalidOperation, ConfigurationNotFound # Added ConfigurationNotFound
# --- NEW: Add HTTP client import (adjust based on available library) ---
import httpx 
# --- NEW: Import logging API and create logger ---
from app.shared.interface.logging.api import get_web_logger
logger = get_web_logger()
# -------------------------------------------------------------------
# --- NEW: Import settings if available --- 
# from app.web.core.config import settings # Example, adjust path as needed
INTERNAL_API_BASE_URL = "http://foundrycord-bot:9090" # Use container name, GET FROM CONFIG ideally
# ----------------------------------------

class GuildTemplateActivateSchema(BaseModel):
    template_id: int

# --- NEW Schema for Settings Update ---
class GuildTemplateSettingsUpdate(BaseModel):
    delete_unmanaged: bool
# --------------------------------------

class GuildTemplateController(BaseController):
    """Controller for managing guild structure templates via API."""

    def __init__(self):
        # Define API prefix and tags for guild-specific routes
        super().__init__(prefix="/guilds/{guild_id}/template", tags=["Guild Templates (Guild-Specific)"])
        
        # Define a separate router for non-guild-specific template routes - REMOVED
        # self.general_template_router = APIRouter(tags=["Guild Templates (General)"])

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

        # --- NEW Guild-Specific Activate Route --- 
        self.router.post("/templates/{template_id}/activate", # Path relative to /guilds/{guild_id}/
                         status_code=status.HTTP_200_OK,
                         summary="Activate Guild Template for specific Guild",
                         description="Marks a specific template as the active one for the specified guild."
                         )(self.activate_guild_template) # Method signature needs update

        # --- Apply Template Route (Remains Guild-Specific) ---
        self.router.post("/apply",
                         status_code=status.HTTP_200_OK, # Or 202 Accepted if it takes time?
                         summary="Apply Active Template to Discord",
                         description="Triggers the bot to apply the currently active template structure to the live Discord server."
                         )(self.apply_guild_template) # NEW method

        # --- NEW Route for Updating Settings --- 
        self.router.put("/settings",
                        status_code=status.HTTP_200_OK,
                        summary="Update Guild Template Application Settings",
                        description="Updates settings related to how templates are applied for this guild, e.g., deleting unmanaged channels."
                        )(self.update_template_settings)
        # ------------------------------------------

        # === General Template Routes (MOVED to self.router, NO prefix needed) ===

        # --- List Guild Structure Templates --- (Path changed to relative '/', method signature updated)
        self.router.get("/", 
                        response_model=GuildTemplateListResponseSchema,
                        summary="List Guild Structure Templates (Now Guild-Specific Context)",
                        description="Retrieves a list of accessible guild structure templates (now relative to guild)."
                       )(self.list_guild_templates) # Signature updated

        # --- Get Specific Guild Structure Template by DB ID --- (Path changed, method signature updated)
        self.router.get("/{template_id}", 
                        response_model=GuildTemplateResponseSchema,
                        summary="Get Guild Structure Template by DB ID (Now Guild-Specific Context)",
                        description="Retrieves a specific guild structure template using its unique database ID."
                       )(self.get_guild_template_by_id) # Signature updated
        
        # --- NEW: Route for updating template metadata (e.g., name) ---
        self.router.put("/{template_id}/metadata",
                        response_model=GuildTemplateResponseSchema, # Return the updated template
                        status_code=status.HTTP_200_OK,
                        summary="Update Guild Template Metadata (Name, etc.)",
                        description="Updates the metadata (like the name) of a specific guild template."
                        )(self.update_template_metadata)

        # --- Delete Specific Guild Structure Template by DB ID --- (Path changed, method signature updated)
        self.router.delete("/{template_id}", 
                           status_code=status.HTTP_204_NO_CONTENT,
                           summary="Delete Guild Structure Template by DB ID (Now Guild-Specific Context)",
                           description="Deletes a specific guild structure template using its unique database ID."
                          )(self.delete_guild_template_by_id) # Signature updated

        # === NEW Share Route (Path changed, method signature updated) ===
        self.router.post("/share",
                         status_code=status.HTTP_201_CREATED,
                         # response_model=GuildTemplateResponseSchema, # Optional: return the created template
                         summary="Share/Copy Guild Structure Template (Now Guild-Specific Context)",
                         description="Creates a new template by copying an existing one."
                         )(self.share_guild_template) # Signature updated

        # === NEW Shared Templates List Route (Path changed, method signature updated) ===
        self.router.get("/shared/",
                        response_model=GuildTemplateListResponseSchema, # Use the same list schema for now
                        summary="List Shared Guild Structure Templates (Now Guild-Specific Context)",
                        description="Retrieves a list of publicly shared guild structure templates."
                        )(self.list_shared_guild_templates) # Signature updated

        # === NEW Get Shared Template Details Route (Path changed, method signature updated) ===
        self.router.get("/shared/{template_id}",
                        response_model=GuildTemplateResponseSchema, # Use the detailed schema
                        summary="Get Shared Guild Structure Template Details by ID (Now Guild-Specific Context)",
                        description="Retrieves the full structure of a specific publicly shared guild template by its ID."
                        )(self.get_shared_guild_template_details) # Signature updated
        
        # === NEW Copy Shared Template Route (Path changed, method signature updated) ===
        self.router.post("/copy_shared",
                         status_code=status.HTTP_201_CREATED,
                         # response_model=GuildTemplateResponseSchema, # Optional: Return the new saved template
                         summary="Copy Shared Template to Saved Templates (Now Guild-Specific Context)",
                         description="Creates a copy of a shared guild structure template and saves it for the current user."
                         )(self.copy_shared_template) # Signature updated

        # --- REGISTER NEW PUT Route for Structure Update (Path changed, signature updated) --- 
        self.router.put(
            "/{template_id}/structure",
            summary="Update Guild Template Structure (Now Guild-Specific Context)",
            description="Updates the categories and channels structure of a specific guild template based on provided node list.",
            response_model=GuildTemplateResponseSchema,
            status_code=status.HTTP_200_OK,
            dependencies=[Depends(get_current_user)] # Keep dependency here
        )(self.update_guild_template_structure) # Signature updated

        # --- REGISTER NEW POST Route for Creating from Structure (Path changed, signature updated) --- 
        self.router.post(
            "/from_structure",
            summary="Create Guild Template from Structure Payload (Now Guild-Specific Context)",
            description="Creates a new guild template based on a provided structure payload (typically from the designer).",
            response_model=GuildStructureTemplateInfo, # Return info of the new template
            status_code=status.HTTP_201_CREATED,
            dependencies=[Depends(get_current_user)] # Keep dependency here
        )(self.create_template_from_structure) # Signature updated

        # === NEW DELETE Endpoints for Categories/Channels (Already moved to self.router) ===
        self.router.delete(
            "/categories/{category_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Delete Template Category by DB ID (Now Guild-Specific Context)",
            description="Deletes a specific category from a guild template using its unique database ID."
        )(self.delete_template_category)

        self.router.delete(
            "/channels/{channel_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Delete Template Channel by DB ID (Now Guild-Specific Context)",
            description="Deletes a specific channel from a guild template using its unique database ID."
        )(self.delete_template_channel)
        # ====================================================

    async def get_guild_template(self, guild_id: str, current_user: AppUserEntity = Depends(get_current_user)) -> GuildTemplateResponseSchema:
        """API endpoint to retrieve the guild template structure by Guild ID."""
        try:
            # --- Permission Check ---
            if not current_user.is_owner:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions to view guild template.")

            # --- Call Service Layer ---
            logger.info(f"Calling GuildTemplateService to fetch template for guild {guild_id}")
            template_data: Optional[Dict[str, Any]] = await self.template_service.get_template_by_guild(guild_id)
            
            # --- Handle Not Found --- 
            if not template_data:
                logger.warning(f"Template not found for guild {guild_id} by service.")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guild template not found for this guild.")
            
            # --- Return Success Response (Data automatically validated by response_model) ---
            logger.info(f"Successfully retrieved template data for guild {guild_id}")
            # FastAPI handles validation against GuildTemplateResponseSchema
            # We might need to adjust the keys from the service dict to match the schema field names/aliases
            # Pydantic's populate_by_name in the schema helps here if dict keys match aliases
            return template_data 

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            logger.error(f"Error fetching guild template for {guild_id}: {e}", exc_info=True)
            return self.handle_exception(e)

    # --- Method for NEW List Route (Signature updated) --- 
    async def list_guild_templates(self, 
                                   guild_id: str, # <<< ADDED guild_id
                                   current_user: AppUserEntity = Depends(get_current_user),
                                   # Add context_guild_id as an optional query parameter
                                   context_guild_id: Optional[str] = None 
                                  ) -> GuildTemplateListResponseSchema:
        """API endpoint to list guild structure templates visible to the current user,
           optionally including the initial snapshot for a specific context guild.
        """ # Updated docstring
        logger.info(f"Listing templates requested by user {current_user.id}. Context guild_id: {context_guild_id}") # Updated log
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
            logger.error(f"Error listing guild templates: {e}", exc_info=True)
            # Use base controller handler or raise generic 500
            return self.handle_exception(e)

    # --- RENAMED Method for Get by ID Route (Signature updated) --- 
    async def get_guild_template_by_id(self, 
                                     guild_id: str, 
                                     template_id: int, 
                                     current_user: AppUserEntity = Depends(get_current_user)
                                    ) -> GuildTemplateResponseSchema:
        """API endpoint to retrieve a specific guild template by its database ID."""
        try:
            pass # Assuming any authenticated user can fetch for now (permissions check placeholder)
            
            logger.info(f"Calling GuildTemplateService to fetch template by database ID {template_id}")
            template_data: Optional[Dict[str, Any]] = await self.template_service.get_template_by_id(template_id)

            if not template_data:
                logger.warning(f"Template not found for database ID {template_id} by service.")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guild template not found.")
            
            logger.info(f"Successfully retrieved template data for database ID {template_id}")
            return template_data

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            logger.error(f"Error fetching template for database ID {template_id}: {e}", exc_info=True)
            return self.handle_exception(e)
            
    # --- Method for NEW Delete Route (Signature updated) --- 
    async def delete_guild_template_by_id(self, 
                                        guild_id: str, # <<< ADDED guild_id
                                        template_id: int, 
                                        current_user: AppUserEntity = Depends(get_current_user)
                                       ):
        """API endpoint to delete a specific guild template by its database ID."""
        try:
            # --- Permission Check --- 
            # Fetch the template first to check ownership
            # We need the service method that returns the raw entity or at least the creator ID
            # Let's use get_template_by_id but access the underlying entity if possible, 
            # or modify get_template_by_id in service to return creator_id if needed.
            # Assuming template_service.get_raw_template_by_id or similar exists for simplicity
            # For now, let's assume get_template_by_id fetches enough info (we need creator_id)
            
            # Fetch the template data (which should include creator_user_id if structured correctly)
            template_to_delete = await self.template_service.get_template_by_id(template_id)
            
            if not template_to_delete:
                logger.warning(f"Delete failed: Template ID {template_id} not found.")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found.")
            
            # Check if the current user is the creator OR a bot owner
            # The service returns a dict, ensure it includes creator_user_id
            creator_id = template_to_delete.get('creator_user_id') # Get creator ID from the dict
            
            is_creator = (creator_id is not None and creator_id == current_user.id)
            is_owner = current_user.is_owner # Assuming is_owner flag is available

            if not is_creator and not is_owner:
                logger.warning(f"Permission denied: User {current_user.id} attempted to delete template {template_id} created by {creator_id}.")
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this template.")
            
            logger.info(f"Permission granted for user {current_user.id} to delete template {template_id} (Is Creator: {is_creator}, Is Owner: {is_owner}).")
            # --- End Permission Check ---

            # --- Call Service Layer --- 
            # Assuming service has a delete method - needs implementation
            deleted_successfully = await self.template_service.delete_template(template_id)

            if not deleted_successfully:
                 logger.warning(f"Failed to delete template ID {template_id}. It might not exist or service failed.")
                 # Keep 404 if not found, maybe 500 if service failed unexpectedly?
                 # Since we checked existence above, this implies a service/DB error during delete
                 raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not delete template due to a server error.")

            logger.info(f"Successfully deleted template ID {template_id}")
            # Return nothing for 204 No Content status
            return

        except HTTPException as http_exc:
            raise http_exc # Includes 404 if not found
        except NotImplementedError:
             logger.error(f"Template deletion service method not implemented for ID {template_id}")
             raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Template deletion not implemented.")
        except Exception as e:
            logger.error(f"Error deleting template ID {template_id}: {e}", exc_info=True)
            return self.handle_exception(e)

    # --- NEW Method for Share Route (Signature updated) --- 
    async def share_guild_template(
        self,
        guild_id: str, # <<< ADDED guild_id
        share_data: GuildTemplateShareSchema,
        current_user: AppUserEntity = Depends(get_current_user)
        # Optional: Return type can be GuildTemplateResponseSchema if you return the new template
    ): # -> GuildTemplateResponseSchema: 
        """API endpoint to create a new template by sharing/copying an existing one."""
        try:
            # --- Permission Check (Example: Any logged-in user can share?) ---
            # Add more specific checks if needed
            if not current_user:
                 raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

            logger.info(f"User {current_user.id} requesting to share/copy template ID {share_data.original_template_id} as '{share_data.new_template_name}'")

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
                logger.error(f"Service failed to share/copy template ID {share_data.original_template_id} as '{share_data.new_template_name}'")
                # More specific error checking might be needed in the service layer
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to share template. Ensure original template exists and new name '{share_data.new_template_name}' is valid/unique.")

            logger.info(f"Successfully shared/copied template ID {share_data.original_template_id} as '{share_data.new_template_name}' (New ID: {new_template.get('template_id', 'N/A')})")
            # Option 1: Return 201 No Content (if frontend doesn't need the new template details)
            # return 
            # Option 2: Return the newly created template data (requires response_model setup)
            # return new_template 
            # For now, just return 201 implicitly by not returning content
            return

        except HTTPException as http_exc:
            raise http_exc
        except NotImplementedError:
             logger.error(f"Template sharing service method not implemented for original ID {share_data.original_template_id}")
             raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Template sharing not implemented.")
        except Exception as e:
            logger.error(f"Error sharing template ID {share_data.original_template_id} as '{share_data.new_template_name}': {e}", exc_info=True)
            # Use base controller handler or raise generic 500
            return self.handle_exception(e)

    # --- NEW Method for Shared List Route (Signature updated) ---
    async def list_shared_guild_templates(self, 
                                        guild_id: str, # <<< ADDED guild_id
                                        current_user: AppUserEntity = Depends(get_current_user)
                                       ) -> GuildTemplateListResponseSchema:
        """API endpoint to list publicly shared guild structure templates."""
        logger.info(f"Listing shared templates requested by user {current_user.id}")
        try:
            # --- Permission Check (Example: Any logged-in user can view shared?) ---
            pass

            # --- Call Service Layer --- 
            # Call the correct service method
            templates_list: List[Dict[str, Any]] = await self.template_service.list_shared_templates()
            # Remove placeholder/warning log from previous version if present
            # self.logger.warning(\"Shared template listing service method not implemented yet. Returning empty list.\")

            # --- Return Success Response ---
            return {"templates": templates_list}

        except NotImplementedError: # Keep this handler in case service method is somehow still missing
             logger.error(f"Shared template listing service method not implemented.")
             raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Shared template listing not implemented.")
        except Exception as e:
            logger.error(f"Error listing shared guild templates: {e}", exc_info=True)
            # Use base controller handler or raise generic 500
            return self.handle_exception(e)

    # --- NEW Method for Get Shared Template Details Route (Signature updated) ---
    async def get_shared_guild_template_details(self, 
                                              guild_id: str, # <<< ADDED guild_id
                                              template_id: int, 
                                              current_user: AppUserEntity = Depends(get_current_user)
                                             ) -> GuildTemplateResponseSchema:
        """API endpoint to retrieve the full details of a specific shared guild template by its ID."""
        logger.info(f"Fetching details for shared template ID {template_id} requested by user {current_user.id}")
        try:
            # --- Permission Check (Example: Any logged-in user can view shared?) ---
            pass

            # --- Call Service Layer --- 
            template_data: Optional[Dict[str, Any]] = await self.template_service.get_shared_template_details(template_id)

            if not template_data:
                logger.warning(f"Shared template not found for ID {template_id} by service.")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shared guild template not found.")
            
            logger.info(f"Successfully retrieved shared template data for ID {template_id}")
            return template_data

        except HTTPException as http_exc:
            raise http_exc
        except NotImplementedError as nie:
             logger.error(f"Shared template detail fetch service method not implemented for ID {template_id}")
             raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=str(nie))
        except Exception as e:
            logger.error(f"Error fetching shared template details for ID {template_id}: {e}", exc_info=True)
            return self.handle_exception(e)
            
    # --- NEW Method for Copy Shared Template Route (Signature updated) ---
    async def copy_shared_template(
        self,
        guild_id: str, # <<< ADDED guild_id
        copy_request: dict, 
        current_user: AppUserEntity = Depends(get_current_user)
        # Optional: response_model=GuildTemplateResponseSchema
    ):
        """API endpoint to copy a shared template to the current user's saved templates."""
        shared_template_id = copy_request.get('shared_template_id')
        new_name_optional = copy_request.get('new_name') # Optional name from request
        
        if not shared_template_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing 'shared_template_id' in request body.")

        logger.info(f"User {current_user.id} requested copy of shared template ID {shared_template_id}. Optional new name: '{new_name_optional}'")
        try:
            # --- Permission Check (Any logged-in user?) ---
            pass

            # --- Call Service Layer ---
            new_saved_template_info = await self.template_service.copy_shared_template(
                shared_template_id=shared_template_id,
                user_id=current_user.id,
                new_name_optional=new_name_optional
            )

            if not new_saved_template_info:
                logger.error(f"Service failed to copy shared template ID {shared_template_id} for user {current_user.id}")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to copy shared template. Ensure original exists and name is valid.")

            logger.info(f"Successfully copied shared template ID {shared_template_id} for user {current_user.id}. New template info: {new_saved_template_info}")
            # Return None for 201 No Content status (as defined in the route decorator)
            # If you wanted to return the new template data, change the route's status_code 
            # and add response_model=GuildTemplateResponseSchema, then return new_saved_template_info
            return

        except HTTPException as http_exc:
            raise http_exc
        except NotImplementedError as nie:
            logger.error(f"Copy shared template service method not implemented for ID {shared_template_id}")
            raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=str(nie))
        except Exception as e:
            logger.error(f"Error copying shared template ID {shared_template_id} for user {current_user.id}: {e}", exc_info=True)
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
            logger.info(f"User {current_user.id} requesting to save guild {guild_id} structure as template '{template_data.template_name}'")
            
            # Pass guild_id from path to service
            created_template = await self.template_service.create_template_from_guild(
                source_guild_id=guild_id, # Use guild_id from path
                template_name=template_data.template_name,
                template_description=template_data.template_description,
                creator_user_id=current_user.id
            )
            
            # --- Handle Service Failure --- 
            if not created_template:
                 logger.error(f"Service failed to create template '{template_data.template_name}' from guild {guild_id}")
                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create template. Ensure source guild exists and template name '{template_data.template_name}' is unique.")
            
            logger.info(f"Successfully created guild template '{template_data.template_name}' by user {current_user.id}")
            return # Status 201 indicates success

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            logger.error(f"Error creating guild template '{template_data.template_name}' from {guild_id}: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create guild template due to an unexpected error.")

    # --- NEW Method for Activate Route --- 
    async def activate_guild_template(
        self,
        guild_id: str, # <<<--- GET FROM PATH
        template_id: int, # <<<--- GET FROM PATH
        current_user: AppUserEntity = Depends(get_current_user), # From dependency
        db: AsyncSession = Depends(get_web_db_session) # Get DB session
    ):
        """API endpoint to activate a specific guild template *for a specific guild*."""
        logger.info(f"User {current_user.id} requesting activation for template ID: {template_id} *for guild ID: {guild_id}*") # Updated log
        try:
            # --- Call Service Layer (Pass guild_id now) --- 
            await self.template_service.activate_template(
                db=db, 
                template_id=template_id, 
                target_guild_id=guild_id, # <<<--- PASS GUILD ID
                requesting_user=current_user 
            )
            
            # --- Return Success Response --- 
            logger.info(f"Template ID {template_id} activated successfully for guild {guild_id} by user {current_user.id}.")
            return {"message": "Template activated successfully."}

        # --- Map Domain Exceptions to HTTP Exceptions (as per convention) ---
        except TemplateNotFound as e:
            logger.warning(f"Activation failed: Template ID {template_id} not found.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except PermissionDenied as e:
            logger.warning(f"Activation failed for template ID {template_id} on guild {guild_id}: User {current_user.id} lacks permissions. Details: {str(e)}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        # --- ADD InvalidOperation for missing GuildConfig --- 
        except InvalidOperation as e:
            logger.error(f"Activation failed for template {template_id} on guild {guild_id}: {e}", exc_info=True)
            # Return 400 Bad Request or 500? 400 seems appropriate if config is missing/invalid.
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error activating template ID {template_id} for guild {guild_id}: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal error occurred during template activation.")

    # --- Method Definition for Structure Update (Signature updated) --- 
    async def update_guild_template_structure(
        self,
        guild_id: str, # <<< ADDED guild_id
        template_id: int,
        payload: GuildStructureUpdatePayload,
        current_user: AppUserEntity = Depends(get_current_user),
        db: AsyncSession = Depends(get_web_db_session)
    ) -> GuildTemplateResponseSchema:
        """Updates the structure (categories and channels) of a specific guild template."""
        # 1. Authorization Check (Ensure user can edit this template)
        try:
            can_edit = await self.template_service.check_user_can_edit_template(
                db=db, # Pass db session
                user_id=current_user.id,
                template_id=template_id
            )
            if not can_edit:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to edit this template."
                )
        except ValueError as e: # Handle if template not found during permission check
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

        # 2. Call the service layer to perform the update
        try:
            # Service now returns a dictionary
            service_result = await self.template_service.update_template_structure(
                db=db,
                template_id=template_id,
                structure_payload=payload,
                requesting_user=current_user
            )
            
            # Extract data from the service result
            template_entity = service_result["template_entity"]
            delete_unmanaged_flag = service_result["delete_unmanaged"]

            # --- Manually Construct the Response Dictionary --- 
            logger.debug(f"Manually constructing response dictionary for template {template_entity.id}")
            response_dict = {
                "guild_id": template_entity.guild_id,
                "template_id": template_entity.id,
                "template_name": template_entity.template_name,
                # Format created_at as string
                "created_at": template_entity.created_at.isoformat() if template_entity.created_at else None, 
                # Determine initial snapshot based on creator_user_id being None
                "is_initial_snapshot": template_entity.creator_user_id is None,
                # Add missing fields
                "creator_user_id": template_entity.creator_user_id,
                "is_shared": template_entity.is_shared,
                "template_delete_unmanaged": delete_unmanaged_flag,
                "categories": [],
                "channels": []
            }

            # Populate categories (using schema logic manually)
            for cat_entity in template_entity.categories:
                cat_dict = {
                    # Use clear key name based on updated schema
                    "category_id": cat_entity.id, 
                    "template_id": template_entity.id, # Template ID this category belongs to
                    "category_name": cat_entity.category_name, 
                    "position": cat_entity.position,
                    "permissions": []
                }
                for perm_entity in cat_entity.permissions:
                    cat_dict["permissions"].append({
                        # Use clear key name based on updated schema
                        "permission_id": perm_entity.id,
                        "role_name": perm_entity.role_name,
                        "allow": perm_entity.allow_permissions_bitfield if perm_entity.allow_permissions_bitfield is not None else 0,
                        "deny": perm_entity.deny_permissions_bitfield if perm_entity.deny_permissions_bitfield is not None else 0
                    })
                response_dict["categories"].append(cat_dict)

            # Populate channels (using schema logic manually)
            for chan_entity in template_entity.channels:
                chan_dict = {
                    # Use clear key name based on updated schema
                    "channel_id": chan_entity.id, 
                    "template_id": template_entity.id, # Template ID this channel belongs to
                    "channel_name": chan_entity.channel_name,
                    "type": chan_entity.channel_type,
                    "position": chan_entity.position,
                    "topic": chan_entity.topic,
                    "is_nsfw": chan_entity.is_nsfw,
                    "slowmode_delay": chan_entity.slowmode_delay,
                    "parent_category_template_id": chan_entity.parent_category_template_id,
                    "permissions": []
                }
                for perm_entity in chan_entity.permissions:
                    chan_dict["permissions"].append({
                        # Use clear key name based on updated schema
                        "permission_id": perm_entity.id,
                        "role_name": perm_entity.role_name,
                        "allow": perm_entity.allow_permissions_bitfield if perm_entity.allow_permissions_bitfield is not None else 0,
                        "deny": perm_entity.deny_permissions_bitfield if perm_entity.deny_permissions_bitfield is not None else 0
                    })
                response_dict["channels"].append(chan_dict)

            # Return the manually constructed dictionary.
            # FastAPI will validate this against the GuildTemplateResponseSchema.
            return response_dict
            # --- END Manual Construction --- 

        except ValueError as e:
            # Handle specific errors from the service layer (e.g., template not found)
            logger.warning(f"Update structure failed for template {template_id}: {e}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except NotImplementedError:
             logger.error(f"Template structure update service method not implemented for ID {template_id}")
             raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Template structure update not implemented.")
        except Exception as e:
            # Generic error handling
            logger.error(f"Error updating template structure for ID {template_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while updating the template structure."
            )

    # --- NEW Method for Creating Template from Structure (Signature updated) --- 
    async def create_template_from_structure(
        self,
        guild_id: str, # <<< ADDED guild_id
        payload: GuildStructureTemplateCreateFromStructure,
        current_user: AppUserEntity = Depends(get_current_user),
        db: AsyncSession = Depends(get_web_db_session)
    ) -> GuildStructureTemplateInfo:
        """Creates a new guild template based on the provided structure data."""
        logger.info(f"User {current_user.id} attempting to create new template '{payload.new_template_name}' from structure.")

        try:
            # Call the new service method
            new_template_entity = await self.template_service.create_template_from_structure(
                db=db,
                creator_user_id=current_user.id,
                payload=payload
            )
            
            # Convert entity to response schema (assuming service returns entity)
            # Manual mapping or use Pydantic's from_orm if service returns the full entity
            # For now, construct manually or assume service returns a dict matching the schema
            # Let's assume service returns an object with needed fields
            response_data = GuildStructureTemplateInfo(
                template_id=new_template_entity.id,
                template_name=new_template_entity.template_name,
                description=new_template_entity.template_description,
                is_shared=new_template_entity.is_shared,
                is_initial_snapshot=False, # Newly created is never initial snapshot
                creator_user_id=new_template_entity.creator_user_id,
                created_at=new_template_entity.created_at
            )

            logger.info(f"Successfully created template '{response_data.template_name}' (ID: {response_data.template_id}) from structure.")
            return response_data

        except ValueError as e:
            # Handle potential errors like invalid structure or duplicate name from service
            logger.warning(f"Failed to create template from structure: {e}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except NotImplementedError:
             logger.error(f"Create template from structure service method not implemented.")
             raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Creating template from structure not implemented.")
        except Exception as e:
            logger.error(f"Error creating template from structure: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred while creating the template."
            )

    # --- NEW Method for Settings Update Route ---
    async def update_template_settings(
        self,
        guild_id: str,
        settings_update: GuildTemplateSettingsUpdate,
        current_user: AppUserEntity = Depends(get_current_user),
        db: AsyncSession = Depends(get_web_db_session)
    ):
        """API endpoint to update guild-specific template application settings."""
        logger.info(f"User {current_user.id} updating template settings for guild {guild_id}: {settings_update.dict()}")
        try:
            # Basic permission check (e.g., only owner or specific admin role)
            # TODO: Refine permission check logic
            if not current_user.is_owner:
                 logger.warning(f"Permission denied: User {current_user.id} attempted to update template settings for guild {guild_id}.")
                 raise PermissionDenied("Insufficient permissions to update template settings.")

            # Call the service layer method (assuming it exists)
            success = await self.template_service.update_template_settings(
                db=db,
                guild_id=guild_id,
                delete_unmanaged=settings_update.delete_unmanaged,
                requesting_user=current_user
            )
            
            if not success:
                # This might indicate the GuildConfig wasn't found
                logger.warning(f"Template settings update failed for guild {guild_id} (potentially config not found).")
                raise ConfigurationNotFound(f"Configuration for guild {guild_id} not found.")

            logger.info(f"Successfully updated template settings for guild {guild_id}.")
            return {"message": "Template settings updated successfully."}

        except PermissionDenied as e:
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        except ConfigurationNotFound as e:
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) 
        except Exception as e:
            logger.error(f"Unexpected error updating template settings for guild {guild_id}: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal error occurred while updating template settings.")
    # ------------------------------------------

    # --- METHOD MODIFIED for Apply Route --- 
    async def apply_guild_template(
        self,
        guild_id: str, # From path parameter
        current_user: AppUserEntity = Depends(get_current_user), # From dependency
        # Add HTTP client dependency if available, otherwise create one
        # http_client: httpx.AsyncClient = Depends(get_http_client) # Example dependency
    ):
        """API endpoint to trigger applying the active template to the Discord guild via Internal API."""
        logger.info(f"User {current_user.id} requesting template application for guild ID: {guild_id}")

        # --- 1. Permission Check (Remains the same) --- 
        if not current_user.is_owner:
             logger.warning(f"Permission denied: User {current_user.id} (not bot owner) attempted to apply template for guild {guild_id}.")
             raise HTTPException(
                 status_code=status.HTTP_403_FORBIDDEN, 
                 detail="You do not have permission to apply templates to this guild." 
             )
        logger.info(f"Permission granted for user {current_user.id} to apply template for guild {guild_id}.")

        # --- 2. Trigger Bot via Internal API --- 
        internal_api_url = f"{INTERNAL_API_BASE_URL}/guilds/{guild_id}/apply_template"
        logger.info(f"Making POST request to internal API: {internal_api_url}")

        try:
            # Use httpx client (instantiate directly for now, ideally inject)
            async with httpx.AsyncClient() as client:
                 response = await client.post(internal_api_url, timeout=10.0) # Add timeout
            
            # Check response status from internal API
            if response.status_code == 202: # 202 Accepted is expected success
                 logger.info(f"Internal API accepted template application trigger for guild {guild_id}.")
                 response_data = response.json()
                 return {"message": response_data.get("message", "Template application trigger accepted by bot.")}
            elif response.status_code == 400:
                 logger.error(f"Internal API returned 400 Bad Request for guild {guild_id}: {response.text}")
                 raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Internal bot error: {response.json().get('message', 'Bad request')}")
            elif response.status_code == 500 or response.status_code == 503:
                 logger.error(f"Internal API returned {response.status_code} for guild {guild_id}: {response.text}")
                 raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Internal bot error: {response.json().get('message', 'Server error')}")
            else:
                 # Handle other unexpected statuses from internal API
                 logger.error(f"Internal API returned unexpected status {response.status_code} for guild {guild_id}: {response.text}")
                 raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Unexpected response from internal bot API (Status: {response.status_code})")

        except httpx.RequestError as exc:
            logger.error(f"HTTP request to internal bot API failed: {exc}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Failed to communicate with the internal bot service.")
        except Exception as e:
            logger.error(f"Unexpected error calling internal API for guild {guild_id}: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred while communicating with the bot.")

    # === NEW Controller Methods for Deleting Elements ===
    async def delete_template_category(
        self,
        guild_id: str, # <<< ADDED guild_id from path
        category_id: int,
        current_user: AppUserEntity = Depends(get_current_user),
        db: AsyncSession = Depends(get_web_db_session)
    ):
        """API endpoint to delete a category from a template."""
        logger.info(f"User {current_user.id} requesting deletion of template category ID: {category_id}")
        try:
            # --- Re-inserted Permission Check ---
            try:
                parent_template_id = await self.template_service.get_parent_template_id_for_element(
                    db=db, element_id=category_id, element_type='category'
                )
                if parent_template_id is None: # Service should ideally raise if not found
                    raise TemplateNotFound("Category or its parent template not found.")

                can_edit = await self.template_service.check_user_can_edit_template(
                    db=db, user_id=current_user.id, template_id=parent_template_id
                )
                if not can_edit:
                    raise PermissionDenied("Permission denied to modify this template.")
                
                logger.info(f"Permission granted for user {current_user.id} to delete category {category_id} (Template ID: {parent_template_id})")

            except (TemplateNotFound, ValueError) as e: # Catch potential service errors
                logger.warning(f"Permission check failed for category {category_id}: {e}")
                logger.warning(f"CONTROLLER INTENTION: Raising 404 - Permission Check Failed for ID: {category_id}")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
            except PermissionDenied as e:
                logger.warning(f"Permission denied for user {current_user.id} on category {category_id}: {e}")
                logger.warning(f"CONTROLLER INTENTION: Raising 403 - Permission Denied for ID: {category_id}")
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
            # --- End Permission Check ---

            # Call the service layer method
            deleted = await self.template_service.delete_template_category(db, category_id)
            
            if not deleted:
                logger.warning(f"Service failed to delete category {category_id} after permission check. Might not exist or DB error.")
                logger.warning(f"CONTROLLER INTENTION: Raising 404 - Service returned False for ID: {category_id}")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found or could not be deleted.")

            logger.info(f"CONTROLLER INTENTION: Returning SUCCESS (implicit 204 No Content) for ID: {category_id}")
            return

        except HTTPException as http_exc:
            raise http_exc
        except NotImplementedError:
            logger.error(f"CONTROLLER INTENTION: Raising 501 - Not Implemented for ID: {category_id}")
            raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Category deletion not implemented.")
        except Exception as e:
            logger.error(f"CONTROLLER INTENTION: Raising 500 - Internal Server Error for ID: {category_id}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal error occurred while deleting the category.")

    async def delete_template_channel(
        self,
        guild_id: str, # <<< ADDED guild_id from path
        channel_id: int,
        current_user: AppUserEntity = Depends(get_current_user),
        db: AsyncSession = Depends(get_web_db_session)
    ):
        """API endpoint to delete a channel from a template."""
        logger.info(f"User {current_user.id} requesting deletion of template channel ID: {channel_id}")
        try:
            # --- Re-inserted Permission Check ---
            try:
                parent_template_id = await self.template_service.get_parent_template_id_for_element(
                    db=db, element_id=channel_id, element_type='channel'
                )
                if parent_template_id is None: # Service should ideally raise if not found
                    raise TemplateNotFound("Channel or its parent template not found.")

                can_edit = await self.template_service.check_user_can_edit_template(
                    db=db, user_id=current_user.id, template_id=parent_template_id
                )
                if not can_edit:
                    raise PermissionDenied("Permission denied to modify this template.")

                logger.info(f"Permission granted for user {current_user.id} to delete channel {channel_id} (Template ID: {parent_template_id})")

            except (TemplateNotFound, ValueError) as e: # Catch potential service errors
                logger.warning(f"Permission check failed for channel {channel_id}: {e}")
                logger.warning(f"CONTROLLER INTENTION: Raising 404 - Permission Check Failed for ID: {channel_id}")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
            except PermissionDenied as e:
                logger.warning(f"Permission denied for user {current_user.id} on channel {channel_id}: {e}")
                logger.warning(f"CONTROLLER INTENTION: Raising 403 - Permission Denied for ID: {channel_id}")
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
            # --- End Permission Check ---
            
            # Call the service layer method
            deleted = await self.template_service.delete_template_channel(db, channel_id)
            
            if not deleted:
                logger.warning(f"Service failed to delete channel {channel_id} after permission check. Might not exist or DB error.")
                logger.warning(f"CONTROLLER INTENTION: Raising 404 - Service returned False for ID: {channel_id}")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found or could not be deleted.")

            logger.info(f"CONTROLLER INTENTION: Returning SUCCESS (implicit 204 No Content) for ID: {channel_id}")
            return

        except HTTPException as http_exc:
            raise http_exc
        except NotImplementedError:
            logger.error(f"CONTROLLER INTENTION: Raising 501 - Not Implemented for ID: {channel_id}")
            raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Channel deletion not implemented.")
        except Exception as e:
            logger.error(f"CONTROLLER INTENTION: Raising 500 - Internal Server Error for ID: {channel_id}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal error occurred while deleting the channel.")

    # --- NEW Method for Metadata Update --- 
    async def update_template_metadata(
        self,
        guild_id: str, # From path
        template_id: int, # From path
        metadata_update: GuildTemplateMetadataUpdateSchema, # From request body
        current_user: AppUserEntity = Depends(get_current_user),
        db: AsyncSession = Depends(get_web_db_session)
    ) -> GuildTemplateResponseSchema:
        """API endpoint to update the metadata (e.g., name) of a guild template."""
        logger.info(f"Metadata update requested for template {template_id} in guild {guild_id} by user {current_user.id}")
        try:
            # Call the service layer to perform the update
            updated_template_data = await self.template_service.update_template_metadata(
                db=db,
                template_id=template_id,
                new_name=metadata_update.name,
                requesting_user=current_user
            )
            
            # Service returns None or raises exception on failure/not found/permission denied
            if not updated_template_data:
                # This case might not be reached if service raises exceptions correctly
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found or update failed.")

            logger.info(f"Successfully updated metadata for template {template_id}")
            # Return the full, updated template data validated by the response model
            return updated_template_data

        except (TemplateNotFound, PermissionDenied) as service_exc:
            # Re-raise specific exceptions from the service as HTTPExceptions
            status_code = status.HTTP_404_NOT_FOUND if isinstance(service_exc, TemplateNotFound) else status.HTTP_403_FORBIDDEN
            logger.warning(f"Service error during metadata update for template {template_id}: {service_exc}")
            raise HTTPException(status_code=status_code, detail=str(service_exc))
        except Exception as e:
            logger.error(f"Unexpected error updating metadata for template {template_id}: {e}", exc_info=True)
            # Use the generic exception handler from BaseController
            return self.handle_exception(e)

# Instantiate the controller for registration
guild_template_controller = GuildTemplateController() 
