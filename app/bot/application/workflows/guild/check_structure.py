import logging
from typing import Dict, List, Optional
import nextcord
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.models.discord.entities import GuildConfigEntity
from app.shared.domain.repositories.guild_templates import (
    GuildTemplateCategoryPermissionRepository,
    GuildTemplateChannelPermissionRepository
)

logger = get_bot_logger()

async def check_and_create_category(
    discord_guild: nextcord.Guild,
    template_cat, # Template category data
    creation_overwrites: Dict,
    template_name: str,
    session: AsyncSession # Keep session if needed for future DB interactions
) -> Optional[nextcord.CategoryChannel]:
    """Checks if a category with the same name exists, creates it if not.

    Args:
        discord_guild: The target nextcord.Guild object.
        template_cat: The template data for the category.
        creation_overwrites: Prepared permission overwrites.
        template_name: The name of the template being applied (for reason string).
        session: The SQLAlchemy async session.

    Returns:
        The created nextcord.CategoryChannel or None if creation skipped/failed.
    """
    # Check if category with the same name exists anywhere in the guild
    category_with_same_name = nextcord.utils.get(discord_guild.categories, name=template_cat.category_name)

    if category_with_same_name:
        logger.warning(f"[GuildWorkflow]       Category '{template_cat.category_name}' already exists on server (ID: {category_with_same_name.id}). Template likely out of sync. Skipping creation to avoid duplicate.")
        return None # Skip creation

    # --- Proceed with Creation Logic ---
    logger.info(f"[GuildWorkflow]     Category '{template_cat.category_name}' does not appear to exist by name server-wide. Proceeding with creation...")
    try:
        new_discord_cat = await discord_guild.create_category(
            name=template_cat.category_name,
            overwrites=creation_overwrites,
            reason=f"Applying template: {template_name}"
        )
        logger.info(f"[GuildWorkflow]       Successfully created category '{new_discord_cat.name}' (ID: {new_discord_cat.id}) at position {new_discord_cat.position}")
        return new_discord_cat

    except nextcord.Forbidden:
        logger.error(f"[GuildWorkflow]       PERMISSION ERROR: Cannot create category '{template_cat.category_name}'. Check bot permissions.")
    except nextcord.HTTPException as http_err:
        logger.error(f"[GuildWorkflow]       HTTP ERROR creating category '{template_cat.category_name}': {http_err}")
    except Exception as creation_err:
        logger.error(f"[GuildWorkflow]       UNEXPECTED ERROR creating category '{template_cat.category_name}': {creation_err}", exc_info=True)

    return None # Return None if creation failed

async def check_and_create_channel(
    discord_guild: nextcord.Guild,
    template_chan, # The template channel data
    target_discord_category: Optional[nextcord.CategoryChannel],
    creation_overwrites: Dict,
    template_name: str, # For reason string
    session: AsyncSession # Keep session if needed for future DB interactions
) -> Optional[nextcord.abc.GuildChannel]:
    """Checks if a channel with the same name exists, creates it if not, and returns the new channel or None.

    Args:
        discord_guild: The target nextcord.Guild object.
        template_chan: The template data for the channel.
        target_discord_category: The target Discord category object (or None).
        creation_overwrites: Prepared permission overwrites.
        template_name: The name of the template being applied (for reason string).
        session: The SQLAlchemy async session.

    Returns:
        The created nextcord.abc.GuildChannel or None if creation skipped/failed.
    """
    # Check if channel with the same name exists anywhere in the guild
    channel_with_same_name = nextcord.utils.get(discord_guild.channels, name=template_chan.channel_name)

    if channel_with_same_name:
        logger.warning(f"[GuildWorkflow]       Channel '{template_chan.channel_name}' already exists on server (ID: {channel_with_same_name.id}, Category: {channel_with_same_name.category}). Template likely out of sync. Skipping creation to avoid duplicate.")
        # Optionally link existing channel ID back to template_chan in DB here if needed
        # template_chan.discord_channel_id = str(channel_with_same_name.id)
        return None # Skip creation

    # --- Proceed with Creation Logic (moved from apply_template) ---
    logger.info(f"[GuildWorkflow]     Channel '{template_chan.channel_name}' does not appear to exist by name server-wide. Proceeding with creation...")

    creation_kwargs = {
        'name': template_chan.channel_name,
        'category': target_discord_category,
        # 'position': template_chan.position, # Position often less reliable on creation
        'overwrites': creation_overwrites, # Apply permissions now
        'reason': f"Applying template: {template_name}"
    }

    # Determine channel type and creator function
    channel_creator = None
    if template_chan.channel_type == 'text':
        creation_kwargs.update({
            'topic': template_chan.topic,
            'slowmode_delay': template_chan.slowmode_delay,
            'nsfw': template_chan.is_nsfw
        })
        channel_creator = discord_guild.create_text_channel
    elif template_chan.channel_type == 'voice':
        creation_kwargs.update({
            # Add bitrate, user_limit if stored in template
        })
        channel_creator = discord_guild.create_voice_channel
    elif template_chan.channel_type == 'stage_voice':
        creation_kwargs.update({
            # Add stage specific args if needed
        })
        channel_creator = discord_guild.create_stage_channel
    elif template_chan.channel_type == 'forum':
        creation_kwargs.update({
            'topic': template_chan.topic,
            # 'slowmode_delay': template_chan.slowmode_delay, # Check API if applicable
            'nsfw': template_chan.is_nsfw
            # Add tags etc. if stored in template
        })
        channel_creator = discord_guild.create_forum
    else:
        logger.error(f"[GuildWorkflow]       Unsupported channel type '{template_chan.channel_type}' in template. Cannot create.")
        return None # Skip this channel

    # Create the channel
    try:
        new_discord_chan = await channel_creator(**creation_kwargs)
        logger.info(f"[GuildWorkflow]       Successfully created {template_chan.channel_type} channel '{new_discord_chan.name}' (ID: {new_discord_chan.id})")
        return new_discord_chan # Return the created channel object

    except nextcord.Forbidden:
        logger.error(f"[GuildWorkflow]       PERMISSION ERROR: Cannot create {template_chan.channel_type} channel '{template_chan.channel_name}'. Check bot permissions.")
    except nextcord.HTTPException as http_err:
        logger.error(f"[GuildWorkflow]       HTTP ERROR creating {template_chan.channel_type} channel '{template_chan.channel_name}': {http_err}")
    except Exception as creation_err:
        logger.error(f"[GuildWorkflow]       UNEXPECTED ERROR creating {template_chan.channel_type} channel '{template_chan.channel_name}': {creation_err}", exc_info=True)

    return None # Return None if creation failed
