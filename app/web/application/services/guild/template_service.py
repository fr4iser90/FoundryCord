from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, and_, or_

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

# Instantiate the service if needed globally (e.g., for factory)
# Or instantiate it where needed
# guild_template_service = GuildTemplateService() 
