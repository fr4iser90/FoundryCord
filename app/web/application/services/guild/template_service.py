from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_, or_, update, delete
from datetime import datetime

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
from app.web.interfaces.api.rest.v1.schemas.guild_template_schemas import GuildStructureUpdatePayload, GuildStructureTemplateCreateFromStructure
# --- Add User Repo/Entity Imports --- 
from app.shared.infrastructure.repositories.auth.user_repository_impl import UserRepositoryImpl
from app.shared.infrastructure.models.auth import AppUserEntity
# -----------------------------------
# Import Exceptions
from app.shared.domain.exceptions import TemplateNotFound, PermissionDenied, InvalidOperation, DomainException, ConfigurationNotFound
# --- ADD Guild Config Repo --- 
from app.shared.infrastructure.repositories.discord import GuildConfigRepositoryImpl
# ---------------------------

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
                # --- ADD Guild Config Repo --- 
                guild_config_repo = GuildConfigRepositoryImpl(session)
                # ---------------------------

                # --- Fetch GuildConfig --- 
                guild_config = await guild_config_repo.get_by_guild_id(guild_id)
                delete_unmanaged_flag = guild_config.template_delete_unmanaged if guild_config else False # Default to False if no config found
                logger.debug(f"GuildConfig found for {guild_id}. template_delete_unmanaged is {delete_unmanaged_flag}")
                # -------------------------

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
                    "is_shared": template.is_shared, # Include shared status
                    "creator_user_id": template.creator_user_id, # Include creator ID
                    "template_delete_unmanaged": delete_unmanaged_flag,
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
                
                # --- Fetch GuildConfig if guild_id is available --- 
                delete_unmanaged_flag = False # Default
                if template.guild_id: # Only fetch config if template is linked to a guild
                    guild_config_repo = GuildConfigRepositoryImpl(session)
                    guild_config = await guild_config_repo.get_by_guild_id(template.guild_id)
                    delete_unmanaged_flag = guild_config.template_delete_unmanaged if guild_config else False
                    logger.debug(f"GuildConfig fetched for guild {template.guild_id}. template_delete_unmanaged is {delete_unmanaged_flag}")
                else:
                    logger.debug(f"Template {template_id} is not linked to a specific guild. delete_unmanaged flag defaults to False.")
                # -------------------------------------------------

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
                    "is_shared": template.is_shared, # Include shared status
                    "creator_user_id": template.creator_user_id, # Include creator ID
                    "template_delete_unmanaged": delete_unmanaged_flag,
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
                
                # --- Build Filter Conditions ---
                # Condition 1: Template created by the user AND is NOT shared
                user_owned_not_shared = and_(
                    GuildTemplateEntity.creator_user_id == user_id,
                    GuildTemplateEntity.is_shared == False 
                )
                
                # Condition 2: The initial snapshot for the context guild (creator is NULL)
                initial_snapshot_condition = None
                if context_guild_id:
                    initial_snapshot_condition = and_(
                        GuildTemplateEntity.guild_id == context_guild_id, 
                        GuildTemplateEntity.creator_user_id.is_(None) # Check for NULL explicitly
                        # No is_shared check here, assume initial snapshot is always shown regardless
                    )
                
                # Combine conditions: Show (user-owned AND NOT shared) OR (initial snapshot)
                filter_conditions = [user_owned_not_shared]
                if initial_snapshot_condition is not None:
                    filter_conditions.append(initial_snapshot_condition)
                
                final_filter = or_(*filter_conditions)
                # --- End Filter Conditions ---

                query = (
                    select(GuildTemplateEntity)
                    .where(final_filter) # Use the corrected filter
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

    async def list_shared_templates(self) -> List[Dict[str, Any]]:
        """Lists basic information about publicly shared guild templates."""
        logger.info(f"Listing shared guild templates requested.")
        templates_info = []

        try:
            async with session_context() as session:
                template_repo = GuildTemplateRepositoryImpl(session)
                # Assuming a flag `is_shared` exists on the entity
                # or a specific convention denotes shared templates.
                # Adjust the query as needed based on the actual schema.
                shared_templates: List[GuildTemplateEntity] = await template_repo.get_shared_templates() # Needs implementation in repo

                for template in shared_templates:
                    templates_info.append({
                        "template_id": template.id,
                        "template_name": template.template_name,
                        "description": template.template_description,
                        "creator_user_id": template.creator_user_id,
                        # Add other relevant fields if needed
                    })
            
            logger.info(f"Found {len(templates_info)} shared templates.")
            return templates_info

        except NotImplementedError:
             logger.error("Repository method 'get_shared_templates' not implemented.")
             raise # Re-raise so controller can return 501
        except Exception as e:
            logger.error(f"Error listing shared templates: {e}", exc_info=True)
            raise # Re-raise for controller to handle

    # --- NEW METHOD: Get Shared Template Details ---
    async def get_shared_template_details(self, template_id: int) -> Optional[Dict[str, Any]]:
        """Fetches the full details of a specific shared guild template by its ID."""
        logger.info(f"Fetching details for shared template_id: {template_id}")
        try:
            async with session_context() as session:
                # 1. Get the main template record by its primary key
                template_repo = GuildTemplateRepositoryImpl(session)
                template: Optional[GuildTemplateEntity] = await template_repo.get_by_id(template_id)

                # 2. Validate if it exists and is actually shared
                if not template:
                    logger.warning(f"No template found for template_id: {template_id}")
                    return None
                
                # TODO: Add check for shared status (e.g., template.is_shared == True)
                # If there's no explicit shared flag, this check might not be needed if the controller
                # only calls this for known shared templates, but it's safer to verify.
                # if not template.is_shared:
                #    logger.warning(f"Template {template_id} exists but is not marked as shared.")
                #    return None # Or raise an error?

                template_db_id = template.id
                logger.debug(f"Found shared template ID {template_db_id}")

                # 3. Fetch Categories and Channels (similar to get_template_by_id)
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

                chan_stmt = (
                    select(GuildTemplateChannelEntity)
                    .where(GuildTemplateChannelEntity.guild_template_id == template_db_id)
                    .options(selectinload(GuildTemplateChannelEntity.permissions))
                    .order_by(GuildTemplateChannelEntity.position)
                )
                chan_result = await session.execute(chan_stmt)
                channels: List[GuildTemplateChannelEntity] = chan_result.scalars().all()

                # 4. Structure the data (similar to get_template_by_id)
                structured_template = {
                    "guild_id": template.guild_id, # May be null or less relevant for shared
                    "template_id": template.id,
                    "template_name": template.template_name,
                    "created_at": template.created_at.isoformat() if template.created_at else None,
                    # Add description if available in schema
                    # "description": template.template_description,
                    "categories": [],
                    "channels": []
                }
                # Populate categories...
                for cat in categories:
                    category_data = {
                        "id": cat.id,
                        "name": cat.category_name, # Use consistent naming with other methods
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
                # Populate channels...
                for chan in channels:
                    channel_data = {
                        "id": chan.id,
                        "name": chan.channel_name, # Use consistent naming
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
                
                logger.info(f"Successfully fetched and structured shared template {template_id}")
                return structured_template

        except Exception as e:
            logger.error(f"Error fetching shared template details for template_id {template_id}: {e}", exc_info=True)
            return None # Controller will handle 500

    # --- NEW METHOD: Copy Shared Template ---
    async def copy_shared_template(
        self,
        shared_template_id: int,
        user_id: int,
        new_name_optional: Optional[str] = None
    ) -> Optional[Dict[str, Any]]: # Return details of the NEW template
        """Copies a shared template structure to create a new saved template for a user."""
        logger.info(f"Attempting to copy shared template {shared_template_id} for user {user_id}. New name: '{new_name_optional}'")
        try:
            async with session_context() as session:
                # Use a single session for all repository operations within the copy
                template_repo = GuildTemplateRepositoryImpl(session)
                cat_repo = GuildTemplateCategoryRepositoryImpl(session)
                chan_repo = GuildTemplateChannelRepositoryImpl(session)
                cat_perm_repo = GuildTemplateCategoryPermissionRepositoryImpl(session)
                chan_perm_repo = GuildTemplateChannelPermissionRepositoryImpl(session)

                # 1. Fetch the original shared template details (ensure it exists and is shared)
                original_template = await template_repo.get_by_id(shared_template_id)
                if not original_template:
                    logger.error(f"Shared template {shared_template_id} not found for copying.")
                    return None
                # TODO: Check original_template.is_shared if applicable
                # if not original_template.is_shared:
                #     logger.error(f"Template {shared_template_id} is not shared and cannot be copied.")
                #     return None
                
                original_categories = await cat_repo.get_by_template_id(shared_template_id)
                original_channels = await chan_repo.get_by_template_id(shared_template_id)
                # Note: Permissions are loaded via relationships usually

                # 2. Create the new GuildTemplateEntity
                new_template_name = new_name_optional if new_name_optional else f"Copy of {original_template.template_name}"
                
                new_template = await template_repo.create(
                    creator_user_id=user_id,
                    template_name=new_template_name,
                    template_description=original_template.template_description, # Copy description
                    guild_id=None, # Not tied to a specific guild initially
                    is_shared=False, # New copy is private by default
                    # Copy other relevant fields from original_template if they exist
                )
                if not new_template:
                    logger.error("Failed to create new template record in database during copy.")
                    return None
                
                new_template_id = new_template.id
                logger.info(f"Created new template record (ID: {new_template_id}) for copy.")

                # --- Copy Categories and Channels --- 
                category_id_map = {} # Map old category ID -> new category ID

                # Copy Categories
                for original_cat in original_categories:
                    new_cat = await cat_repo.create(
                        guild_template_id=new_template_id,
                        category_name=original_cat.category_name,
                        position=original_cat.position
                        # TODO: Copy other category attributes if needed
                    )
                    if not new_cat:
                         logger.error(f"Failed to copy category '{original_cat.category_name}' (original ID {original_cat.id}) to new template {new_template_id}.")
                         # Consider rollback or partial success handling
                         continue # Skip this category and its channels?
                    
                    category_id_map[original_cat.id] = new_cat.id
                    
                    # Copy Category Permissions
                    original_cat_perms = await cat_perm_repo.get_by_category_template_id(original_cat.id)
                    for perm in original_cat_perms:
                        await cat_perm_repo.create(
                             category_template_id=new_cat.id,
                             role_name=perm.role_name,
                             allow_permissions_bitfield=perm.allow_permissions_bitfield,
                             deny_permissions_bitfield=perm.deny_permissions_bitfield
                         )

                # Copy Channels
                for original_chan in original_channels:
                    new_parent_category_id = category_id_map.get(original_chan.parent_category_template_id)
                    if original_chan.parent_category_template_id and not new_parent_category_id:
                        logger.warning(f"Could not find new parent category ID for original parent {original_chan.parent_category_template_id} when copying channel '{original_chan.channel_name}'. Setting parent to None.")

                    new_chan = await chan_repo.create(
                        guild_template_id=new_template_id,
                        parent_category_template_id=new_parent_category_id, # Use the mapped ID
                        channel_name=original_chan.channel_name,
                        channel_type=original_chan.channel_type,
                        position=original_chan.position,
                        topic=original_chan.topic,
                        is_nsfw=original_chan.is_nsfw,
                        slowmode_delay=original_chan.slowmode_delay
                        # TODO: Copy other channel attributes if needed
                    )
                    if not new_chan:
                         logger.error(f"Failed to copy channel '{original_chan.channel_name}' (original ID {original_chan.id}) to new template {new_template_id}.")
                         continue
                    
                    # Copy Channel Permissions
                    original_chan_perms = await chan_perm_repo.get_by_channel_template_id(original_chan.id)
                    for perm in original_chan_perms:
                         await chan_perm_repo.create(
                             channel_template_id=new_chan.id,
                             role_name=perm.role_name,
                             allow_permissions_bitfield=perm.allow_permissions_bitfield,
                             deny_permissions_bitfield=perm.deny_permissions_bitfield
                         )
                         
                # --- End Copy --- 

                logger.info(f"Successfully copied structure from shared template {shared_template_id} to new template {new_template_id} for user {user_id}.")
                
                # Optionally, fetch and return the newly created template details
                # This might involve calling self.get_template_by_id(new_template_id)
                # For now, just return True or a simple dict
                return { "status": "success", "new_template_id": new_template_id, "new_template_name": new_template_name }

        except Exception as e:
            logger.error(f"Error copying shared template {shared_template_id} for user {user_id}: {e}", exc_info=True)
            return None # Indicate failure

    async def share_template(
        self, 
        original_template_id: int, 
        new_name: str, 
        new_description: Optional[str], 
        creator_user_id: int
    ) -> Optional[Dict[str, Any]]:
        """Creates a new template by copying an existing one."""
        logger.info(f"Attempting to share/copy template ID {original_template_id} as '{new_name}' for user {creator_user_id}")
        
        # Fetch the original template structure first
        original_template_data = await self.get_template_by_id(original_template_id)
        if not original_template_data:
            logger.warning(f"Original template ID {original_template_id} not found for sharing.")
            return None # Original template doesn't exist

        async with session_context() as session:
            try:
                # Instantiate repositories within the session
                template_repo = GuildTemplateRepositoryImpl(session)
                cat_repo = GuildTemplateCategoryRepositoryImpl(session)
                chan_repo = GuildTemplateChannelRepositoryImpl(session)
                cat_perm_repo = GuildTemplateCategoryPermissionRepositoryImpl(session)
                chan_perm_repo = GuildTemplateChannelPermissionRepositoryImpl(session)

                # Check if the new name already exists FOR THIS USER
                existing_by_name = await template_repo.get_by_name_and_creator(new_name, creator_user_id)
                if existing_by_name:
                    logger.warning(f"Template name '{new_name}' already exists for user {creator_user_id}. Cannot create copy.")
                    raise ValueError(f"You already have a template named '{new_name}'.")

                # 1. Create the new main template entity
                new_template = GuildTemplateEntity(
                    template_name=new_name,
                    template_description=new_description,
                    creator_user_id=creator_user_id,
                    guild_id=None,  # Not tied to a specific guild initially
                    is_shared=True # Set to True when sharing/copying
                )
                session.add(new_template)
                await session.flush() # Get the new template ID
                new_template_id = new_template.id
                logger.debug(f"Created new template record with ID: {new_template_id}")

                # 2. Copy categories and their permissions
                original_cat_id_to_new_cat_id = {} # Map old category IDs to new ones
                for original_cat_data in original_template_data.get("categories", []):
                    new_category = GuildTemplateCategoryEntity(
                        guild_template_id=new_template_id,
                        category_name=original_cat_data["name"],
                        position=original_cat_data["position"]
                    )
                    session.add(new_category)
                    await session.flush() # Get new category ID
                    new_category_id = new_category.id
                    original_cat_id = original_cat_data["id"]
                    original_cat_id_to_new_cat_id[original_cat_id] = new_category_id
                    logger.debug(f"Copied category '{new_category.category_name}' (Original ID: {original_cat_id}, New ID: {new_category_id})")

                    # Copy category permissions
                    for original_perm_data in original_cat_data.get("permissions", []):
                        new_cat_perm = GuildTemplateCategoryPermissionEntity(
                            category_template_id=new_category_id,
                            role_name=original_perm_data["role_name"],
                            allow_permissions_bitfield=original_perm_data["allow"],
                            deny_permissions_bitfield=original_perm_data["deny"]
                        )
                        session.add(new_cat_perm)
                    await session.flush() # Flush permissions for this category

                # 3. Copy channels and their permissions
                for original_chan_data in original_template_data.get("channels", []):
                    original_parent_id = original_chan_data.get("parent_category_template_id")
                    new_parent_id = original_cat_id_to_new_cat_id.get(original_parent_id) if original_parent_id else None

                    new_channel = GuildTemplateChannelEntity(
                        guild_template_id=new_template_id,
                        channel_name=original_chan_data["name"],
                        channel_type=original_chan_data["type"],
                        position=original_chan_data["position"],
                        topic=original_chan_data.get("topic"),
                        is_nsfw=original_chan_data.get("is_nsfw", False),
                        slowmode_delay=original_chan_data.get("slowmode_delay", 0),
                        parent_category_template_id=new_parent_id # Use the mapped new category ID
                    )
                    session.add(new_channel)
                    await session.flush() # Get new channel ID
                    new_channel_id = new_channel.id
                    logger.debug(f"Copied channel '{new_channel.channel_name}' (Original ID: {original_chan_data['id']}, New ID: {new_channel_id})")

                    # Copy channel permissions
                    for original_perm_data in original_chan_data.get("permissions", []):
                        new_chan_perm = GuildTemplateChannelPermissionEntity(
                            channel_template_id=new_channel_id,
                            role_name=original_perm_data["role_name"],
                            allow_permissions_bitfield=original_perm_data["allow"],
                            deny_permissions_bitfield=original_perm_data["deny"]
                        )
                        session.add(new_chan_perm)
                    await session.flush() # Flush permissions for this channel

                # 4. Commit the entire transaction
                await session.commit()
                logger.info(f"Successfully committed shared/copied template '{new_name}' (New ID: {new_template_id})")

                # Return some representation of the new template (optional)
                # Could call get_template_by_id(new_template_id) or just return basic info
                return {
                    "template_id": new_template_id,
                    "template_name": new_template.template_name,
                    "created_at": new_template.created_at.isoformat() if new_template.created_at else None,
                    # Add other fields if needed by the controller/frontend
                }

            except ValueError as ve: # Catch specific error for duplicate name
                 logger.error(f"Value error during template share: {ve}", exc_info=False) # Log as error, but don't need full traceback
                 await session.rollback()
                 # Propagate the error so controller can potentially return 409 or similar
                 raise ve 
            except Exception as e:
                logger.error(f"Error during template share transaction: {e}", exc_info=True)
                await session.rollback() # Rollback on any other error
                # Return None or re-raise a custom service exception
                return None

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

    async def activate_template(
        self, 
        db: AsyncSession, # Use the session passed from controller
        template_id: int, 
        target_guild_id: str, # <<<--- NEUER PARAMETER
        requesting_user: AppUserEntity
    ) -> None: # Return None on success, raise exception on failure
        """
        Activates a specific template for the target guild.
        Ensures only one template is active per guild by deactivating others.
        Performs permission checks.
        """
        logger.info(f"Attempting to activate template ID {template_id} for guild {target_guild_id} by user {requesting_user.id}") # Updated log

        # Use the provided session directly, no need for session_context here
        template_repo = GuildTemplateRepositoryImpl(db)

        # 1. Fetch the template to activate
        template_to_activate: Optional[GuildTemplateEntity] = await template_repo.get_by_id(template_id)

        if not template_to_activate:
            logger.warning(f"Activate failed: Template ID {template_id} not found.")
            raise TemplateNotFound(template_id=template_id) 

        logger.debug(f"Found template '{template_to_activate.template_name}' (ID: {template_id}) for activation.")

        # 2. Permission Check
        # TODO: Enhance permission check - does user have rights *in the target_guild_id*?
        # Current check is based on template creator/bot owner.
        is_creator = template_to_activate.creator_user_id == requesting_user.id
        is_bot_owner = requesting_user.is_owner
        is_guild_admin_or_owner = False # Placeholder 

        if not (is_creator or is_bot_owner or is_guild_admin_or_owner):
            logger.warning(f"Permission denied: User {requesting_user.id} tried to activate template {template_id} for guild {target_guild_id}.")
            raise PermissionDenied(
                user_id=requesting_user.id, 
                action=f"activate template {template_id} for guild {target_guild_id}",
                message=f"Only the template creator or a bot owner can activate this template (Guild admin check pending)."
            )
        
        logger.debug(f"Permission granted for user {requesting_user.id} to activate template {template_id} for guild {target_guild_id}.")

        # 5. Deactivate other active templates for the TARGET guild
        logger.info(f"Deactivating other active templates for guild {target_guild_id} (if any).")
        deactivate_stmt = (
            update(GuildTemplateEntity)
            .where(
                GuildTemplateEntity.guild_id == target_guild_id, # <<<--- Verwende target_guild_id
                GuildTemplateEntity.is_active == True,
                GuildTemplateEntity.id != template_id # Exclude the one we are activating
            )
            .values(is_active=False)
            .execution_options(synchronize_session="fetch") 
        )
        await db.execute(deactivate_stmt)

        # 6. Activate the target template
        logger.debug(f"Activating target template {template_id}")
        template_to_activate.is_active = True

        # --- Update GuildConfigEntity.active_template_id für die TARGET guild ---
        logger.debug(f"Updating GuildConfigEntity for guild {target_guild_id} to set active_template_id={template_id}")
        from app.shared.infrastructure.models.discord import GuildConfigEntity
        update_config_stmt = (
            update(GuildConfigEntity)
            .where(GuildConfigEntity.guild_id == target_guild_id) # <<<--- Verwende target_guild_id
            .values(active_template_id=template_id)
        )
        config_update_result = await db.execute(update_config_stmt)

        if config_update_result.rowcount == 0:
            logger.error(f"Could not find or update GuildConfigEntity for guild {target_guild_id} to set active_template_id={template_id}. Guild config might be missing!")
            raise InvalidOperation(f"Could not update guild configuration for guild {target_guild_id}. Configuration might be missing.")
        else:
            logger.debug(f"Successfully updated GuildConfigEntity.active_template_id for guild {target_guild_id}.")
        # --- ENDE Update GuildConfig ---

        logger.info(f"Successfully marked template {template_id} as active and updated GuildConfig (pending commit) for guild {target_guild_id}")

    # --- NEW: Placeholder for permission check --- 
    async def check_user_can_edit_template(self, db: AsyncSession, user_id: int, template_id: int) -> bool:
        """Checks if a user has permission to edit a specific template.
           Placeholder logic: Allows creator or bot owners.
        """
        logger.debug(f"Checking edit permission for user {user_id} on template {template_id}")
        # TODO: Implement proper role/permission checks if needed beyond creator/owner.
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
            
            # TODO: Add check for bot owner status if AppUserEntity is easily available
            # This might require fetching the user entity or passing it down
            # For now, just rely on creator check
            # Example: 
            # user_repo = UserRepositoryImpl(db) # Assuming you have UserRepositoryImpl
            # user = await user_repo.get_by_id(user_id)
            # if user and user.is_owner:
            #    logger.debug(f"User {user_id} is a bot owner. Permission granted for template {template_id}.")
            #    return True

            logger.warning(f"Permission denied: User {user_id} is not creator of template {template_id}.")
            return False
        except ValueError as ve:
            raise ve # Re-raise ValueError if template not found
        except Exception as e:
            logger.error(f"Error checking edit permission for user {user_id} on template {template_id}: {e}", exc_info=True)
            return False # Deny permission on error

    # --- RESTORED: Method to update template structure (Original Version) --- 
    async def update_template_structure(
        self,
        db: AsyncSession,
        template_id: int,
        structure_payload: GuildStructureUpdatePayload,
        requesting_user: AppUserEntity # Added user for permission check
    ) -> Dict[str, Any]: # Return a dictionary now
        """
        Updates the structure (positions, parentage, properties) of categories and channels
        for a given template based on the payload received from the frontend designer.
        Handles updates to existing items and deletion of items removed in the designer.
        Returns a dictionary containing the updated template entity and the relevant delete_unmanaged flag.
        NOTE: Does not currently handle adding *new* items via this method.
        """
        logger.info(f"Attempting structure update for template ID: {template_id} by user {requesting_user.id}")

        template_repo = GuildTemplateRepositoryImpl(db)
        category_repo = GuildTemplateCategoryRepositoryImpl(db) # Use passed session
        channel_repo = GuildTemplateChannelRepositoryImpl(db)   # Use passed session

        # --- 1. Permission Check (This is redundant if controller checks, but safe) ---
        template = await template_repo.get_by_id(template_id)
        if not template:
            logger.error(f"Update failed: Template {template_id} not found.")
            raise TemplateNotFound(template_id=template_id)

        is_creator = template.creator_user_id == requesting_user.id
        is_bot_owner = requesting_user.is_owner
        if not is_creator and not is_bot_owner:
             logger.warning(f"Permission denied for user {requesting_user.id} to update structure of template {template_id}")
             raise PermissionDenied(user_id=requesting_user.id, action=f"update structure for template {template_id}")

        logger.debug(f"Permission granted for user {requesting_user.id} to update template {template_id}.")

        # --- 2. Fetch Existing Structure from DB ---
        existing_categories = await category_repo.get_by_template_id(template_id)
        existing_channels = await channel_repo.get_by_template_id(template_id)

        existing_cats_by_dbid = {cat.id: cat for cat in existing_categories}
        existing_chans_by_dbid = {chan.id: chan for chan in existing_channels}
        
        existing_cat_dbids = set(existing_cats_by_dbid.keys())
        existing_chan_dbids = set(existing_chans_by_dbid.keys())

        logger.debug(f"Template {template_id}: Found {len(existing_cat_dbids)} existing categories, {len(existing_chan_dbids)} existing channels.")

        # --- 3. Process Incoming Payload ---
        incoming_cat_dbids = set()
        incoming_chan_dbids = set()
        incoming_nodes_data = {} # Map DB ID -> { id_str, parent_id_str, position }

        for node_data in structure_payload.nodes:
            node_id_str = node_data.id
            item_db_id = None
            item_type = None

            if node_id_str.startswith("category_"):
                item_type = "category"
                try: item_db_id = int(node_id_str.split("_")[1])
                except (IndexError, ValueError): continue # Skip invalid ID
                if item_db_id in existing_cat_dbids: # Only process known items
                     incoming_cat_dbids.add(item_db_id)
                     incoming_nodes_data[item_db_id] = node_data
                else:
                     logger.warning(f"Incoming node {node_id_str} does not match an existing category in template {template_id}. Ignoring.")

            elif node_id_str.startswith("channel_"):
                item_type = "channel"
                try: item_db_id = int(node_id_str.split("_")[1])
                except (IndexError, ValueError): continue # Skip invalid ID
                if item_db_id in existing_chan_dbids: # Only process known items
                    incoming_chan_dbids.add(item_db_id)
                    incoming_nodes_data[item_db_id] = node_data
                else:
                    logger.warning(f"Incoming node {node_id_str} does not match an existing channel in template {template_id}. Ignoring.")
        
        logger.debug(f"Template {template_id}: Processing {len(incoming_cat_dbids)} incoming categories, {len(incoming_chan_dbids)} incoming channels.")

        # --- 4. Identify Changes ---
        cats_to_delete_ids = existing_cat_dbids - incoming_cat_dbids
        chans_to_delete_ids = existing_chan_dbids - incoming_chan_dbids
        
        items_to_update = [] # Collect DB entities that need updating

        # --- 5. Process Updates ---
        # --- 5a. Process Property Changes (NEW) --- 
        if structure_payload.property_changes:
             logger.info(f"Processing {len(structure_payload.property_changes)} nodes with property changes for template {template_id}")
             for node_key, changes in structure_payload.property_changes.items():
                 try:
                     item_type, item_db_id_str = node_key.split('_')
                     item_db_id = int(item_db_id_str)

                     target_entity = None
                     if item_type == 'category' and item_db_id in existing_cats_by_dbid:
                         target_entity = existing_cats_by_dbid[item_db_id]
                     elif item_type == 'channel' and item_db_id in existing_chans_by_dbid:
                          target_entity = existing_chans_by_dbid[item_db_id]
                     
                     if target_entity:
                         logger.debug(f"Applying property changes to {item_type} ID {item_db_id}: {changes}")
                         for prop_name, new_value in changes.items():
                             # Map frontend prop names to entity attribute names if necessary
                             entity_attr_name = prop_name # Default: assume direct mapping
                             if item_type == 'category':
                                 if prop_name == 'name': entity_attr_name = 'category_name'
                                 # Add other category mappings if needed
                             elif item_type == 'channel':
                                 if prop_name == 'name': entity_attr_name = 'channel_name'
                                 # if prop_name == 'type': entity_attr_name = 'channel_type' # Type change unlikely here
                                 # is_nsfw and slowmode_delay likely map directly
                                 # topic likely maps directly
                             
                             if hasattr(target_entity, entity_attr_name):
                                 current_value = getattr(target_entity, entity_attr_name)
                                 # Type casting might be needed (e.g., string to int for slowmode)
                                 try:
                                     # Attempt type casting based on expected type
                                     expected_type = type(current_value)
                                     if expected_type is bool and isinstance(new_value, str): # Handle string 'true'/'false' from JS for bool
                                          casted_value = new_value.lower() == 'true'
                                     elif expected_type is int and isinstance(new_value, (str, bool)): # Handle potential string/bool for int
                                          casted_value = int(new_value)
                                     elif expected_type is float and isinstance(new_value, (str, bool, int)): # Handle potential string/bool/int for float
                                         casted_value = float(new_value)
                                     else:
                                          casted_value = expected_type(new_value)
                                     
                                     if current_value != casted_value:
                                          logger.debug(f"  Updating {entity_attr_name} from '{current_value}' to '{casted_value}'")
                                          setattr(target_entity, entity_attr_name, casted_value)
                                          if target_entity not in items_to_update:
                                              items_to_update.append(target_entity)
                                     else:
                                          logger.debug(f"  Skipping {entity_attr_name}: Value '{current_value}' already matches new value '{casted_value}'")
                                 except (ValueError, TypeError) as cast_err:
                                      logger.warning(f"  Could not apply change for {entity_attr_name}: Failed to cast new value '{new_value}' to expected type {expected_type}. Error: {cast_err}")
                             else:
                                 logger.warning(f"  Property '{prop_name}' (mapped to '{entity_attr_name}') not found on {item_type} entity ID {item_db_id}. Skipping.")
                     else:
                         logger.warning(f"Node key '{node_key}' in property changes refers to a non-existent or mismatched item. Skipping changes: {changes}")

                 except (ValueError, IndexError) as e:
                     logger.warning(f"Could not parse node key '{node_key}' from property changes payload: {e}. Skipping changes: {changes}")
        # --- End Property Changes ---

        # Update existing categories
        for cat_dbid in incoming_cat_dbids:
            category = existing_cats_by_dbid[cat_dbid]
            node_data = incoming_nodes_data[cat_dbid]
            if category.position != node_data.position:
                logger.debug(f"Updating category {cat_dbid} position from {category.position} to {node_data.position}")
                category.position = node_data.position
                items_to_update.append(category)

        # Update existing channels
        for chan_dbid in incoming_chan_dbids:
            channel = existing_chans_by_dbid[chan_dbid]
            node_data = incoming_nodes_data[chan_dbid]
            needs_update = False

            # Check position
            if channel.position != node_data.position:
                logger.debug(f"Updating channel {chan_dbid} position from {channel.position} to {node_data.position}")
                channel.position = node_data.position
                needs_update = True

            # Check parent
            new_parent_db_id: Optional[int] = None
            parent_id_str = node_data.parent_id
            if parent_id_str and parent_id_str.startswith("category_"):
                try:
                    potential_parent_dbid = int(parent_id_str.split("_")[1])
                    # IMPORTANT: Check if the potential parent *still exists* in the incoming structure
                    if potential_parent_dbid in incoming_cat_dbids:
                         new_parent_db_id = potential_parent_dbid
                    else:
                         logger.warning(f"Channel {chan_dbid} requested parent {parent_id_str} which is being deleted or wasn't found. Setting parent to NULL.")
                except (IndexError, ValueError):
                    logger.warning(f"Channel {chan_dbid} has invalid parent ID format {parent_id_str}. Setting parent to NULL.")
            # If parent_id_str starts with template_ or is '#', new_parent_db_id remains None (correct)

            if channel.parent_category_template_id != new_parent_db_id:
                logger.debug(f"Updating channel {chan_dbid} parent from {channel.parent_category_template_id} to {new_parent_db_id}")
                channel.parent_category_template_id = new_parent_db_id
                needs_update = True

            if needs_update and channel not in items_to_update:
                items_to_update.append(channel)

        # --- 6. Perform Deletions ---
        if cats_to_delete_ids:
             logger.info(f"Deleting {len(cats_to_delete_ids)} categories from template {template_id}: {cats_to_delete_ids}")
             # Assuming cascading delete handles permissions, otherwise delete them first
             delete_cat_stmt = delete(GuildTemplateCategoryEntity).where(GuildTemplateCategoryEntity.id.in_(cats_to_delete_ids))
             await db.execute(delete_cat_stmt)

        if chans_to_delete_ids:
             logger.info(f"Deleting {len(chans_to_delete_ids)} channels from template {template_id}: {chans_to_delete_ids}")
             # Assuming cascading delete handles permissions, otherwise delete them first
             delete_chan_stmt = delete(GuildTemplateChannelEntity).where(GuildTemplateChannelEntity.id.in_(chans_to_delete_ids))
             await db.execute(delete_chan_stmt)

        # --- 7. Commit Changes ---
        if items_to_update or cats_to_delete_ids or chans_to_delete_ids:
            try:
                if items_to_update:
                     logger.info(f"Committing updates for {len(items_to_update)} items in template {template_id}")
                     db.add_all(items_to_update) # Add updated items if needed (SQLAlchemy might track automatically)
                
                await db.commit()
                logger.info(f"Successfully committed structure updates for template {template_id}")
            except Exception as e:
                logger.error(f"Database error committing structure updates for template {template_id}: {e}", exc_info=True)
                await db.rollback()
                raise DomainException(f"Failed to save structure updates due to database error.") from e
        else:
            logger.info(f"No structure changes detected for template {template_id}. Nothing to commit.")

        # --- 8. Return Updated Template AND Config Flag ---
        # Re-fetch the template with all necessary relationships eager-loaded
        logger.info(f"Re-fetching updated template {template_id} with eager loading.")
        try:
            stmt = (
                select(GuildTemplateEntity)
                .options(
                    selectinload(GuildTemplateEntity.categories)
                    .selectinload(GuildTemplateCategoryEntity.permissions),
                    selectinload(GuildTemplateEntity.channels)
                    .selectinload(GuildTemplateChannelEntity.permissions)
                )
                .where(GuildTemplateEntity.id == template_id)
            )
            result = await db.execute(stmt)
            updated_template_entity = result.scalar_one_or_none()

            if not updated_template_entity:
                logger.error(f"Failed to re-fetch template {template_id} after update.")
                raise DomainException(f"Failed to retrieve updated template data for template ID {template_id}.")

            logger.info(f"Successfully re-fetched template {template_id}.")

            # --- Fetch the delete_unmanaged flag ---
            delete_unmanaged_flag = False # Default value
            if updated_template_entity.guild_id:
                 logger.debug(f"Fetching GuildConfig for guild_id: {updated_template_entity.guild_id}")
                 config_repo = GuildConfigRepositoryImpl(db)
                 guild_config = await config_repo.get_by_guild_id(updated_template_entity.guild_id)
                 if guild_config:
                     delete_unmanaged_flag = guild_config.template_delete_unmanaged
                     logger.debug(f"Found GuildConfig. template_delete_unmanaged = {delete_unmanaged_flag}")
                 else:
                     logger.warning(f"No GuildConfig found for guild_id: {updated_template_entity.guild_id}. Defaulting delete_unmanaged to False.")
            else:
                 logger.warning(f"Template {template_id} is not associated with a guild_id. Defaulting delete_unmanaged to False.")
            # ----------------------------------------

            # Return both the entity and the flag in a dictionary
            return {
                "template_entity": updated_template_entity,
                "delete_unmanaged": delete_unmanaged_flag
            }

        except Exception as fetch_err:
            logger.error(f"Error re-fetching template {template_id} or its config after update: {fetch_err}", exc_info=True)
            raise DomainException(f"Failed to retrieve complete updated template data or config: {fetch_err}") from fetch_err

    # --- NEW Method to Create Template from Structure --- 
    async def create_template_from_structure(
        self, 
        db: AsyncSession, 
        creator_user_id: int, 
        payload: GuildStructureTemplateCreateFromStructure
    ) -> GuildTemplateEntity: # Return the newly created template entity
        """Creates a new template entity based on name, description, and a structure payload."""
        logger.info(f"Attempting to create template '{payload.new_template_name}' from structure for user {creator_user_id}")

        # Use provided session directly
        session = db
        template_repo = GuildTemplateRepositoryImpl(session)
        category_repo = GuildTemplateCategoryRepositoryImpl(session)
        channel_repo = GuildTemplateChannelRepositoryImpl(session)

        # 1. Basic Validation (e.g., check for name uniqueness if required)
        existing_by_name = await template_repo.get_by_name_and_creator(payload.new_template_name, creator_user_id)
        if existing_by_name:
             logger.warning(f"Template name '{payload.new_template_name}' already exists for user {creator_user_id}. Cannot create.")
             raise ValueError(f"You already have a template named '{payload.new_template_name}'.")

        # 2. Create the main Template Entity
        new_template = GuildTemplateEntity(
            template_name=payload.new_template_name,
            template_description=payload.new_template_description,
            creator_user_id=creator_user_id,
            is_shared=False, # Default to not shared
        )
        session.add(new_template)
        # We need the ID of the new template *before* creating children, so flush.
        try:
            await session.flush()
            await session.refresh(new_template)
            logger.info(f"Flushed new template '{new_template.template_name}'. Assigned ID: {new_template.id}")
        except Exception as e:
            logger.error(f"Database error flushing new template '{payload.new_template_name}': {e}", exc_info=True)
            await session.rollback()
            raise ValueError(f"Could not save initial template record: {e}") 

        # 3. Process Nodes and Create Categories/Channels
        created_categories_map = {} # Map jsTree ID ("category_XYZ") -> DB Entity
        nodes_to_create = []

        # First pass: Create Categories
        for node_data in payload.structure.nodes:
            if node_data.id.startswith("category_"):
                category_name = node_data.name if node_data.name else f"Category {node_data.id}" # Use name from payload or fallback
                logger.debug(f"Preparing category: ID={node_data.id}, Name='{category_name}', Pos={node_data.position}")
                new_category = GuildTemplateCategoryEntity(
                    guild_template_id=new_template.id,
                    category_name=category_name,
                    position=node_data.position
                )
                created_categories_map[node_data.id] = new_category # Store entity before flush
                nodes_to_create.append(new_category)

        # Add all categories first
        if nodes_to_create:
            session.add_all(nodes_to_create)
            try:
                await session.flush() # Flush to get category IDs
                logger.info(f"Flushed {len(created_categories_map)} new categories for template {new_template.id}")
                # Refresh categories to get their assigned IDs
                for js_id, cat_entity in created_categories_map.items():
                    await session.refresh(cat_entity)
                    logger.debug(f"Refreshed category '{cat_entity.category_name}' (jsID: {js_id}), got DB ID: {cat_entity.id}")
            except Exception as e:
                logger.error(f"Database error flushing categories for template {new_template.id}: {e}", exc_info=True)
                await session.rollback()
                raise ValueError(f"Could not save categories: {e}")
            nodes_to_create.clear() # Clear list for channels
        
        # Second pass: Create Channels
        for node_data in payload.structure.nodes:
            if node_data.id.startswith("channel_"):
                parent_category_db_id: Optional[int] = None
                parent_js_id = node_data.parent_id # Get parent ID from payload
                logger.debug(f"Processing Channel Node: ID={node_data.id}, PayloadParentID='{parent_js_id}'")

                if parent_js_id and parent_js_id.startswith("category_"):
                    # Look up the PARENT category entity using the jsTree ID from the payload
                    parent_category_entity = created_categories_map.get(parent_js_id)
                    if parent_category_entity:
                        # Get the DATABASE ID from the SQLAlchemy entity object (should be populated after flush/refresh)
                        parent_category_db_id = parent_category_entity.id 
                        logger.debug(f"  Found parent category entity in map. Extracted DB ID: {parent_category_db_id} (from Entity: {parent_category_entity})")
                    else:
                        # Log if the lookup failed
                        logger.warning(f"  Parent category entity NOT FOUND in map for key '{parent_js_id}'. Setting DB Parent ID to NULL.")
                        # parent_category_db_id remains None
                elif parent_js_id and parent_js_id.startswith("template_"):
                    logger.debug(f"  Parent is template root ('{parent_js_id}'). Setting DB Parent ID to NULL.")
                    # parent_category_db_id remains None
                else:
                    logger.warning(f"  Unrecognized or missing parent ID '{parent_js_id}'. Setting DB Parent ID to NULL.")
                    # parent_category_db_id remains None
                
                channel_name = node_data.name if node_data.name else f"Channel {node_data.id}" # Use name from payload or fallback
                channel_type = node_data.channel_type if node_data.channel_type else "text" # Use type from payload or fallback
                logger.debug(f"  Final assignment: Name='{channel_name}', Type='{channel_type}', ParentDBID={parent_category_db_id}, Pos={node_data.position}")

                new_channel = GuildTemplateChannelEntity(
                    guild_template_id=new_template.id,
                    channel_name=channel_name,
                    channel_type=channel_type,
                    position=node_data.position,
                    parent_category_template_id=parent_category_db_id,
                    topic=None # Placeholder topic - TODO: Add topic to payload?
                )
                nodes_to_create.append(new_channel)

        # Add all channels
        if nodes_to_create:
            session.add_all(nodes_to_create)
            try:
                await session.flush() # Flush to get channel IDs (optional)
                logger.info(f"Flushed {len(nodes_to_create)} new channels for template {new_template.id}")
            except Exception as e:
                logger.error(f"Database error flushing channels for template {new_template.id}: {e}", exc_info=True)
                await session.rollback()
                raise ValueError(f"Could not save channels: {e}")

        # 4. Commit the transaction
        try:
            await session.commit()
            logger.info(f"Successfully committed new template '{new_template.template_name}' (ID: {new_template.id}) and its structure.")
            # Refresh the main template entity to ensure relationships are loaded if accessed immediately after
            # Using options might be more efficient if only certain relationships are needed
            await session.refresh(new_template, attribute_names=['categories', 'channels'])
            return new_template
        except Exception as e:
            logger.error(f"Database error committing new template {new_template.id}: {e}", exc_info=True)
            await session.rollback()
            raise ValueError(f"Failed to commit new template: {e}") # Raise specific error

    # --- NEW Method to update template settings --- 
    async def update_template_settings(
        self, 
        db: AsyncSession, 
        guild_id: str, 
        delete_unmanaged: bool,
        requesting_user: AppUserEntity # For potential permission checks later
    ) -> bool:
        """Updates specific template application settings for a guild."""
        logger.info(f"Service attempting to update template_delete_unmanaged to {delete_unmanaged} for guild {guild_id}")
        try:
            # TODO: Add more robust permission check if needed (e.g., based on user role in guild)
            if not requesting_user.is_owner:
                 logger.warning(f"Permission denied in service for user {requesting_user.id} updating settings for guild {guild_id}")
                 raise PermissionDenied("User does not have permission to update these settings.")
            
            # Instantiate the repository
            config_repo = GuildConfigRepositoryImpl(db)
            
            # Call the repository method to update the flag
            success = await config_repo.update_template_delete_unmanaged(
                guild_id=guild_id,
                delete_unmanaged=delete_unmanaged
            )
            
            if success:
                logger.info(f"Successfully updated template_delete_unmanaged flag for guild {guild_id}")
            else:
                logger.warning(f"GuildConfigRepository failed to update flag for guild {guild_id} (config likely not found). Raising ConfigurationNotFound.")
                # Raise the specific exception if repo indicates failure (e.g., config not found)
                raise ConfigurationNotFound(f"Configuration for guild {guild_id} not found.")
                
            return True # Return True on success
            
        # Let specific exceptions bubble up to the controller
        except (PermissionDenied, ConfigurationNotFound) as e:
             raise e
        except Exception as e:
            logger.error(f"Unexpected error in update_template_settings for guild {guild_id}: {e}", exc_info=True)
            # Raise a generic domain exception or re-raise the original
            raise DomainException(f"An unexpected error occurred while updating template settings for guild {guild_id}.") from e

    # --- NEW Service Methods for Deleting Elements ---

    async def delete_template_category(self, db: AsyncSession, category_id: int) -> bool:
        """Deletes a specific category from a template database entry."""
        logger.info(f"Service attempting to delete template category ID: {category_id}")
        try:
            category_repo = GuildTemplateCategoryRepositoryImpl(db)
            category_to_delete = await category_repo.get_by_id(category_id)

            if not category_to_delete:
                logger.warning(f"Category ID {category_id} not found for deletion.")
                return False # Indicate not found

            # Optional: Add check if category has child channels before deleting?
            # For simplicity, we assume cascading delete is handled by DB or we allow deletion.
            # If a check is needed:
            # channel_repo = GuildTemplateChannelRepositoryImpl(db)
            # children_exist = await channel_repo.check_if_channels_exist_for_category(category_id)
            # if children_exist:
            #     logger.warning(f"Attempted to delete category {category_id} which still has child channels.")
            #     raise InvalidOperation("Cannot delete category with existing channels.")

            await category_repo.delete(category_to_delete)
            # Commit should be handled by the controller's session management or context manager
            # await db.commit() 
            logger.info(f"Successfully marked category ID {category_id} for deletion (pending commit).")
            return True

        # Let specific exceptions like InvalidOperation bubble up
        except InvalidOperation as e:
            raise e
        except Exception as e:
            logger.error(f"Error deleting template category ID {category_id}: {e}", exc_info=True)
            await db.rollback() # Rollback on error within this operation
            # Raise a generic exception or return False?
            raise DomainException(f"Failed to delete category {category_id} due to database error.") from e

    async def delete_template_channel(self, db: AsyncSession, channel_id: int) -> bool:
        """Deletes a specific channel from a template database entry."""
        logger.info(f"Service attempting to delete template channel ID: {channel_id}")
        try:
            channel_repo = GuildTemplateChannelRepositoryImpl(db)
            channel_to_delete = await channel_repo.get_by_id(channel_id)

            if not channel_to_delete:
                logger.warning(f"Channel ID {channel_id} not found for deletion.")
                return False # Indicate not found

            await channel_repo.delete(channel_to_delete)
            # Commit should be handled by the controller's session management
            # await db.commit()
            logger.info(f"Successfully marked channel ID {channel_id} for deletion (pending commit).")
            return True

        except Exception as e:
            logger.error(f"Error deleting template channel ID {channel_id}: {e}", exc_info=True)
            await db.rollback()
            raise DomainException(f"Failed to delete channel {channel_id} due to database error.") from e

    # --- NEW Method to get parent template ID ---
    async def get_parent_template_id_for_element(
        self,
        db: AsyncSession,
        element_id: int,
        element_type: str # 'category' or 'channel'
    ) -> Optional[int]:
        """Fetches the parent GuildTemplateEntity ID for a given category or channel ID."""
        logger.debug(f"Fetching parent template ID for {element_type} ID: {element_id}")
        try:
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
    # --- End NEW Method ---

    # --- Method to update template METADATA (name, description etc.) --- 
    async def update_template_metadata(
        self,
        db: AsyncSession,
        template_id: int,
        new_name: str,
        requesting_user: AppUserEntity
        # Add new_description later if needed
    ) -> Optional[Dict[str, Any]]: # Return full updated template data
        """Updates metadata (like name) for a specific template. Checks ownership."""
        logger.info(f"SERVICE: Attempting metadata update for template {template_id} by user {requesting_user.id}. New name: '{new_name}'")

        async with db.begin(): # Use transaction
            # 1. Fetch the template
            result = await db.execute(select(GuildTemplateEntity).where(GuildTemplateEntity.template_id == template_id))
            template = result.scalars().first()

            if not template:
                logger.warning(f"SERVICE: Template {template_id} not found for metadata update.")
                raise TemplateNotFound(f"Template with ID {template_id} not found.")

            # 2. Check Permissions (User must be the creator)
            # TODO: Define permission logic more clearly (e.g., allow admins?)
            if template.creator_user_id != requesting_user.id:
                logger.warning(f"SERVICE: Permission denied. User {requesting_user.id} cannot update metadata for template {template_id} owned by {template.creator_user_id}.")
                raise PermissionDenied("You do not have permission to modify this template.")

            # Cannot modify initial snapshot metadata
            if template.is_initial_snapshot:
                logger.warning(f"SERVICE: Attempted to modify metadata of initial snapshot template {template_id}.")
                raise PermissionDenied("Cannot modify the initial guild snapshot.")

            # 3. Update fields
            template.template_name = new_name
            template.updated_at = datetime.utcnow() # Update timestamp
            # Update description if added later
            
            # Add the updated template back to the session
            db.add(template)

        # Re-fetch the full updated data to return it
        # This ensures categories/channels are included as expected by the response schema
        logger.info(f"SERVICE: Metadata for template {template_id} updated successfully. Re-fetching full data.")
        return await self.get_template_by_id(template_id=template_id)

# Instantiate the service if needed globally (e.g., for factory)
# Or instantiate it where needed
# guild_template_service = GuildTemplateService() 
