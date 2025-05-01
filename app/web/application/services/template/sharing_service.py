"""
Service responsible for template sharing and copying, based on OLD.py logic.
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.shared.infrastructure.database.session.context import session_context
from app.shared.interface.logging.api import get_web_logger
# Import Template Repositories & Entities (copied from OLD.py imports)
from app.shared.infrastructure.repositories.guild_templates import (
    GuildTemplateRepositoryImpl,
    GuildTemplateCategoryRepositoryImpl,
    GuildTemplateChannelRepositoryImpl,
    GuildTemplateCategoryPermissionRepositoryImpl,
    GuildTemplateChannelPermissionRepositoryImpl
)
from app.shared.infrastructure.models.guild_templates import (
    GuildTemplateEntity,
    GuildTemplateCategoryEntity,
    GuildTemplateChannelEntity,
    GuildTemplateCategoryPermissionEntity,
    GuildTemplateChannelPermissionEntity
)
# Import Exceptions (copied from OLD.py imports)
from app.shared.domain.exceptions import TemplateNotFound, PermissionDenied, InvalidOperation, DomainException, ConfigurationNotFound
# Import User Repo/Entity (copied from OLD.py imports)
from app.shared.infrastructure.repositories.auth.user_repository_impl import UserRepositoryImpl
from app.shared.infrastructure.models.auth import AppUserEntity

logger = get_web_logger()

class TemplateSharingService:
    """Handles logic related to sharing and copying templates, mirroring OLD.py."""

    def __init__(self):
        """Initialize TemplateSharingService."""
        logger.info("TemplateSharingService initialized.")

    async def list_shared_templates(self) -> List[Dict[str, Any]]:
        """Lists basic information about publicly shared guild templates. (Copied from OLD.py)"""
        logger.info(f"Listing shared guild templates requested.")
        templates_info = []
        try:
            async with session_context() as session:
                template_repo = GuildTemplateRepositoryImpl(session)
                # Use the repo method as defined in OLD.py context
                shared_templates: List[GuildTemplateEntity] = await template_repo.get_shared_templates()

                for template in shared_templates:
                    templates_info.append({
                        "template_id": template.id,
                        "template_name": template.template_name,
                        "creator_user_id": template.creator_user_id,
                        "created_at": template.created_at.isoformat() if template.created_at else None,
                        "is_shared": template.is_shared
                        # Description was not included in OLD.py's list method
                    })
            logger.info(f"Found {len(templates_info)} shared templates.")
            return templates_info
        except NotImplementedError:
             logger.error("Repository method 'get_shared_templates' not implemented.")
             raise # Re-raise so controller can return 501 (behavior from OLD.py)
        except Exception as e:
            logger.error(f"Error listing shared templates: {e}", exc_info=True)
            raise # Re-raise for controller to handle (behavior from OLD.py)

    async def get_shared_template_details(self, template_id: int) -> Optional[Dict[str, Any]]:
        """Fetches the full details of a specific shared guild template by ID. (Copied from OLD.py)"""
        logger.info(f"Fetching details for shared template_id: {template_id}")
        try:
            async with session_context() as session:
                template_repo = GuildTemplateRepositoryImpl(session)
                template: Optional[GuildTemplateEntity] = await template_repo.get_by_id(template_id)

                if not template:
                    logger.warning(f"No template found for template_id: {template_id}")
                    return None # Behavior from OLD.py
                
                # OLD.py had a TODO for checking is_shared here, but didn't implement it.
                # We follow OLD.py and do NOT check is_shared here.
                # if not template.is_shared:
                #    logger.warning(f"Template {template_id} exists but is not marked as shared.")
                #    return None 

                template_db_id = template.id
                logger.debug(f"Found shared template ID {template_db_id}")

                cat_repo = GuildTemplateCategoryRepositoryImpl(session)
                chan_repo = GuildTemplateChannelRepositoryImpl(session)

                cat_stmt = (
                    select(GuildTemplateCategoryEntity)
                    .where(GuildTemplateCategoryEntity.guild_template_id == template_db_id)
                    .options(selectinload(GuildTemplateCategoryEntity.permissions)) # OLD.py loaded perms
                    .order_by(GuildTemplateCategoryEntity.position)
                )
                cat_result = await session.execute(cat_stmt)
                categories: List[GuildTemplateCategoryEntity] = cat_result.scalars().all()

                chan_stmt = (
                    select(GuildTemplateChannelEntity)
                    .where(GuildTemplateChannelEntity.guild_template_id == template_db_id)
                    .options(selectinload(GuildTemplateChannelEntity.permissions)) # OLD.py loaded perms
                    .order_by(GuildTemplateChannelEntity.position)
                )
                chan_result = await session.execute(chan_stmt)
                channels: List[GuildTemplateChannelEntity] = chan_result.scalars().all()

                structured_template = {
                    "guild_id": template.guild_id,
                    "template_id": template.id,
                    "template_name": template.template_name,
                    "created_at": template.created_at.isoformat() if template.created_at else None,
                    "is_shared": template.is_shared, # Include is_shared status
                    "creator_user_id": template.creator_user_id, # Include creator
                    # OLD.py did not explicitly add description here, but added comment
                    # "description": template.template_description,
                    "categories": [],
                    "channels": []
                }
                
                for cat in categories:
                    category_data = {
                        "id": cat.id,
                        "name": cat.category_name, # Use consistent naming as in OLD.py structure
                        "position": cat.position,
                        "permissions": [] # OLD.py structured perms this way
                    }
                    # OLD.py iterated through loaded permissions
                    for perm in cat.permissions:
                         category_data["permissions"].append({
                            "id": perm.id,
                            "role_name": perm.role_name,
                            "allow": perm.allow_permissions_bitfield if perm.allow_permissions_bitfield is not None else 0,
                            "deny": perm.deny_permissions_bitfield if perm.deny_permissions_bitfield is not None else 0
                        })
                    structured_template["categories"].append(category_data)
                
                for chan in channels:
                    channel_data = {
                        "id": chan.id,
                        "name": chan.channel_name, # Use consistent naming as in OLD.py structure
                        "type": chan.channel_type,
                        "position": chan.position,
                        "topic": chan.topic,
                        "is_nsfw": chan.is_nsfw,
                        "slowmode_delay": chan.slowmode_delay,
                        "parent_category_template_id": chan.parent_category_template_id,
                        "permissions": [] # OLD.py structured perms this way
                    }
                    # OLD.py iterated through loaded permissions
                    for perm in chan.permissions:
                         channel_data["permissions"].append({
                            "id": perm.id,
                            "role_name": perm.role_name,
                            "allow": perm.allow_permissions_bitfield if perm.allow_permissions_bitfield is not None else 0,
                            "deny": perm.deny_permissions_bitfield if perm.deny_permissions_bitfield is not None else 0
                        })
                    structured_template["channels"].append(channel_data)
                
                logger.info(f"Successfully fetched and structured shared template {template_id}")
                return structured_template
        except Exception as e:
            logger.error(f"Error fetching shared template details for template_id {template_id}: {e}", exc_info=True)
            return None # Return None on error, as in OLD.py

    async def copy_shared_template(
        self,
        shared_template_id: int,
        user_id: int,
        new_name_optional: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Copies a shared template structure to create a new saved template. (Copied from OLD.py)"""
        logger.info(f"Attempting to copy shared template {shared_template_id} for user {user_id}. New name: '{new_name_optional}'")
        try:
            async with session_context() as session:
                template_repo = GuildTemplateRepositoryImpl(session)
                cat_repo = GuildTemplateCategoryRepositoryImpl(session)
                chan_repo = GuildTemplateChannelRepositoryImpl(session)
                cat_perm_repo = GuildTemplateCategoryPermissionRepositoryImpl(session)
                chan_perm_repo = GuildTemplateChannelPermissionRepositoryImpl(session)

                original_template = await template_repo.get_by_id(shared_template_id)
                if not original_template:
                    logger.error(f"Shared template {shared_template_id} not found for copying.")
                    return None # Behavior from OLD.py
                
                # OLD.py had a TODO for checking is_shared but didn't implement it.
                # if not original_template.is_shared:
                #     logger.error(f"Template {shared_template_id} is not shared and cannot be copied.")
                #     return None
                
                original_categories = await cat_repo.get_by_template_id(shared_template_id)
                original_channels = await chan_repo.get_by_template_id(shared_template_id)

                new_template_name = new_name_optional if new_name_optional else f"Copy of {original_template.template_name}"
                
                # OLD.py did not check for duplicate name on copy
                # existing_by_name = await template_repo.get_by_name_and_creator(new_template_name, user_id)
                # if existing_by_name:
                #     raise ValueError(f"You already have a template named '{new_template_name}'.")

                new_template = await template_repo.create(
                    creator_user_id=user_id,
                    template_name=new_template_name,
                    template_description=original_template.template_description,
                    guild_id=None,
                    is_shared=False, # New copy is private
                )
                if not new_template:
                    logger.error("Failed to create new template record in database during copy.")
                    return None # Behavior from OLD.py
                
                new_template_id = new_template.id
                logger.info(f"Created new template record (ID: {new_template_id}) for copy.")

                category_id_map = {}
                for original_cat in original_categories:
                    new_cat = await cat_repo.create(
                        guild_template_id=new_template_id,
                        category_name=original_cat.category_name,
                        position=original_cat.position
                    )
                    if not new_cat:
                         logger.error(f"Failed to copy category '{original_cat.category_name}' (original ID {original_cat.id}) to new template {new_template_id}.")
                         # OLD.py continued on error here
                         continue 
                    
                    category_id_map[original_cat.id] = new_cat.id
                    
                    original_cat_perms = await cat_perm_repo.get_by_category_template_id(original_cat.id)
                    for perm in original_cat_perms:
                        await cat_perm_repo.create(
                             category_template_id=new_cat.id,
                             role_name=perm.role_name,
                             allow_permissions_bitfield=perm.allow_permissions_bitfield,
                             deny_permissions_bitfield=perm.deny_permissions_bitfield
                         )
                    # OLD.py flushed permissions inside category loop
                    await session.flush() 

                for original_chan in original_channels:
                    new_parent_category_id = category_id_map.get(original_chan.parent_category_template_id)
                    if original_chan.parent_category_template_id and not new_parent_category_id:
                        logger.warning(f"Could not find new parent category ID for original parent {original_chan.parent_category_template_id} when copying channel '{original_chan.channel_name}'. Setting parent to None.")

                    new_chan = await chan_repo.create(
                        guild_template_id=new_template_id,
                        parent_category_template_id=new_parent_category_id,
                        channel_name=original_chan.channel_name,
                        channel_type=original_chan.channel_type,
                        position=original_chan.position,
                        topic=original_chan.topic,
                        is_nsfw=original_chan.is_nsfw,
                        slowmode_delay=original_chan.slowmode_delay
                    )
                    if not new_chan:
                         logger.error(f"Failed to copy channel '{original_chan.channel_name}' (original ID {original_chan.id}) to new template {new_template_id}.")
                         # OLD.py continued on error here
                         continue
                    
                    original_chan_perms = await chan_perm_repo.get_by_channel_template_id(original_chan.id)
                    for perm in original_chan_perms:
                         await chan_perm_repo.create(
                             channel_template_id=new_chan.id,
                             role_name=perm.role_name,
                             allow_permissions_bitfield=perm.allow_permissions_bitfield,
                             deny_permissions_bitfield=perm.deny_permissions_bitfield
                         )
                    # OLD.py flushed permissions inside channel loop
                    await session.flush()
                         
                # OLD.py did not explicitly commit here, relied on context manager
                # await session.commit() 
                logger.info(f"Successfully copied structure from shared template {shared_template_id} to new template {new_template_id} for user {user_id}.")
                
                # Return structure from OLD.py
                return { "status": "success", "new_template_id": new_template_id, "new_template_name": new_template_name }
        except Exception as e:
            logger.error(f"Error copying shared template {shared_template_id} for user {user_id}: {e}", exc_info=True)
            # await session.rollback() # Handled by context manager
            return None # Return None on error, as in OLD.py

    async def share_template(
        self,
        original_template_id: int,
        new_name: str,
        new_description: Optional[str],
        creator_user_id: int
    ) -> Optional[Dict[str, Any]]:
        """Creates a new template by copying an existing one. (Copied from OLD.py)"""
        logger.info(f"Attempting to share/copy template ID {original_template_id} as '{new_name}' for user {creator_user_id}")

        # OLD.py fetched the template data first using get_template_by_id
        # We need to replicate this temporary dependency or adapt the logic
        # For now, let's adapt and fetch directly
        # original_template_data = await self.get_template_by_id(original_template_id) # OLD.py dependency
        # if not original_template_data:
        #     logger.warning(f"Original template ID {original_template_id} not found for sharing.")
        #     return None

        async with session_context() as session:
            try:
                template_repo = GuildTemplateRepositoryImpl(session)
                cat_repo = GuildTemplateCategoryRepositoryImpl(session)
                chan_repo = GuildTemplateChannelRepositoryImpl(session)
                cat_perm_repo = GuildTemplateCategoryPermissionRepositoryImpl(session)
                chan_perm_repo = GuildTemplateChannelPermissionRepositoryImpl(session)

                # Fetch original template within the session
                original_template = await template_repo.get_by_id(original_template_id)
                if not original_template:
                    logger.warning(f"Original template ID {original_template_id} not found for sharing/copying.")
                    # OLD.py would have returned None earlier based on get_template_by_id result
                    return None 

                # OLD.py did NOT check ownership here.

                # Check if the new name already exists FOR THIS USER (as in OLD.py)
                existing_by_name = await template_repo.get_by_name_and_creator(new_name, creator_user_id)
                if existing_by_name:
                    logger.warning(f"Template name '{new_name}' already exists for user {creator_user_id}. Cannot create copy.")
                    raise ValueError(f"You already have a template named '{new_name}'.") # OLD.py raised ValueError

                # Create the new main template entity (OLD.py set is_shared=True here!)
                new_template = GuildTemplateEntity(
                    template_name=new_name,
                    template_description=new_description, # Use provided description
                    creator_user_id=creator_user_id,
                    guild_id=None,
                    is_shared=True # <<< This was the behavior in OLD.py for share_template
                )
                session.add(new_template)
                await session.flush()
                new_template_id = new_template.id
                logger.debug(f"Created new template record with ID: {new_template_id} (is_shared=True based on OLD.py)")

                # Fetch original structure (categories and channels)
                original_categories = await cat_repo.get_by_template_id(original_template_id)
                original_channels = await chan_repo.get_by_template_id(original_template_id)

                # Copy categories and their permissions
                original_cat_id_to_new_cat_id = {}
                for original_cat in original_categories:
                    new_category = GuildTemplateCategoryEntity(
                        guild_template_id=new_template_id,
                        category_name=original_cat.category_name,
                        position=original_cat.position,
                    )
                    session.add(new_category)
                    await session.flush()
                    new_category_id = new_category.id
                    original_cat_id = original_cat.id
                    original_cat_id_to_new_cat_id[original_cat_id] = new_category_id
                    logger.debug(f"Copied category '{new_category.category_name}' (Original ID: {original_cat_id}, New ID: {new_category_id})")

                    # Copy category permissions (OLD.py iterated loaded perms, need to fetch)
                    original_perms = await cat_perm_repo.get_by_category_template_id(original_cat.id)
                    for perm in original_perms:
                        new_cat_perm = GuildTemplateCategoryPermissionEntity(
                            category_template_id=new_category_id,
                            role_name=perm.role_name,
                            allow_permissions_bitfield=perm.allow_permissions_bitfield,
                            deny_permissions_bitfield=perm.deny_permissions_bitfield
                        )
                        session.add(new_cat_perm)
                    await session.flush() # Flush permissions for this category (as in OLD.py structure)

                # Copy channels and their permissions
                for original_chan in original_channels:
                    original_parent_id = original_chan.parent_category_template_id
                    new_parent_id = original_cat_id_to_new_cat_id.get(original_parent_id) if original_parent_id else None

                    new_channel = GuildTemplateChannelEntity(
                        guild_template_id=new_template_id,
                        parent_category_template_id=new_parent_id,
                        channel_name=original_chan.channel_name,
                        channel_type=original_chan.channel_type,
                        position=original_chan.position,
                        topic=original_chan.topic,
                        is_nsfw=original_chan.is_nsfw,
                        slowmode_delay=original_chan.slowmode_delay
                    )
                    session.add(new_channel)
                    await session.flush() # Flush to get channel ID
                    new_channel_id = new_channel.id

                    # Copy channel permissions (OLD.py iterated loaded perms, need to fetch)
                    original_perms = await chan_perm_repo.get_by_channel_template_id(original_chan.id)
                    for perm in original_perms:
                         new_chan_perm = GuildTemplateChannelPermissionEntity(
                             channel_template_id=new_channel_id,
                             role_name=perm.role_name,
                             allow_permissions_bitfield=perm.allow_permissions_bitfield,
                             deny_permissions_bitfield=perm.deny_permissions_bitfield
                         )
                         session.add(new_chan_perm)
                    await session.flush() # Flush perms for channel

                await session.commit()
                logger.info(f"Successfully committed shared/copied template '{new_name}' (New ID: {new_template_id})")

                # Return structure from OLD.py
                # Fetch the newly created template entity to get created_at
                await session.refresh(new_template)
                return {
                    "template_id": new_template_id,
                    "template_name": new_template.template_name,
                    "created_at": new_template.created_at.isoformat() if new_template.created_at else None,
                    # Add other fields if needed by the controller/frontend
                }

            except ValueError as ve:
                 logger.error(f"Value error during template share: {ve}", exc_info=False)
                 await session.rollback()
                 raise ve # Re-raise ValueError as in OLD.py
            except Exception as e:
                logger.error(f"Error during template share transaction: {e}", exc_info=True)
                await session.rollback()
                return None # Return None on other errors as in OLD.py
