"""
Service responsible for general template management actions (activation, deletion, settings, metadata).
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update, delete
from datetime import datetime

from app.shared.infrastructure.database.session.context import session_context
from app.shared.interfaces.logging.api import get_web_logger
# Import Template Repositories & Entities
from app.shared.infrastructure.repositories.guild_templates import (
    GuildTemplateRepositoryImpl,
    GuildTemplateCategoryRepositoryImpl,
    GuildTemplateChannelRepositoryImpl
)
from app.shared.infrastructure.models.guild_templates import (
    GuildTemplateEntity,
    GuildTemplateCategoryEntity,
    GuildTemplateChannelEntity
)
# Import Schemas (if needed by methods)
# from app.web.interfaces.api.rest.v1.schemas.guild_template_schemas import ...
# Import Exceptions
from app.shared.domain.exceptions import TemplateNotFound, PermissionDenied, InvalidOperation, DomainException, ConfigurationNotFound
# Import User Entity & Repo
from app.shared.infrastructure.models.auth import AppUserEntity
from app.shared.infrastructure.repositories.auth.user_repository_impl import UserRepositoryImpl
# Import Config Repo & Entity
from app.shared.infrastructure.repositories.discord import GuildConfigRepositoryImpl
from app.shared.infrastructure.models.discord import GuildConfigEntity

logger = get_web_logger()

class TemplateManagementService:
    """Handles general template management: activation, deletion, settings, metadata."""

    def __init__(self):
        """Initialize TemplateManagementService."""
        logger.info("TemplateManagementService initialized.")
        # Repositories are typically instantiated per request/session

    async def delete_template(self, template_id: int) -> bool:
        """Deletes a guild structure template by its database ID."""
        logger.info(f"Attempting to delete template with ID: {template_id}")
        try:
            async with session_context() as session:
                template_repo = GuildTemplateRepositoryImpl(session)
                template_to_delete = await template_repo.get_by_id(template_id)

                if not template_to_delete:
                    logger.warning(f"Template ID {template_id} not found for deletion.")
                    return False # Indicate not found

                # Cannot delete initial snapshot
                if template_to_delete.creator_user_id is None:
                     logger.warning(f"Attempt to delete initial snapshot template ID {template_id} denied.")
                     # Consider raising PermissionDenied or InvalidOperation
                     raise InvalidOperation("Cannot delete the initial guild snapshot template.")

                await template_repo.delete(template_to_delete)
                await session.commit()
                logger.info(f"Successfully deleted template ID {template_id}.")
                return True

        except InvalidOperation as io_err:
             logger.error(f"Invalid operation deleting template {template_id}: {io_err}")
             raise io_err # Re-raise specific exceptions
        except Exception as e:
            logger.error(f"Error deleting template ID {template_id}: {e}", exc_info=True)
            # await session.rollback() # Context manager handles rollback
            return False

    async def activate_template(
        self,
        db: AsyncSession,
        template_id: int,
        target_guild_id: str,
        requesting_user: AppUserEntity
    ) -> None:
        """
        Activates a specific template for the target guild.
        Ensures only one template is active per guild by deactivating others.
        Performs permission checks.
        """
        logger.info(f"Attempting to activate template ID {template_id} for guild {target_guild_id} by user {requesting_user.id}")

        template_repo = GuildTemplateRepositoryImpl(db)

        template_to_activate: Optional[GuildTemplateEntity] = await template_repo.get_by_id(template_id)

        if not template_to_activate:
            logger.warning(f"Activate failed: Template ID {template_id} not found.")
            raise TemplateNotFound(template_id=template_id)

        logger.debug(f"Found template '{template_to_activate.template_name}' (ID: {template_id}) for activation.")

        # Permission Check (placeholder, assumes controller did main checks)
        # is_creator = template_to_activate.creator_user_id == requesting_user.id
        # is_bot_owner = requesting_user.is_owner
        # TODO: Add proper guild-level permission check
        # if not (is_creator or is_bot_owner):
        #     logger.warning(f"Permission denied: User {requesting_user.id} tried to activate template {template_id} for guild {target_guild_id}.")
        #     raise PermissionDenied(...)
        # logger.debug(f"Permission granted for user {requesting_user.id} to activate template {template_id} for guild {target_guild_id}.")

        # Deactivate other active templates for the TARGET guild
        logger.info(f"Deactivating other active templates for guild {target_guild_id} (if any).")
        deactivate_stmt = (
            update(GuildTemplateEntity)
            .where(
                GuildTemplateEntity.guild_id == target_guild_id,
                GuildTemplateEntity.is_active == True,
                GuildTemplateEntity.id != template_id
            )
            .values(is_active=False)
            .execution_options(synchronize_session="fetch")
        )
        await db.execute(deactivate_stmt)

        # Activate the target template
        logger.debug(f"Activating target template {template_id}")
        template_to_activate.is_active = True
        db.add(template_to_activate) # Add to session for state change

        # Update GuildConfigEntity.active_template_id for the TARGET guild
        logger.debug(f"Updating GuildConfigEntity for guild {target_guild_id} to set active_template_id={template_id}")
        update_config_stmt = (
            update(GuildConfigEntity)
            .where(GuildConfigEntity.guild_id == target_guild_id)
            .values(active_template_id=template_id)
            .execution_options(synchronize_session=False) # Avoid synchronizing here
        )
        config_update_result = await db.execute(update_config_stmt)

        if config_update_result.rowcount == 0:
            # Attempt to create config if it doesn't exist
            logger.warning(f"GuildConfigEntity for guild {target_guild_id} not found. Attempting to create.")
            try:
                new_config = GuildConfigEntity(guild_id=target_guild_id, active_template_id=template_id)
                db.add(new_config)
                # No need to flush yet, commit will handle it
                logger.info(f"Created new GuildConfigEntity for guild {target_guild_id} with active_template_id={template_id}")
            except Exception as create_exc:
                 logger.error(f"Failed to create GuildConfigEntity for guild {target_guild_id}: {create_exc}", exc_info=True)
                 raise InvalidOperation(f"Could not update or create guild configuration for guild {target_guild_id}. Configuration might be missing or creation failed.")
        else:
            logger.debug(f"Successfully updated GuildConfigEntity.active_template_id for guild {target_guild_id}.")

        # Commit should happen in the controller/calling context after this returns
        logger.info(f"Successfully marked template {template_id} as active and updated/created GuildConfig (pending commit) for guild {target_guild_id}")

    async def check_user_can_edit_template(self, db: AsyncSession, user_id: int, template_id: int) -> bool:
        """Checks if a user has permission to edit a specific template."""
        logger.debug(f"Checking edit permission for user {user_id} on template {template_id}")
        try:
            template_repo = GuildTemplateRepositoryImpl(db)
            template = await template_repo.get_by_id(template_id)

            if not template:
                logger.warning(f"Permission check failed: Template {template_id} not found.")
                raise ValueError(f"Template with ID {template_id} not found.")

            # Allow if user is the creator
            if template.creator_user_id == user_id:
                logger.debug(f"User {user_id} is the creator of template {template_id}. Permission granted.")
                return True

            # Check owner status
            user_repo = UserRepositoryImpl(db)
            user = await user_repo.get_by_id(user_id)
            if user and user.is_owner:
               logger.debug(f"User {user_id} is a bot owner. Permission granted for template {template_id}.")
               return True

            logger.warning(f"Permission denied: User {user_id} is not creator or owner for template {template_id}.")
            return False
        except ValueError as ve:
            raise ve
        except Exception as e:
            logger.error(f"Error checking edit permission for user {user_id} on template {template_id}: {e}", exc_info=True)
            return False

    async def update_template_settings(
        self,
        db: AsyncSession,
        guild_id: str,
        delete_unmanaged: bool,
        requesting_user: AppUserEntity
    ) -> bool:
        """Updates specific template application settings for a guild."""
        logger.info(f"Service attempting to update template_delete_unmanaged to {delete_unmanaged} for guild {guild_id}")
        try:
            # Basic permission check (owner or guild admin? TODO: Add guild admin check)
            if not requesting_user.is_owner:
                 logger.warning(f"Permission denied in service for user {requesting_user.id} updating settings for guild {guild_id}")
                 raise PermissionDenied("User does not have permission to update these settings.")

            config_repo = GuildConfigRepositoryImpl(db)

            success = await config_repo.update_template_delete_unmanaged(
                guild_id=guild_id,
                delete_unmanaged=delete_unmanaged
            )

            if success:
                logger.info(f"Successfully updated template_delete_unmanaged flag for guild {guild_id}")
            else:
                logger.warning(f"GuildConfigRepository failed to update flag for guild {guild_id} (config likely not found). Raising ConfigurationNotFound.")
                raise ConfigurationNotFound(f"Configuration for guild {guild_id} not found.")

            return True

        except (PermissionDenied, ConfigurationNotFound) as e:
             raise e
        except Exception as e:
            logger.error(f"Unexpected error in update_template_settings for guild {guild_id}: {e}", exc_info=True)
            raise DomainException(f"An unexpected error occurred while updating template settings for guild {guild_id}.") from e

    async def delete_template_category(self, db: AsyncSession, category_id: int, requesting_user_id: int, is_owner: bool) -> bool:
        """
        Deletes a specific category from a template database entry after checking permissions.
        Raises TemplateNotFound or PermissionDenied on failure.
        Returns True on success.
        """
        logger.info(f"Service attempting to delete template category ID: {category_id} by user {requesting_user_id}")
        try:
            category_repo = GuildTemplateCategoryRepositoryImpl(db)
            template_repo = GuildTemplateRepositoryImpl(db) # Needed for permission check

            # 1. Find the category
            category_to_delete = await category_repo.get_by_id(category_id)
            if not category_to_delete:
                logger.warning(f"Delete category failed: Category ID {category_id} not found.")
                raise TemplateNotFound(f"Category with ID {category_id} not found.")

            # 2. Find the parent template for permission check
            parent_template_id = category_to_delete.guild_template_id
            if not parent_template_id:
                 logger.error(f"Data integrity issue: Category {category_id} has no parent template ID.")
                 raise DomainException(f"Cannot determine parent template for category {category_id}.")

            parent_template = await template_repo.get_by_id(parent_template_id)
            if not parent_template:
                 logger.error(f"Data integrity issue: Parent template {parent_template_id} for category {category_id} not found.")
                 raise TemplateNotFound(f"Parent template with ID {parent_template_id} not found.")

            # 3. Permission Check
            is_creator = parent_template.creator_user_id == requesting_user_id
            if not is_creator and not is_owner:
                logger.warning(f"Permission denied: User {requesting_user_id} is not owner or creator ({parent_template.creator_user_id}) of template {parent_template_id}.")
                raise PermissionDenied(f"User does not have permission to modify template {parent_template_id}.")

            logger.debug(f"Permission granted for user {requesting_user_id} to delete category {category_id} from template {parent_template_id}.")

            # 4. Delete the category
            await category_repo.delete(category_to_delete)
            # Commit handled by caller (controller)

            logger.info(f"Successfully marked category ID {category_id} for deletion (pending commit).")
            return True

        except (TemplateNotFound, PermissionDenied, DomainException) as specific_exception:
             # Re-raise specific exceptions for the controller to handle
             raise specific_exception
        except Exception as e:
            logger.error(f"Error deleting template category ID {category_id}: {e}", exc_info=True)
            # Rollback handled by caller (controller)
            raise DomainException(f"Failed to delete category {category_id} due to a database error.") from e

    async def delete_template_channel(self, db: AsyncSession, channel_id: int, requesting_user_id: int, is_owner: bool) -> bool:
        """
        Deletes a specific channel from a template database entry after checking permissions.
        Raises TemplateNotFound or PermissionDenied on failure.
        Returns True on success.
        """
        logger.info(f"Service attempting to delete template channel ID: {channel_id} by user {requesting_user_id}")
        try:
            channel_repo = GuildTemplateChannelRepositoryImpl(db)
            template_repo = GuildTemplateRepositoryImpl(db) # Needed for permission check

            # 1. Find the channel
            channel_to_delete = await channel_repo.get_by_id(channel_id)
            if not channel_to_delete:
                logger.warning(f"Delete channel failed: Channel ID {channel_id} not found.")
                raise TemplateNotFound(f"Channel with ID {channel_id} not found.")

            # 2. Find the parent template for permission check
            parent_template_id = channel_to_delete.guild_template_id
            if not parent_template_id:
                 logger.error(f"Data integrity issue: Channel {channel_id} has no parent template ID.")
                 raise DomainException(f"Cannot determine parent template for channel {channel_id}.")

            parent_template = await template_repo.get_by_id(parent_template_id)
            if not parent_template:
                 logger.error(f"Data integrity issue: Parent template {parent_template_id} for channel {channel_id} not found.")
                 raise TemplateNotFound(f"Parent template with ID {parent_template_id} not found.")

            # 3. Permission Check
            is_creator = parent_template.creator_user_id == requesting_user_id
            if not is_creator and not is_owner:
                logger.warning(f"Permission denied: User {requesting_user_id} is not owner or creator ({parent_template.creator_user_id}) of template {parent_template_id}.")
                raise PermissionDenied(f"User does not have permission to modify template {parent_template_id}.")

            logger.debug(f"Permission granted for user {requesting_user_id} to delete channel {channel_id} from template {parent_template_id}.")

            # 4. Delete the channel
            await channel_repo.delete(channel_to_delete)
            # Commit handled by caller (controller)

            logger.info(f"Successfully marked channel ID {channel_id} for deletion (pending commit).")
            return True

        except (TemplateNotFound, PermissionDenied, DomainException) as specific_exception:
             # Re-raise specific exceptions for the controller to handle
             raise specific_exception
        except Exception as e:
            logger.error(f"Error deleting template channel ID {channel_id}: {e}", exc_info=True)
            # Rollback handled by caller (controller)
            raise DomainException(f"Failed to delete channel {channel_id} due to a database error.") from e

    async def update_template_metadata(
        self,
        db: AsyncSession,
        template_id: int,
        requesting_user: AppUserEntity,
        new_name: Optional[str] = None,
        new_description: Optional[str] = None,
        is_shared: Optional[bool] = None
    ) -> int: # Return template_id on success
        """Updates metadata (name, description, is_shared) for a template. Checks ownership. Returns template ID on success."""
        logger.info(f"SERVICE: Attempting metadata update for template {template_id} by user {requesting_user.id}. Update fields: name={new_name}, desc={new_description}, shared={is_shared}")

        result = await db.execute(select(GuildTemplateEntity).where(GuildTemplateEntity.id == template_id))
        template = result.scalar_one_or_none()

        if not template:
            logger.warning(f"SERVICE: Template {template_id} not found for metadata update.")
            raise TemplateNotFound(f"Template with ID {template_id} not found.")

        # Permission Check
        if template.creator_user_id != requesting_user.id and not requesting_user.is_owner:
            logger.warning(f"SERVICE: Permission denied. User {requesting_user.id} cannot update metadata for template {template_id} owned by {template.creator_user_id}.")
            raise PermissionDenied("You do not have permission to modify this template.")

        # Cannot modify initial snapshot metadata (except maybe sharing? TBD)
        if template.creator_user_id is None and (new_name is not None or new_description is not None):
             logger.warning(f"SERVICE: Attempted to modify name/description of initial snapshot template {template_id}.")
             raise PermissionDenied("Cannot modify name or description of the initial guild snapshot.")

        updated = False
        if new_name is not None and template.template_name != new_name:
            template.template_name = new_name
            updated = True
        if new_description is not None and template.template_description != new_description:
            template.template_description = new_description
            updated = True
        if is_shared is not None and template.is_shared != is_shared:
             # Cannot un-share initial snapshot
             if template.creator_user_id is None and not is_shared:
                  logger.warning(f"SERVICE: Attempted to un-share initial snapshot template {template_id}.")
                  raise PermissionDenied("Cannot un-share the initial guild snapshot.")
             template.is_shared = is_shared
             updated = True

        if updated:
            template.updated_at = datetime.utcnow()
            db.add(template)
            # Commit handled by caller
            logger.info(f"SERVICE: Metadata for template {template_id} updated successfully (pending commit). Returning ID.")
        else:
             logger.info(f"SERVICE: No metadata changes detected for template {template_id}. Returning ID.")

        return template.id # Return the ID 