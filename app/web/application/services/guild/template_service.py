from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.shared.infrastructure.database.session.context import session_context
from app.shared.interface.logging.api import get_web_logger
# Import Template Repositories
from app.shared.infrastructure.repositories.guild_templates import (
    GuildTemplateRepositoryImpl,
    GuildTemplateCategoryRepositoryImpl,
    GuildTemplateChannelRepositoryImpl,
    GuildTemplateCategoryPermissionRepositoryImpl,
    GuildTemplateChannelPermissionRepositoryImpl
)
# Import Template Entities (for type hints, optional)
from app.shared.infrastructure.models.guild_templates import (
    GuildTemplateEntity,
    GuildTemplateCategoryEntity,
    GuildTemplateChannelEntity,
    GuildTemplateCategoryPermissionEntity,
    GuildTemplateChannelPermissionEntity
)

logger = get_web_logger()

class GuildTemplateService:
    """Service layer for managing guild structure templates."""

    # No __init__ needed for now, repositories are created per request

    async def get_template_by_guild(self, guild_id: str) -> Optional[Dict[str, Any]]:
        """Fetches the complete guild template structure from the database."""
        logger.info(f"Fetching guild template data for guild_id: {guild_id}")
        try:
            async with session_context() as session:
                # 1. Get the main template record
                template_repo = GuildTemplateRepositoryImpl(session)
                template: Optional[GuildTemplateEntity] = await template_repo.get_by_guild_id(guild_id)

                if not template:
                    logger.warning(f"No guild template found for guild_id: {guild_id}")
                    return None # Indicate template not found
                
                template_db_id = template.id
                logger.debug(f"Found template ID {template_db_id} for guild {guild_id}")

                # Instantiate other repos
                cat_repo = GuildTemplateCategoryRepositoryImpl(session)
                chan_repo = GuildTemplateChannelRepositoryImpl(session)
                cat_perm_repo = GuildTemplateCategoryPermissionRepositoryImpl(session)
                chan_perm_repo = GuildTemplateChannelPermissionRepositoryImpl(session)

                # 2. Get all categories for this template, eager loading permissions
                cat_stmt = (
                    select(GuildTemplateCategoryEntity)
                    .where(GuildTemplateCategoryEntity.guild_template_id == template_db_id)
                    .options(selectinload(GuildTemplateCategoryEntity.permissions))
                    .order_by(GuildTemplateCategoryEntity.position)
                )
                cat_result = await session.execute(cat_stmt)
                categories: List[GuildTemplateCategoryEntity] = cat_result.scalars().all()
                logger.debug(f"Found {len(categories)} categories for template {template_db_id}")

                # 3. Get all channels for this template, eager loading permissions
                chan_stmt = (
                    select(GuildTemplateChannelEntity)
                    .where(GuildTemplateChannelEntity.guild_template_id == template_db_id)
                    .options(selectinload(GuildTemplateChannelEntity.permissions))
                    .order_by(GuildTemplateChannelEntity.position) # Order by position
                )
                chan_result = await session.execute(chan_stmt)
                channels: List[GuildTemplateChannelEntity] = chan_result.scalars().all()
                logger.debug(f"Found {len(channels)} channels for template {template_db_id}")

                # 4. Structure the data for the response
                structured_template = {
                    "guild_id": template.guild_id,
                    "template_id": template.id,
                    "template_name": template.template_name,
                    "created_at": template.created_at.isoformat() if template.created_at else None,
                    "categories": [],
                    "channels": []
                }

                # Process categories and their permissions
                for cat in categories:
                    category_data = {
                        "id": cat.id,
                        "name": cat.category_name,
                        "position": cat.position,
                        "permissions": []
                    }
                    for perm in cat.permissions:
                        category_data["permissions"].append({
                            "id": perm.id,
                            "role_name": perm.role_name,
                            "allow": perm.allow_permissions_bitfield,
                            "deny": perm.deny_permissions_bitfield
                        })
                    structured_template["categories"].append(category_data)

                # Process channels and their permissions
                for chan in channels:
                    channel_data = {
                        "id": chan.id,
                        "name": chan.channel_name,
                        "type": chan.channel_type,
                        "position": chan.position,
                        "topic": chan.topic,
                        "is_nsfw": chan.is_nsfw,
                        "slowmode_delay": chan.slowmode_delay,
                        "parent_category_template_id": chan.parent_category_template_id,
                        "permissions": []
                    }
                    for perm in chan.permissions:
                        channel_data["permissions"].append({
                            "id": perm.id,
                            "role_name": perm.role_name,
                            "allow": perm.allow_permissions_bitfield if perm.allow_permissions_bitfield is not None else 0,
                            "deny": perm.deny_permissions_bitfield if perm.deny_permissions_bitfield is not None else 0
                        })
                    structured_template["channels"].append(channel_data)
                
                logger.info(f"Successfully fetched and structured template data for guild {guild_id}")
                return structured_template

        except Exception as e:
            logger.error(f"Error fetching template for guild {guild_id}: {e}", exc_info=True)
            # Depending on desired behavior, could return None or raise an exception
            # Returning None for now, controller can handle the 404/500 response.
            return None

    async def get_template_by_id(self, template_id: int) -> Optional[Dict[str, Any]]:
        """Fetches the complete guild template structure from the database using its primary key ID."""
        logger.info(f"Fetching guild template data for template_id: {template_id}")
        try:
            async with session_context() as session:
                # 1. Get the main template record by its primary key
                template_repo = GuildTemplateRepositoryImpl(session)
                template: Optional[GuildTemplateEntity] = await template_repo.get_by_id(template_id)

                if not template:
                    logger.warning(f"No guild template found for template_id: {template_id}")
                    return None # Indicate template not found

                template_db_id = template.id
                logger.debug(f"Found template ID {template_db_id}")

                # Instantiate other repos
                cat_repo = GuildTemplateCategoryRepositoryImpl(session)
                chan_repo = GuildTemplateChannelRepositoryImpl(session)
                # cat_perm_repo = GuildTemplateCategoryPermissionRepositoryImpl(session) # Not directly used
                # chan_perm_repo = GuildTemplateChannelPermissionRepositoryImpl(session) # Not directly used

                # 2. Get all categories for this template, eager loading permissions
                cat_stmt = (
                    select(GuildTemplateCategoryEntity)
                    .where(GuildTemplateCategoryEntity.guild_template_id == template_db_id)
                    .options(selectinload(GuildTemplateCategoryEntity.permissions))
                    .order_by(GuildTemplateCategoryEntity.position)
                )
                cat_result = await session.execute(cat_stmt)
                categories: List[GuildTemplateCategoryEntity] = cat_result.scalars().all()
                logger.debug(f"Found {len(categories)} categories for template {template_db_id}")

                # 3. Get all channels for this template, eager loading permissions
                chan_stmt = (
                    select(GuildTemplateChannelEntity)
                    .where(GuildTemplateChannelEntity.guild_template_id == template_db_id)
                    .options(selectinload(GuildTemplateChannelEntity.permissions))
                    .order_by(GuildTemplateChannelEntity.position) # Order by position
                )
                chan_result = await session.execute(chan_stmt)
                channels: List[GuildTemplateChannelEntity] = chan_result.scalars().all()
                logger.debug(f"Found {len(channels)} channels for template {template_db_id}")

                # 4. Structure the data for the response
                structured_template = {
                    "guild_id": template.guild_id, # Still include guild_id if relevant
                    "template_id": template.id,
                    "template_name": template.template_name,
                    "created_at": template.created_at.isoformat() if template.created_at else None,
                    "categories": [],
                    "channels": []
                }

                # Process categories and their permissions
                for cat in categories:
                    category_data = {
                        "id": cat.id,
                        "name": cat.category_name,
                        "position": cat.position,
                        "permissions": []
                    }
                    for perm in cat.permissions:
                        category_data["permissions"].append({
                            "id": perm.id,
                            "role_name": perm.role_name,
                            "allow": perm.allow_permissions_bitfield,
                            "deny": perm.deny_permissions_bitfield
                        })
                    structured_template["categories"].append(category_data)

                # Process channels and their permissions
                for chan in channels:
                    channel_data = {
                        "id": chan.id,
                        "name": chan.channel_name,
                        "type": chan.channel_type,
                        "position": chan.position,
                        "topic": chan.topic,
                        "is_nsfw": chan.is_nsfw,
                        "slowmode_delay": chan.slowmode_delay,
                        "parent_category_template_id": chan.parent_category_template_id,
                        "permissions": []
                    }
                    for perm in chan.permissions:
                        channel_data["permissions"].append({
                            "id": perm.id,
                            "role_name": perm.role_name,
                            "allow": perm.allow_permissions_bitfield if perm.allow_permissions_bitfield is not None else 0,
                            "deny": perm.deny_permissions_bitfield if perm.deny_permissions_bitfield is not None else 0
                        })
                    structured_template["channels"].append(channel_data)

                logger.info(f"Successfully fetched and structured template data for template {template_id}")
                return structured_template

        except Exception as e:
            logger.error(f"Error fetching template for template_id {template_id}: {e}", exc_info=True)
            # Returning None for now, controller can handle the 404/500 response.
            return None

    async def list_templates(self, user_id: int, context_guild_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists basic information about saved guild templates visible to the user.
        
        Fetches:
        1. Templates created by the user.
        2. Templates marked as shared.
        3. The initial snapshot (creator_user_id is NULL) for the specified context_guild_id (if provided).

        Args:
            user_id: The ID of the user requesting the templates.
            context_guild_id: The ID of the guild currently being viewed/designed, to include its initial snapshot.

        Returns:
            A list of dictionaries, each containing basic template info.
        """
        logger.info(f"Listing visible guild templates for user_id: {user_id}, context_guild_id: {context_guild_id}")
        templates_info = []
        try:
            async with session_context() as session:
                
                # Build the base query parts
                user_owned_filter = (GuildTemplateEntity.creator_user_id == user_id)
                shared_filter = (GuildTemplateEntity.is_shared == True)
                
                # Filter for the specific initial snapshot of the context guild
                initial_snapshot_filter = None
                if context_guild_id:
                    initial_snapshot_filter = (
                        (GuildTemplateEntity.guild_id == context_guild_id) & 
                        (GuildTemplateEntity.creator_user_id.is_(None)) # Check for NULL explicitly
                    )
                
                # Combine filters with OR
                combined_filter = user_owned_filter | shared_filter
                if initial_snapshot_filter is not None:
                    combined_filter = combined_filter | initial_snapshot_filter

                query = (
                    select(GuildTemplateEntity)
                    .where(combined_filter)
                    .order_by(GuildTemplateEntity.created_at.desc())
                )

                result = await session.execute(query)
                visible_templates: List[GuildTemplateEntity] = result.scalars().all()

                for template in visible_templates:
                    templates_info.append({
                        "template_id": template.id,
                        "template_name": template.template_name,
                        "created_at": template.created_at.isoformat() if template.created_at else None,
                        "guild_id": template.guild_id,
                        "creator_user_id": template.creator_user_id,
                        "is_shared": template.is_shared 
                    })
                
                logger.info(f"Successfully listed {len(templates_info)} visible templates for user {user_id} (context: {context_guild_id}).")
                return templates_info
                
        except Exception as e:
            logger.error(f"Error listing visible guild templates for user {user_id} (context: {context_guild_id}): {e}", exc_info=True)
            return []

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
                
                # Assuming the repository handles cascading deletes or we handle relations here
                await template_repo.delete(template_to_delete)
                await session.commit() # Commit the transaction
                logger.info(f"Successfully deleted template ID {template_id}.")
                return True

        except Exception as e:
            logger.error(f"Error deleting template ID {template_id}: {e}", exc_info=True)
            # Raise or return False? Returning False for now.
            # Consider specific exception types if repo raises them (e.g., IntegrityError)
            return False

# Instantiate the service if needed globally (e.g., for factory)
# Or instantiate it where needed
# guild_template_service = GuildTemplateService() 
