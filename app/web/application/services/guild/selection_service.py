"""    
Service responsible for guild selection logic.
"""
from fastapi import Request, HTTPException, status
from app.shared.infrastructure.models.auth import AppUserEntity
from app.shared.infrastructure.models.discord import GuildEntity, DiscordGuildUserEntity
from app.shared.infrastructure.database.session.context import session_context
from app.shared.interfaces.logging.api import get_web_logger
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload # If needed later
from typing import Optional

logger = get_web_logger()

class GuildSelectionService:
    """Handles logic related to selecting the current guild and session management."""

    def __init__(self):
        """Initialize GuildSelectionService."""
        logger.debug("GuildSelectionService initialized.")

    async def get_current_guild(self, request: Request, user: AppUserEntity) -> Optional[GuildEntity]:
        """Get the currently selected guild, prioritizing DB then Session."""
        guild_id_from_db = user.last_selected_guild_id
        session_payload = request.session.get('selected_guild')
        guild_id_from_session = session_payload.get('guild_id') if session_payload else None

        guild_id_to_fetch = None
        # This flag will determine if the session needs an update *after* a successful guild fetch.
        # It's true if DB was the source AND (session was empty OR session had a different guild_id).
        session_needs_update_post_fetch = False

        if guild_id_from_db:
            guild_id_to_fetch = guild_id_from_db
            logger.debug(f"DB preference: last_selected_guild_id {guild_id_to_fetch} for user {user.id}")
            if guild_id_from_db != guild_id_from_session:
                logger.debug(f"Session guild_id ({guild_id_from_session}) differs from DB or is missing. Session will be updated if DB fetch is valid.")
                session_needs_update_post_fetch = True
            else:
                logger.debug(f"Session guild_id ({guild_id_from_session}) matches DB. Session is consistent with DB preference.")
        elif guild_id_from_session:
            guild_id_to_fetch = guild_id_from_session
            logger.debug(f"No DB preference. Using guild_id from session: {guild_id_to_fetch} for user {user.id}")
            # session_needs_update_post_fetch remains False as session is the source and presumed current.
        else:
            logger.debug(f"No guild_id in DB or session for user {user.id}")
            return None

        if not guild_id_to_fetch: # Should be redundant due to logic above, but for safety.
            return None

        logger.debug(f"Attempting to fetch guild {guild_id_to_fetch} from DB for user {user.id}")
        try:
             async with session_context() as session:
                # Fetch the full GuildEntity
                # Verify guild exists and is approved. Check user access only if not owner.
                stmt = (
                    select(GuildEntity)
                    .outerjoin(DiscordGuildUserEntity, DiscordGuildUserEntity.guild_id == GuildEntity.guild_id)
                    .where(GuildEntity.guild_id == guild_id_to_fetch)
                    .where(GuildEntity.access_status == 'approved')
                )
                # If user is not owner, add condition to check their membership via the join
                if not user.is_owner:
                    stmt = stmt.where(DiscordGuildUserEntity.user_id == user.id)

                result = await session.execute(stmt.limit(1))
                guild = result.scalar_one_or_none()

                if not guild:
                     source_info = 'Unknown'
                     if guild_id_from_db == guild_id_to_fetch:
                         source_info = 'DB'
                     elif guild_id_from_session == guild_id_to_fetch:
                         source_info = 'Session'
                     
                     logger.warning(f"Guild {guild_id_to_fetch} (source: {source_info}) not found, not approved, or user {user.id} lost access.")
                     
                     # If the guild_id_to_fetch came from the DB, it's invalid there.
                     if guild_id_from_db == guild_id_to_fetch:
                         try:
                            update_stmt_clear_db = (
                                update(AppUserEntity)
                                .where(AppUserEntity.id == user.id)
                                .values(last_selected_guild_id=None)
                            )
                            await session.execute(update_stmt_clear_db)
                            await session.commit() 
                            user.last_selected_guild_id = None 
                            logger.debug(f"Cleared invalid last_selected_guild_id {guild_id_to_fetch} for user {user.id}")
                         except Exception as db_exc:
                             logger.error(f"Failed to clear invalid last_selected_guild_id for user {user.id}: {db_exc}", exc_info=True)
                             await session.rollback() # Rollback only this clear attempt
                     
                     # If the guild_id_to_fetch was present in session (either as source or matching an invalid DB one), clear it.
                     if guild_id_from_session == guild_id_to_fetch: 
                         if request.session.get('selected_guild'): # Check if it's actually there before popping
                            request.session.pop('selected_guild', None)
                            logger.debug(f"Removed invalid guild {guild_id_to_fetch} from session.")
                     
                     return None

                # If guild is successfully fetched, and session_needs_update_post_fetch is true:
                if session_needs_update_post_fetch and guild:
                    selected_data = {
                        "guild_id": guild.guild_id,
                        "name": guild.name,
                        "icon_url": str(guild.icon_url) if guild.icon_url else None
                    }
                    request.session['selected_guild'] = selected_data
                    logger.info(f"Session updated with guild {guild.guild_id} (from DB preference) for user {user.id}")

                return guild # Return the ORM object
        except Exception as e:
            logger.exception(f"Error fetching current/last guild {guild_id_to_fetch} for user {user.id}: {e}", exc_info=e)
            # Don't raise HTTPException here, let the controller handle it if needed,
            # returning None might be sufficient depending on usage.
            # Consider if clearing session/last_selected is appropriate on general exception
            return None # Indicate failure to retrieve

    async def select_guild(self, request: Request, guild_id: str, user: AppUserEntity) -> GuildEntity:
        """Select a guild, store its basic info in the session, and update user's last selection."""
        logger.info(f"User {user.id} attempting to select guild: {guild_id}")

        try:
            async with session_context() as session:
                # Verify guild exists and is approved. Check user access only if not owner.
                stmt = (
                    select(GuildEntity)
                    # Always OUTER JOIN to potentially check membership for non-owners
                    .join(DiscordGuildUserEntity, DiscordGuildUserEntity.guild_id == GuildEntity.guild_id, isouter=True)
                    .where(GuildEntity.guild_id == guild_id)
                    .where(GuildEntity.access_status == 'approved')
                )
                # If user is not owner, add condition to check their membership via the join
                if not user.is_owner:
                    stmt = stmt.where(DiscordGuildUserEntity.user_id == user.id)

                # Execute the query
                result = await session.execute(stmt.limit(1))
                guild = result.scalar_one_or_none()

                if not guild:
                    logger.warning(f"User {user.id} denied access to select guild {guild_id} (not found, not approved, or no access).")
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this guild")

                # --- Update User's Last Selected Guild ---
                try:
                    # Use SQLAlchemy update for efficiency
                    update_stmt = (
                        update(AppUserEntity)
                        .where(AppUserEntity.id == user.id)
                        .values(last_selected_guild_id=guild.guild_id)
                    )
                    await session.execute(update_stmt)
                    logger.debug(f"Attempting to update last_selected_guild_id for user {user.id} to {guild.guild_id}")
                    # Commit happens at the end of the 'async with' block if no exceptions
                except Exception as db_exc:
                    logger.error(f"Failed to update last_selected_guild_id for user {user.id}: {db_exc}", exc_info=True)
                    await session.rollback() # Rollback the failed update attempt
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save selection preference") from db_exc
                # --- End Update ---

                # Store essential info in session
                selected_data = {
                    "guild_id": guild.guild_id,
                    "name": guild.name,
                    "icon_url": str(guild.icon_url) if guild.icon_url else None
                }
                request.session['selected_guild'] = selected_data
                logger.info(f"Stored selected guild in session for user {user.id}: {selected_data}")

                # Commit both the user update and session changes implicitly by exiting context manager without error
                await session.commit()
                logger.info(f"Successfully updated last_selected_guild_id and session for user {user.id}")

                # Refresh the user object in memory if needed elsewhere in the request lifecycle
                user.last_selected_guild_id = guild.guild_id

                # Return the full GuildEntity object
                return guild

        except HTTPException as http_exc:
            # Assume rollback is handled by the context manager on exception
            # await session.rollback() # Rollback on HTTP exceptions triggered within the block
            raise http_exc
        except Exception as e:
            # Assume rollback is handled by the context manager on exception
            # await session.rollback() # Rollback on general exceptions
            logger.exception(f"Error selecting guild {guild_id} for user {user.id}: {e}", exc_info=e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Guild selection failed")
