from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, Dict, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

from app.web.interfaces.api.rest.v1.base_controller import BaseController
from app.shared.infrastructure.models.auth import AppUserEntity
from app.web.interfaces.api.rest.dependencies.auth_dependencies import get_current_user, get_web_db_session
from app.web.application.services.template.template_service import GuildTemplateService
from app.web.interfaces.api.rest.v1.schemas.guild_template_schemas import (
    GuildTemplateResponseSchema,
    GuildStructureUpdatePayload,
    GuildStructureTemplateCreateFromStructure,
    GuildStructureTemplateInfo
)
from app.shared.domain.exceptions import TemplateNotFound, PermissionDenied, DomainException # Added DomainException
from app.shared.interface.logging.api import get_web_logger

logger = get_web_logger()

class GuildTemplateStructureController(BaseController):
    """Controller for managing the internal structure (categories, channels) of guild templates."""

    def __init__(self):
        # Use the same prefix as other designer controllers
        super().__init__(prefix="/guilds/{guild_id}/template", tags=["Guild Templates (Structure)"])
        self.template_service = GuildTemplateService()
        self._register_routes()

    def _register_routes(self):
        """Register API routes for template structure manipulation."""

        # Update structure from payload
        self.router.put(
            "/{template_id}/structure",
            summary="Update Guild Template Structure",
            description="Updates the categories and channels structure of a specific template.",
            response_model=GuildTemplateResponseSchema,
            status_code=status.HTTP_200_OK,
            dependencies=[Depends(get_current_user)] # Keep dependency for auth check
        )(self.update_guild_template_structure)

        # Create template from structure payload
        self.router.post(
            "/from_structure",
            summary="Create Guild Template from Structure Payload",
            description="Creates a new template based on a provided structure payload.",
            response_model=GuildStructureTemplateInfo,
            status_code=status.HTTP_201_CREATED,
            dependencies=[Depends(get_current_user)] # Keep dependency for auth check
        )(self.create_template_from_structure)

        # Delete a category within a template
        self.router.delete(
            "/categories/{category_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Delete Template Category by DB ID",
            description="Deletes a specific category from a guild template.",
            dependencies=[Depends(get_current_user)] # Keep dependency for auth check
        )(self.delete_template_category)

        # Delete a channel within a template
        self.router.delete(
            "/channels/{channel_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Delete Template Channel by DB ID",
            description="Deletes a specific channel from a guild template.",
            dependencies=[Depends(get_current_user)] # Keep dependency for auth check
        )(self.delete_template_channel)


    # --- Method Implementations --- 

    async def update_guild_template_structure(
        self,
        guild_id: str, # Context guild
        template_id: int,
        payload: GuildStructureUpdatePayload,
        current_user: AppUserEntity = Depends(get_current_user),
        db: AsyncSession = Depends(get_web_db_session)
    ) -> GuildTemplateResponseSchema:
        """Updates the structure (categories and channels) of a specific guild template."""
        try:
            # Service handles authorization check internally
            service_result = await self.template_service.update_template_structure(
                db=db,
                template_id=template_id,
                structure_payload=payload,
                requesting_user=current_user
            )
            logger.info(f"Successfully updated structure for template {template_id}")

            template_entity = service_result["template_entity"]
            delete_unmanaged_flag = service_result["delete_unmanaged"]

            response_dict = {
                "guild_id": template_entity.guild_id,
                "template_id": template_entity.id,
                "template_name": template_entity.template_name,
                "created_at": template_entity.created_at.isoformat() if template_entity.created_at else None,
                "is_initial_snapshot": template_entity.creator_user_id is None,
                "creator_user_id": template_entity.creator_user_id,
                "is_shared": template_entity.is_shared,
                "template_delete_unmanaged": delete_unmanaged_flag,
                "categories": [],
                "channels": []
            }

            for cat_entity in template_entity.categories:
                cat_dict = {
                    "category_id": cat_entity.id,
                    "template_id": template_entity.id,
                    "category_name": cat_entity.category_name,
                    "position": cat_entity.position,
                    "permissions": []
                }
                for perm_entity in cat_entity.permissions:
                    cat_dict["permissions"].append({
                        "permission_id": perm_entity.id,
                        "role_name": perm_entity.role_name,
                        "allow": perm_entity.allow_permissions_bitfield if perm_entity.allow_permissions_bitfield is not None else 0,
                        "deny": perm_entity.deny_permissions_bitfield if perm_entity.deny_permissions_bitfield is not None else 0
                    })
                response_dict["categories"].append(cat_dict)

            for chan_entity in template_entity.channels:
                chan_dict = {
                    "channel_id": chan_entity.id,
                    "template_id": template_entity.id,
                    "channel_name": chan_entity.channel_name,
                    "type": chan_entity.channel_type,
                    "position": chan_entity.position,
                    "topic": chan_entity.topic,
                    "is_nsfw": chan_entity.is_nsfw,
                    "slowmode_delay": chan_entity.slowmode_delay,
                    "is_dashboard_enabled": chan_entity.is_dashboard_enabled,
                    "dashboard_types": chan_entity.dashboard_types,
                    "parent_category_template_id": chan_entity.parent_category_template_id,
                    "permissions": []
                }
                for perm_entity in chan_entity.permissions:
                    chan_dict["permissions"].append({
                        "permission_id": perm_entity.id,
                        "role_name": perm_entity.role_name,
                        "allow": perm_entity.allow_permissions_bitfield if perm_entity.allow_permissions_bitfield is not None else 0,
                        "deny": perm_entity.deny_permissions_bitfield if perm_entity.deny_permissions_bitfield is not None else 0
                    })
                response_dict["channels"].append(chan_dict)

            return response_dict

        except (TemplateNotFound, PermissionDenied, DomainException) as service_exc:
            status_code = status.HTTP_404_NOT_FOUND
            if isinstance(service_exc, PermissionDenied):
                status_code = status.HTTP_403_FORBIDDEN
            elif isinstance(service_exc, DomainException):
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            logger.warning(f"Structure update failed for template {template_id}: {service_exc}")
            raise HTTPException(status_code=status_code, detail=str(service_exc))
        except ValueError as e: # Catch other potential errors like during permission check
             logger.warning(f"Structure update failed for template {template_id} (ValueError): {e}")
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except Exception as e:
            logger.error(f"Error updating template structure for ID {template_id}: {e}", exc_info=True)
            return self.handle_exception(e) # Use BaseController handler

    async def create_template_from_structure(
        self,
        guild_id: str, # Context guild (unused here but part of prefix)
        payload: GuildStructureTemplateCreateFromStructure,
        current_user: AppUserEntity = Depends(get_current_user),
        db: AsyncSession = Depends(get_web_db_session)
    ) -> GuildStructureTemplateInfo:
        """Creates a new guild template based on the provided structure data."""
        logger.info(f"User {current_user.id} attempting to create new template '{payload.new_template_name}' from structure.")
        try:
            # Service handles logic and exceptions
            new_template_entity = await self.template_service.create_template_from_structure(
                db=db,
                creator_user_id=current_user.id,
                payload=payload
            )
            # Validate and return using Pydantic model
            response_data = GuildStructureTemplateInfo.model_validate(new_template_entity, from_attributes=True)
            logger.info(f"Successfully created template '{response_data.template_name}' (ID: {response_data.template_id}) from structure.")
            return response_data
        except ValueError as e: # Duplicate name etc.
            logger.warning(f"Failed to create template from structure: {e}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            logger.error(f"Error creating template from structure: {e}", exc_info=True)
            return self.handle_exception(e) # Use BaseController handler

    async def delete_template_category(
        self,
        guild_id: str, # Context guild (unused here but part of prefix)
        category_id: int,
        current_user: AppUserEntity = Depends(get_current_user),
        db: AsyncSession = Depends(get_web_db_session)
    ):
        """API endpoint to delete a specific category from a guild template."""
        logger.info(f"Attempting to delete template category {category_id} by user {current_user.id}")
        try:
            # Service handles permission check
            await self.template_service.delete_category(
                db=db,
                category_id=category_id,
                requesting_user_id=current_user.id,
                is_owner=current_user.is_owner
            )
            logger.info(f"Successfully deleted category {category_id}")
            return # Return None for 204
        except TemplateNotFound as e:
             logger.warning(f"Delete category failed: {e}")
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except PermissionDenied as e:
             logger.warning(f"Permission denied for category deletion: {e}")
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        except Exception as e:
             logger.error(f"Error deleting template category {category_id}: {e}", exc_info=True)
             return self.handle_exception(e) # Use BaseController handler

    async def delete_template_channel(
        self,
        guild_id: str, # Context guild (unused here but part of prefix)
        channel_id: int,
        current_user: AppUserEntity = Depends(get_current_user),
        db: AsyncSession = Depends(get_web_db_session)
    ):
        """API endpoint to delete a specific channel from a guild template."""
        logger.info(f"Attempting to delete template channel {channel_id} by user {current_user.id}")
        try:
            # Service handles permission check
            await self.template_service.delete_template_channel(
                db=db,
                channel_id=channel_id,
                requesting_user_id=current_user.id,
                is_owner=current_user.is_owner
            )
            logger.info(f"Successfully deleted channel {channel_id}")
            return # Return None for 204
        except TemplateNotFound as e:
             logger.warning(f"Delete channel failed: {e}")
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except PermissionDenied as e:
             logger.warning(f"Permission denied for channel deletion: {e}")
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        except Exception as e:
             logger.error(f"Error deleting template channel {channel_id}: {e}", exc_info=True)
             return self.handle_exception(e) # Use BaseController handler

# Instantiate the controller for registration
structure_controller = GuildTemplateStructureController()
