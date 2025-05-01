"""
Service responsible for querying template information.
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_, or_

from app.shared.infrastructure.database.session.context import session_context
from app.shared.interface.logging.api import get_web_logger
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
# Import Exceptions (if needed by copied methods, e.g., for logging?)
from app.shared.domain.exceptions import TemplateNotFound
# Import Config Repo
from app.shared.infrastructure.repositories.discord import GuildConfigRepositoryImpl

logger = get_web_logger()

class TemplateQueryService:
    """Handles logic related to querying template information."""

    def __init__(self):
        """Initialize TemplateQueryService."""
        logger.info("TemplateQueryService initialized.")
        # Repositories are typically instantiated per request/session

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
                guild_config_repo = GuildConfigRepositoryImpl(session)

                # Fetch GuildConfig
                guild_config = await guild_config_repo.get_by_guild_id(guild_id)
                delete_unmanaged_flag = guild_config.template_delete_unmanaged if guild_config else False
                logger.debug(f"GuildConfig found for {guild_id}. template_delete_unmanaged is {delete_unmanaged_flag}")

                # Get categories
                cat_stmt = (
                    select(GuildTemplateCategoryEntity)
                    .where(GuildTemplateCategoryEntity.guild_template_id == template_db_id)
                    .options(selectinload(GuildTemplateCategoryEntity.permissions))
                    .order_by(GuildTemplateCategoryEntity.position)
                )
                cat_result = await session.execute(cat_stmt)
                categories: List[GuildTemplateCategoryEntity] = cat_result.scalars().all()
                logger.debug(f"Found {len(categories)} categories for template {template_db_id}")

                # Get channels
                chan_stmt = (
                    select(GuildTemplateChannelEntity)
                    .where(GuildTemplateChannelEntity.guild_template_id == template_db_id)
                    .options(selectinload(GuildTemplateChannelEntity.permissions))
                    .order_by(GuildTemplateChannelEntity.position)
                )
                chan_result = await session.execute(chan_stmt)
                channels: List[GuildTemplateChannelEntity] = chan_result.scalars().all()
                logger.debug(f"Found {len(channels)} channels for template {template_db_id}")

                # Structure the data using the UPDATED field names expected by the schema
                structured_template = {
                    "guild_id": template.guild_id,
                    "template_id": template.id,
                    "template_name": template.template_name,
                    "created_at": template.created_at.isoformat() if template.created_at else None,
                    "is_shared": template.is_shared,
                    "creator_user_id": template.creator_user_id,
                    "is_active": template.is_active,
                    "template_delete_unmanaged": delete_unmanaged_flag,
                    "categories": [],
                    "channels": []
                }

                for cat in categories:
                    category_data = {
                        "category_id": cat.id,
                        "template_id": cat.guild_template_id,
                        "category_name": cat.category_name,
                        "position": cat.position,
                        "permissions": [] # Add permissions if CategoryResponseSchema requires them
                    }
                    # TODO: Add manual permission construction if schema requires it and ORM mode doesn't handle it
                    structured_template["categories"].append(category_data)

                for chan in channels:
                    channel_data = {
                        "channel_id": chan.id,
                        "template_id": chan.guild_template_id,
                        "parent_category_template_id": chan.parent_category_template_id,
                        "channel_name": chan.channel_name,
                        "type": chan.channel_type, # Use key 'type' as per original schema
                        "position": chan.position,
                        "topic": chan.topic,
                        "is_nsfw": chan.is_nsfw,
                        "slowmode_delay": chan.slowmode_delay,
                        "permissions": [] # Add permissions if ChannelResponseSchema requires them
                    }
                    # TODO: Add manual permission construction if schema requires it and ORM mode doesn't handle it
                    structured_template["channels"].append(channel_data)

                logger.info(f"Successfully fetched and structured template data for guild {guild_id}")
                return structured_template

        except Exception as e:
            logger.error(f"Error fetching template for guild {guild_id}: {e}", exc_info=True)
            return None

    async def get_template_by_id(self, template_id: int) -> Optional[Dict[str, Any]]:
        """Fetches the complete guild template structure from the database using its primary key ID."""
        logger.info(f"Fetching guild template data for template_id: {template_id}")
        try:
            async with session_context() as session:
                template_repo = GuildTemplateRepositoryImpl(session)
                template: Optional[GuildTemplateEntity] = await template_repo.get_by_id(template_id)

                if not template:
                    logger.warning(f"No guild template found for template_id: {template_id}")
                    return None

                template_db_id = template.id
                logger.debug(f"Found template ID {template_db_id}")

                delete_unmanaged_flag = False
                if template.guild_id:
                    guild_config_repo = GuildConfigRepositoryImpl(session)
                    guild_config = await guild_config_repo.get_by_guild_id(template.guild_id)
                    delete_unmanaged_flag = guild_config.template_delete_unmanaged if guild_config else False
                    logger.debug(f"GuildConfig fetched for guild {template.guild_id}. template_delete_unmanaged is {delete_unmanaged_flag}")
                else:
                    logger.debug(f"Template {template_id} is not linked to a specific guild. delete_unmanaged flag defaults to False.")

                cat_repo = GuildTemplateCategoryRepositoryImpl(session)
                chan_repo = GuildTemplateChannelRepositoryImpl(session)

                cat_stmt = (
                    select(GuildTemplateCategoryEntity)
                    .where(GuildTemplateCategoryEntity.guild_template_id == template_db_id)
                    .options(selectinload(GuildTemplateCategoryEntity.permissions))
                    .order_by(GuildTemplateCategoryEntity.position)
                )
                cat_result = await session.execute(cat_stmt)
                categories: List[GuildTemplateCategoryEntity] = cat_result.scalars().all()
                logger.debug(f"Found {len(categories)} categories for template {template_db_id}")

                chan_stmt = (
                    select(GuildTemplateChannelEntity)
                    .where(GuildTemplateChannelEntity.guild_template_id == template_db_id)
                    .options(selectinload(GuildTemplateChannelEntity.permissions))
                    .order_by(GuildTemplateChannelEntity.position)
                )
                chan_result = await session.execute(chan_stmt)
                channels: List[GuildTemplateChannelEntity] = chan_result.scalars().all()
                logger.debug(f"Found {len(channels)} channels for template {template_db_id}")

                # Structure the data using the UPDATED field names expected by the schema
                structured_template = {
                    "template_id": template.id,
                    "creator_user_id": template.creator_user_id,
                    "template_name": template.template_name,
                    "created_at": template.created_at.isoformat() if template.created_at else None,
                    "is_shared": template.is_shared,
                    "is_active": template.is_active,
                    "template_delete_unmanaged": delete_unmanaged_flag,
                    "categories": [],
                    "channels": []
                }

                for cat in categories:
                    category_data = {
                        "category_id": cat.id,
                        "template_id": cat.guild_template_id,
                        "category_name": cat.category_name,
                        "position": cat.position,
                        "permissions": [] # Add permissions if CategoryResponseSchema requires them
                    }
                    # TODO: Add manual permission construction if schema requires it and ORM mode doesn't handle it
                    structured_template["categories"].append(category_data)

                for chan in channels:
                    channel_data = {
                        "channel_id": chan.id,
                        "template_id": chan.guild_template_id,
                        "parent_category_template_id": chan.parent_category_template_id,
                        "channel_name": chan.channel_name,
                        "type": chan.channel_type, # Use key 'type' as per original schema
                        "position": chan.position,
                        "topic": chan.topic,
                        "is_nsfw": chan.is_nsfw,
                        "slowmode_delay": chan.slowmode_delay,
                        "permissions": [] # Add permissions if ChannelResponseSchema requires them
                    }
                    # TODO: Add manual permission construction if schema requires it and ORM mode doesn't handle it
                    structured_template["channels"].append(channel_data)

                logger.info(f"Successfully fetched and structured template data for template {template_id}")
                return structured_template

        except Exception as e:
            logger.error(f"Error fetching template for template_id {template_id}: {e}", exc_info=True)
            return None

    async def list_templates(self, user_id: int, context_guild_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists basic information about saved guild templates visible to the user."""
        logger.info(f"Listing visible guild templates for user_id: {user_id}, context_guild_id: {context_guild_id}")
        templates_info = []
        try:
            async with session_context() as session:
                user_owned_not_shared = and_(
                    GuildTemplateEntity.creator_user_id == user_id,
                    GuildTemplateEntity.is_shared == False
                )

                initial_snapshot_condition = None
                if context_guild_id:
                    initial_snapshot_condition = and_(
                        GuildTemplateEntity.guild_id == context_guild_id,
                        GuildTemplateEntity.creator_user_id.is_(None)
                    )

                filter_conditions = [user_owned_not_shared]
                if initial_snapshot_condition is not None:
                    filter_conditions.append(initial_snapshot_condition)

                final_filter = or_(*filter_conditions)

                query = (
                    select(GuildTemplateEntity)
                    .where(final_filter)
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
                        "is_shared": template.is_shared,
                        "is_active": template.is_active, # Include active status
                        "is_initial_snapshot": template.creator_user_id is None # Derive initial snapshot status
                    })

                logger.info(f"Successfully listed {len(templates_info)} visible templates for user {user_id} (context: {context_guild_id}).")
                return templates_info

        except Exception as e:
            logger.error(f"Error listing visible guild templates for user {user_id} (context: {context_guild_id}): {e}", exc_info=True)
            return []

    async def get_parent_template_id_for_element(
        self,
        db: AsyncSession,
        element_id: int,
        element_type: str # 'category' or 'channel'
    ) -> Optional[int]:
        """Fetches the parent GuildTemplateEntity ID for a given category or channel ID."""
        logger.debug(f"Fetching parent template ID for {element_type} ID: {element_id}")
        try:
            # Note: This method uses the passed 'db' session directly,
            # unlike others using session_context. Consider standardizing.
            entity = None
            if element_type == 'category':
                repo = GuildTemplateCategoryRepositoryImpl(db)
                entity = await repo.get_by_id(element_id)
            elif element_type == 'channel':
                repo = GuildTemplateChannelRepositoryImpl(db)
                entity = await repo.get_by_id(element_id)
            else:
                logger.warning(f"Invalid element_type '{element_type}' provided.")
                return None

            if not entity:
                logger.warning(f"{element_type.capitalize()} ID {element_id} not found.")
                return None

            logger.debug(f"Found parent template ID {entity.guild_template_id} for {element_type} {element_id}")
            return entity.guild_template_id

        except Exception as e:
            logger.error(f"Error fetching parent template ID for {element_type} {element_id}: {e}", exc_info=True)
            return None # Return None on error 