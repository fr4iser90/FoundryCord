# app/bot/core/workflows/guild/__init__.py
import logging
from typing import Dict, Optional

from app.bot.core.workflows.base_workflow import BaseWorkflow, WorkflowStatus
from app.bot.core.workflows.database_workflow import DatabaseWorkflow
from app.shared.interface.logging.api import get_bot_logger

# Import methods from other files within this directory
from .initialization import initialize
from .sync import on_guild_join, initialize_for_guild, sync_guild
from .approval import approve_guild, deny_guild, enforce_access_control, get_guild_access_status
from .template_application import apply_template, _prepare_permission_overwrites, _apply_category_permissions, _apply_channel_permissions
from .state import get_guild_status, disable_for_guild, cleanup_guild, cleanup

from .check_structure import check_and_create_category as _check_and_create_category
from .check_structure import check_and_create_channel as _check_and_create_channel

# Import constants from approval
from .approval import ACCESS_PENDING, ACCESS_APPROVED, ACCESS_REJECTED, ACCESS_SUSPENDED

logger = get_bot_logger()

class GuildWorkflow(BaseWorkflow):
    """Manages guild-related operations and synchronization"""
    
    def __init__(self, database_workflow: DatabaseWorkflow, bot):
        super().__init__("guild")
        self.bot = bot
        self.database_workflow = database_workflow
        self.requires_guild_approval = True
        self._guild_statuses: Dict[str, WorkflowStatus] = {}
        self._guild_access_statuses: Dict[str, str] = {}
        self.guild_repo = None
        self.guild_config_repo = None
        
        # Add database dependency
        self.add_dependency("database")

    # Assign methods from imported files
    initialize = initialize
    on_guild_join = on_guild_join
    initialize_for_guild = initialize_for_guild
    sync_guild = sync_guild
    approve_guild = approve_guild
    deny_guild = deny_guild
    enforce_access_control = enforce_access_control
    get_guild_access_status = get_guild_access_status
    apply_template = apply_template
    _prepare_permission_overwrites = _prepare_permission_overwrites
    _apply_category_permissions = _apply_category_permissions
    _apply_channel_permissions = _apply_channel_permissions
    get_guild_status = get_guild_status
    disable_for_guild = disable_for_guild
    cleanup_guild = cleanup_guild
    cleanup = cleanup
    
    # Assign check_structure functions as static methods
    @staticmethod
    async def check_and_create_category(discord_guild, template_cat, creation_overwrites, template_name, session):
        return await _check_and_create_category(discord_guild, template_cat, creation_overwrites, template_name, session)
        
    @staticmethod
    async def check_and_create_channel(discord_guild, template_chan, target_discord_category, creation_overwrites, template_name, session):
        return await _check_and_create_channel(discord_guild, template_chan, target_discord_category, creation_overwrites, template_name, session)

    # Make constants accessible if needed (optional)
    ACCESS_PENDING = ACCESS_PENDING
    ACCESS_APPROVED = ACCESS_APPROVED
    ACCESS_REJECTED = ACCESS_REJECTED
    ACCESS_SUSPENDED = ACCESS_SUSPENDED 