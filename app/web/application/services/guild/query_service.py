"""
Service responsible for querying guild information.
"""
from fastapi import HTTPException, status
from app.shared.infrastructure.models.auth import AppUserEntity
from app.shared.infrastructure.models.discord import GuildEntity, DiscordGuildUserEntity
from app.shared.infrastructure.database.session.context import session_context
from app.shared.interface.logging.api import get_web_logger
from sqlalchemy import select
from sqlalchemy.orm import selectinload # If needed later for relationships
from typing import List

logger = get_web_logger()

class GuildQueryService:
    """Handles logic related to querying guild information."""

    def __init__(self):
        """Initialize GuildQueryService."""
        # Dependencies like repositories would be injected here in a full implementation
        logger.info("GuildQueryService initialized.")

    async def get_available_guilds(self, user: AppUserEntity) -> List[GuildEntity]:
        """Get list of guilds the user has access to (approved status)."""
        logger.debug(f"Fetching available guilds for user: {user.id}")

        guilds: List[GuildEntity] = []
        try:
            async with session_context() as session:
                if user.is_owner:
                    # Owners see all approved guilds
                    stmt = (
                        select(GuildEntity)
                        .where(GuildEntity.access_status == 'approved')
                        # Optionally load relationships if needed for GuildInfo conversion
                        # .options(selectinload(GuildEntity.some_relationship))
                        .order_by(GuildEntity.name)
                    )
                    result = await session.execute(stmt)
                    guilds = result.scalars().all()
                    logger.info(f"Owner {user.id} has access to {len(guilds)} approved guilds.")
                else:
                    # Non-owners: Find guilds they are associated with AND are approved
                    # We need to join AppUser -> DiscordGuildUserEntity -> GuildEntity
                    stmt = (
                        select(GuildEntity)
                        .join(DiscordGuildUserEntity, DiscordGuildUserEntity.guild_id == GuildEntity.guild_id)
                        .where(DiscordGuildUserEntity.user_id == user.id)
                        .where(GuildEntity.access_status == 'approved')
                        # Optionally load relationships
                        .order_by(GuildEntity.name)
                        # Use distinct() to avoid duplicates if a user has multiple roles in one guild (rare)
                        .distinct()
                    )
                    result = await session.execute(stmt)
                    guilds = result.scalars().all()
                    logger.info(f"User {user.id} has access to {len(guilds)} approved guilds they are members of.")

            # --- DEBUG LOGGING ---
            logger.debug(f"Returning {len(guilds)} guilds from GuildQueryService.get_available_guilds.")
            for i, g in enumerate(guilds):
                # Log type and relevant attributes to check before Pydantic conversion
                logger.debug(f"  Guild {i}: Type={type(g)}, ID={getattr(g, 'guild_id', 'N/A')}, Name={getattr(g, 'name', 'N/A')}, Status={getattr(g, 'access_status', 'N/A')}, Icon={getattr(g, 'icon_url', 'N/A')}, Members={getattr(g, 'member_count', 'N/A')}")
            # --- END DEBUG LOGGING ---

            # The list of GuildEntity objects will be automatically converted
            # by FastAPI using the GuildInfo response_model with orm_mode=True.
            return guilds

        except Exception as e:
            logger.exception(f"Error fetching available guilds for user {user.id}: {e}", exc_info=e)
            # Let the controller/global handler deal with the exception
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve guild list")

    async def get_all_manageable_guilds(self, user: AppUserEntity) -> List[GuildEntity]:
        """Get all guilds relevant for owner management (all statuses)."""
        logger.debug(f"Fetching all manageable guilds for owner: {user.id}")
        if not user.is_owner:
            logger.warning(f"Non-owner {user.id} attempted to fetch all manageable guilds.")
            # Return empty list or raise 403 - raising is probably better
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners can view all manageable guilds.")

        guilds: List[GuildEntity] = []
        try:
            async with session_context() as session:
                # Owners see all guilds, ordered by name
                stmt = (
                    select(GuildEntity)
                    # Optionally load relationships needed for display later
                    # .options(selectinload(GuildEntity.config), selectinload(GuildEntity.user_roles))
                    .order_by(GuildEntity.name)
                )
                result = await session.execute(stmt)
                guilds = result.scalars().all()
                logger.info(f"Owner {user.id} fetching {len(guilds)} total guilds for management.")
            return guilds
        except Exception as e:
            logger.exception(f"Error fetching all manageable guilds for owner {user.id}: {e}", exc_info=e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve manageable guild list")
