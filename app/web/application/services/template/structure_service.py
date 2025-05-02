"""
Service responsible for modifying template structure.
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, update, delete

from app.shared.infrastructure.database.session.context import session_context
from app.shared.interface.logging.api import get_web_logger
# Import Template Repositories & Entities
from app.shared.infrastructure.repositories.guild_templates import (
    GuildTemplateRepositoryImpl,
    GuildTemplateCategoryRepositoryImpl,
    GuildTemplateChannelRepositoryImpl,
)
from app.shared.infrastructure.models.guild_templates import (
    GuildTemplateEntity,
    GuildTemplateCategoryEntity,
    GuildTemplateChannelEntity,
)
# Import Schemas
from app.web.interfaces.api.rest.v1.schemas.guild_template_schemas import GuildStructureUpdatePayload, GuildStructureTemplateCreateFromStructure, PropertyChangeValue
# Import Exceptions
from app.shared.domain.exceptions import TemplateNotFound, PermissionDenied, DomainException
# Import User Entity for permission checks
from app.shared.infrastructure.models.auth import AppUserEntity
# Import Config Repo
from app.shared.infrastructure.repositories.discord import GuildConfigRepositoryImpl

logger = get_web_logger()

class TemplateStructureService:
    """Handles logic related to creating and updating the structure of templates."""

    def __init__(self):
        """Initialize TemplateStructureService."""
        logger.info("TemplateStructureService initialized.")
        # Repositories are typically instantiated per request/session

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

        # Note: This method uses the passed 'db' session directly.
        template_repo = GuildTemplateRepositoryImpl(db)
        category_repo = GuildTemplateCategoryRepositoryImpl(db)
        channel_repo = GuildTemplateChannelRepositoryImpl(db)

        # --- 1. Permission Check --- 
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

        # --- 2. Fetch Existing Structure --- 
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
        incoming_nodes_data = {} # Map DB ID -> { id_str, parent_id_str, position, name, channel_type? }

        for node_data in structure_payload.nodes:
            node_id_str = node_data.id
            item_db_id = None

            if node_id_str.startswith("category_"):
                try: item_db_id = int(node_id_str.split("_")[1])
                except (IndexError, ValueError): continue
                if item_db_id in existing_cat_dbids:
                     incoming_cat_dbids.add(item_db_id)
                     incoming_nodes_data[item_db_id] = node_data
                else:
                     logger.warning(f"Incoming node {node_id_str} does not match an existing category in template {template_id}. Ignoring.")

            elif node_id_str.startswith("channel_"):
                try: item_db_id = int(node_id_str.split("_")[1])
                except (IndexError, ValueError): continue
                if item_db_id in existing_chan_dbids:
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
        # --- 5a. Process Property Changes --- 
        if structure_payload.property_changes:
             logger.info(f"Processing {len(structure_payload.property_changes)} nodes with property changes for template {template_id}")
             for node_key, changes_data in structure_payload.property_changes.items():
                 try:
                     # Parse the node key
                     item_type, item_db_id_str = node_key.split('_')
                     item_db_id = int(item_db_id_str)

                     # Validate changes data using Pydantic model
                     try:
                         changes = PropertyChangeValue.model_validate(changes_data)
                     except Exception as validation_error:
                         logger.warning(f"Invalid property change data for node '{node_key}': {validation_error}. Skipping changes: {changes_data}")
                         continue
                     
                     target_entity = None
                     if item_type == 'category' and item_db_id in existing_cats_by_dbid:
                         target_entity = existing_cats_by_dbid[item_db_id]
                     elif item_type == 'channel' and item_db_id in existing_chans_by_dbid:
                          target_entity = existing_chans_by_dbid[item_db_id]
                     
                     if target_entity:
                         logger.debug(f"Applying property changes to {item_type} ID {item_db_id}: {changes}")
                         update_applied = False
                         
                         # --- Process standard properties (name, topic, etc.) ---
                         for prop_name, new_value in changes.model_dump(exclude_unset=True).items():
                             entity_attr_name = prop_name
                             # --- Field Name Mapping ---
                             if item_type == 'category':
                                 if prop_name == 'name': entity_attr_name = 'category_name'
                                 # Add other category field mappings if needed
                             elif item_type == 'channel':
                                 if prop_name == 'name': entity_attr_name = 'channel_name'
                                 # elif prop_name == 'is_dashboard_enabled': entity_attr_name = 'is_dashboard_enabled' # Direct mapping
                                 # elif prop_name == 'dashboard_types': entity_attr_name = 'dashboard_types' # Direct mapping
                             # --------------------------
                             
                             if hasattr(target_entity, entity_attr_name):
                                 current_value = getattr(target_entity, entity_attr_name)
                                 try:
                                     # Determine expected type (handle None)
                                     expected_type = type(current_value) if current_value is not None else None 
                                     # If expected_type is still None, try to infer from attr name
                                     if expected_type is None:
                                         # --- REMOVE mirror field from inference --- 
                                         # if entity_attr_name in ['is_nsfw', 'mirror_dashboard_in_followers']:
                                         if entity_attr_name in ['is_nsfw']: 
                                         # ----------------------------------------
                                             expected_type = bool
                                         elif entity_attr_name in ['slowmode_delay']: 
                                             expected_type = int
                                         # --- ADD: Expected type for dashboard_types ---
                                         elif entity_attr_name == 'dashboard_types':
                                             expected_type = list
                                         else:
                                             expected_type = str # Default guess
                                             
                                     # --- Type Casting Logic --- 
                                     casted_value = None
                                     # Special handling for bool from JS strings or bools
                                     if expected_type is bool and isinstance(new_value, (str, bool)):
                                         if isinstance(new_value, bool):
                                             casted_value = new_value
                                         else:
                                             casted_value = new_value.lower() == 'true'
                                     # Special handling for int/float that might come as strings
                                     elif expected_type is int and isinstance(new_value, (str, bool, int)):
                                         casted_value = int(new_value) if str(new_value).strip() else None
                                     elif expected_type is float and isinstance(new_value, (str, bool, int)):
                                         casted_value = float(new_value)
                                     # Generic cast for other types, handling potential None
                                     elif new_value is None:
                                         casted_value = None
                                     # --- ADD: Handle list type directly ---
                                     elif expected_type is list and isinstance(new_value, list):
                                         casted_value = new_value # Assume it's already a list of strings from JSON
                                     # -------------------------------------
                                     else:
                                         casted_value = expected_type(new_value)
                                     # --- End Type Casting ---
                                     
                                     if current_value != casted_value:
                                          logger.debug(f"  Updating {entity_attr_name} from '{current_value}' ({type(current_value).__name__}) to '{casted_value}' ({type(casted_value).__name__})")
                                          setattr(target_entity, entity_attr_name, casted_value)
                                          update_applied = True
                                     else:
                                          logger.debug(f"  Skipping {entity_attr_name}: Value '{current_value}' already matches new value '{casted_value}'")
                                 except (ValueError, TypeError) as cast_err:
                                      logger.warning(f"  Could not apply change for {entity_attr_name}: Failed to cast new value '{new_value}' to expected type {expected_type}. Error: {cast_err}")
                             else:
                                 logger.warning(f"  Property '{prop_name}' (mapped to '{entity_attr_name}') not found on {item_type} entity ID {item_db_id}. Skipping.")
                         # --- End standard properties --- 
                         
                         # Add entity to update list if any property changed
                         if update_applied and target_entity not in items_to_update:
                             items_to_update.append(target_entity)
                     else:
                         logger.warning(f"Node key '{node_key}' in property changes refers to a non-existent or mismatched item. Skipping changes: {changes_data}")

                 except (ValueError, IndexError) as e:
                     logger.warning(f"Could not parse node key '{node_key}' from property changes payload: {e}. Skipping changes: {changes_data}")
        # --- End Property Changes --- 

        # Update existing categories (position)
        for cat_dbid in incoming_cat_dbids:
            category = existing_cats_by_dbid[cat_dbid]
            node_data = incoming_nodes_data[cat_dbid]
            if category.position != node_data.position:
                logger.debug(f"Updating category {cat_dbid} position from {category.position} to {node_data.position}")
                category.position = node_data.position
                if category not in items_to_update: items_to_update.append(category)

        # Update existing channels (position, parent)
        for chan_dbid in incoming_chan_dbids:
            channel = existing_chans_by_dbid[chan_dbid]
            node_data = incoming_nodes_data[chan_dbid]
            needs_update = False

            if channel.position != node_data.position:
                logger.debug(f"Updating channel {chan_dbid} position from {channel.position} to {node_data.position}")
                channel.position = node_data.position
                needs_update = True

            new_parent_db_id: Optional[int] = None
            parent_id_str = node_data.parent_id
            if parent_id_str and parent_id_str.startswith("category_"):
                try:
                    potential_parent_dbid = int(parent_id_str.split("_")[1])
                    if potential_parent_dbid in incoming_cat_dbids:
                         new_parent_db_id = potential_parent_dbid
                    else:
                         logger.warning(f"Channel {chan_dbid} requested parent {parent_id_str} which is being deleted or wasn't found. Setting parent to NULL.")
                except (IndexError, ValueError):
                    logger.warning(f"Channel {chan_dbid} has invalid parent ID format {parent_id_str}. Setting parent to NULL.")

            if channel.parent_category_template_id != new_parent_db_id:
                logger.debug(f"Updating channel {chan_dbid} parent from {channel.parent_category_template_id} to {new_parent_db_id}")
                channel.parent_category_template_id = new_parent_db_id
                needs_update = True

            if needs_update and channel not in items_to_update:
                items_to_update.append(channel)

        # --- 6. Perform Deletions --- 
        if cats_to_delete_ids:
             logger.info(f"Deleting {len(cats_to_delete_ids)} categories from template {template_id}: {cats_to_delete_ids}")
             delete_cat_stmt = delete(GuildTemplateCategoryEntity).where(GuildTemplateCategoryEntity.id.in_(cats_to_delete_ids))
             await db.execute(delete_cat_stmt)

        if chans_to_delete_ids:
             logger.info(f"Deleting {len(chans_to_delete_ids)} channels from template {template_id}: {chans_to_delete_ids}")
             delete_chan_stmt = delete(GuildTemplateChannelEntity).where(GuildTemplateChannelEntity.id.in_(chans_to_delete_ids))
             await db.execute(delete_chan_stmt)

        # --- 7. Commit Changes --- 
        if items_to_update or cats_to_delete_ids or chans_to_delete_ids:
            try:
                if items_to_update:
                     logger.info(f"Committing updates for {len(items_to_update)} items in template {template_id}")
                     db.add_all(items_to_update) # Add updated items
                
                await db.commit()
                logger.info(f"Successfully committed structure updates for template {template_id}")
            except Exception as e:
                logger.error(f"Database error committing structure updates for template {template_id}: {e}", exc_info=True)
                await db.rollback()
                raise DomainException(f"Failed to save structure updates due to database error.") from e
        else:
            logger.info(f"No structure changes detected for template {template_id}. Nothing to commit.")

        # --- 8. Return Updated Template AND Config Flag --- 
        logger.info(f"Re-fetching updated template {template_id} with eager loading.")
        try:
            stmt = (
                select(GuildTemplateEntity)
                .options(
                    selectinload(GuildTemplateEntity.categories)
                    .selectinload(GuildTemplateCategoryEntity.permissions),
                    selectinload(GuildTemplateEntity.channels)
                    .selectinload(GuildTemplateChannelEntity.permissions),
                )
                .where(GuildTemplateEntity.id == template_id)
            )
            result = await db.execute(stmt)
            updated_template_entity = result.scalar_one_or_none()

            if not updated_template_entity:
                logger.error(f"Failed to re-fetch template {template_id} after update.")
                raise DomainException(f"Failed to retrieve updated template data for template ID {template_id}.")

            logger.info(f"Successfully re-fetched template {template_id}.")

            delete_unmanaged_flag = False
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

            return {
                "template_entity": updated_template_entity,
                "delete_unmanaged": delete_unmanaged_flag
            }

        except Exception as fetch_err:
            logger.error(f"Error re-fetching template {template_id} or its config after update: {fetch_err}", exc_info=True)
            raise DomainException(f"Failed to retrieve complete updated template data or config: {fetch_err}") from fetch_err

    async def create_template_from_structure(
        self,
        db: AsyncSession,
        creator_user_id: int,
        payload: GuildStructureTemplateCreateFromStructure
    ) -> GuildTemplateEntity:
        """Creates a new template entity based on name, description, and a structure payload."""
        logger.info(f"Attempting to create template '{payload.new_template_name}' from structure for user {creator_user_id}")

        session = db # Use passed session
        template_repo = GuildTemplateRepositoryImpl(session)
        category_repo = GuildTemplateCategoryRepositoryImpl(session)
        channel_repo = GuildTemplateChannelRepositoryImpl(session)

        existing_by_name = await template_repo.get_by_name_and_creator(payload.new_template_name, creator_user_id)
        if existing_by_name:
             logger.warning(f"Template name '{payload.new_template_name}' already exists for user {creator_user_id}. Cannot create.")
             raise ValueError(f"You already have a template named '{payload.new_template_name}'.")

        new_template = GuildTemplateEntity(
            template_name=payload.new_template_name,
            template_description=payload.new_template_description,
            creator_user_id=creator_user_id,
            is_shared=False,
        )
        session.add(new_template)
        try:
            await session.flush()
            await session.refresh(new_template)
            logger.info(f"Flushed new template '{new_template.template_name}'. Assigned ID: {new_template.id}")
        except Exception as e:
            logger.error(f"Database error flushing new template '{payload.new_template_name}': {e}", exc_info=True)
            await session.rollback()
            raise ValueError(f"Could not save initial template record: {e}")

        created_categories_map = {}
        nodes_to_create = []

        for node_data in payload.structure.nodes:
            if node_data.id.startswith("category_"):
                category_name = node_data.name if node_data.name else f"Category {node_data.id}"
                logger.debug(f"Preparing category: ID={node_data.id}, Name='{category_name}', Pos={node_data.position}")
                new_category = GuildTemplateCategoryEntity(
                    guild_template_id=new_template.id,
                    category_name=category_name,
                    position=node_data.position
                )
                created_categories_map[node_data.id] = new_category
                nodes_to_create.append(new_category)

        if nodes_to_create:
            session.add_all(nodes_to_create)
            try:
                await session.flush()
                logger.info(f"Flushed {len(created_categories_map)} new categories for template {new_template.id}")
                for js_id, cat_entity in created_categories_map.items():
                    await session.refresh(cat_entity)
                    logger.debug(f"Refreshed category '{cat_entity.category_name}' (jsID: {js_id}), got DB ID: {cat_entity.id}")
            except Exception as e:
                logger.error(f"Database error flushing categories for template {new_template.id}: {e}", exc_info=True)
                await session.rollback()
                raise ValueError(f"Could not save categories: {e}")
            nodes_to_create.clear()

        for node_data in payload.structure.nodes:
            if node_data.id.startswith("channel_"):
                parent_category_db_id: Optional[int] = None
                parent_js_id = node_data.parent_id
                logger.debug(f"Processing Channel Node: ID={node_data.id}, PayloadParentID='{parent_js_id}'")

                if parent_js_id and parent_js_id.startswith("category_"):
                    parent_category_entity = created_categories_map.get(parent_js_id)
                    if parent_category_entity:
                        parent_category_db_id = parent_category_entity.id
                        logger.debug(f"  Found parent category entity in map. Extracted DB ID: {parent_category_db_id} (from Entity: {parent_category_entity})")
                    else:
                        logger.warning(f"  Parent category entity NOT FOUND in map for key '{parent_js_id}'. Setting DB Parent ID to NULL.")
                elif parent_js_id and parent_js_id.startswith("template_"):
                    logger.debug(f"  Parent is template root ('{parent_js_id}'). Setting DB Parent ID to NULL.")
                else:
                    logger.warning(f"  Unrecognized or missing parent ID '{parent_js_id}'. Setting DB Parent ID to NULL.")
                
                channel_name = node_data.name if node_data.name else f"Channel {node_data.id}"
                channel_type = node_data.channel_type if node_data.channel_type else "text"
                logger.debug(f"  Final assignment: Name='{channel_name}', Type='{channel_type}', ParentDBID={parent_category_db_id}, Pos={node_data.position}")

                new_channel = GuildTemplateChannelEntity(
                    guild_template_id=new_template.id,
                    channel_name=channel_name,
                    channel_type=channel_type,
                    position=node_data.position,
                    parent_category_template_id=parent_category_db_id,
                    topic=node_data.topic if hasattr(node_data, 'topic') else None,
                    is_nsfw=node_data.is_nsfw if hasattr(node_data, 'is_nsfw') else False,
                    slowmode_delay=node_data.slowmode_delay if hasattr(node_data, 'slowmode_delay') else 0
                )
                nodes_to_create.append(new_channel)

        if nodes_to_create:
            session.add_all(nodes_to_create)
            try:
                await session.flush()
                logger.info(f"Flushed {len(nodes_to_create)} new channels for template {new_template.id}")
            except Exception as e:
                logger.error(f"Database error flushing channels for template {new_template.id}: {e}", exc_info=True)
                await session.rollback()
                raise ValueError(f"Could not save channels: {e}")

        try:
            await session.commit()
            logger.info(f"Successfully committed new template '{new_template.template_name}' (ID: {new_template.id}) and its structure.")
            await session.refresh(new_template, attribute_names=['categories', 'channels'])
            return new_template
        except Exception as e:
            logger.error(f"Database error committing new template {new_template.id}: {e}", exc_info=True)
            await session.rollback()
            raise ValueError(f"Failed to commit new template: {e}") 