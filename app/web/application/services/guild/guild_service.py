"""
Service responsible for guild selection logic within the web application.
Acts as a Facade, delegating calls to more specific guild services.
"""
from fastapi import Request, HTTPException, status
from app.shared.infrastructure.models.auth import AppUserEntity
# Import necessary DB models and session management
from app.shared.infrastructure.models.discord import GuildEntity, DiscordGuildUserEntity
from app.shared.infrastructure.database.session.context import session_context # Or use the factory approach if preferred
from app.shared.interface.logging.api import get_web_logger
from sqlalchemy import select, update # Import update
from sqlalchemy.orm import selectinload # To potentially load relationships if needed by GuildInfo
from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx # Added httpx import

# Import the specific services
from .query_service import GuildQueryService
from .selection_service import GuildSelectionService
from .management_service import GuildManagementService

logger = get_web_logger()

class GuildService:
    """Facade that delegates guild-related logic to specialized services."""

    def __init__(self):
        """Initialize GuildService and its underlying specific services."""
        # Instantiate the specific services
        # In a production system with dependency injection, these might be injected
        self._query_service = GuildQueryService()
        self._selection_service = GuildSelectionService()
        self._management_service = GuildManagementService()
        logger.info("GuildService Facade initialized, delegating to Query, Selection, and Management services.")

    # --- Query Methods --- 
    async def get_available_guilds(self, user: AppUserEntity) -> List[GuildEntity]:
        """Delegates to GuildQueryService to get available guilds."""
        logger.debug(f"GuildService facade delegating get_available_guilds for user {user.id}")
        return await self._query_service.get_available_guilds(user)

    async def get_all_manageable_guilds(self, user: AppUserEntity) -> List[GuildEntity]:
        """Delegates to GuildQueryService to get all manageable guilds."""
        logger.debug(f"GuildService facade delegating get_all_manageable_guilds for user {user.id}")
        return await self._query_service.get_all_manageable_guilds(user)

    # --- Selection Methods --- 
    async def get_current_guild(self, request: Request, user: AppUserEntity) -> Optional[GuildEntity]:
        """Delegates to GuildSelectionService to get the current guild."""
        logger.debug(f"GuildService facade delegating get_current_guild for user {user.id}")
        return await self._selection_service.get_current_guild(request, user)

    async def select_guild(self, request: Request, guild_id: str, user: AppUserEntity) -> GuildEntity:
        """Delegates to GuildSelectionService to select a guild."""
        logger.debug(f"GuildService facade delegating select_guild for user {user.id}, guild {guild_id}")
        return await self._selection_service.select_guild(request, guild_id, user)

    # --- Management Methods --- 
    async def update_guild_access_status(self, guild_id: str, new_status: str, reviewed_by_user_id: int) -> GuildEntity:
        """Delegates to GuildManagementService to update guild access status."""
        logger.debug(f"GuildService facade delegating update_guild_access_status for guild {guild_id}")
        return await self._management_service.update_guild_access_status(guild_id, new_status, reviewed_by_user_id)

    # --- Placeholder for potential helper --- 
    # async def check_user_guild_access(self, user_id: int, guild_id: str) -> bool:
    #     """Check if user has approved access to the guild."""
    #     # Logic using DiscordGuildUserRepository and/or GuildRepository
    #     return True # Placeholder

