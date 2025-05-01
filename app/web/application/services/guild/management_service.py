"""
Service responsible for guild management actions.
"""
from fastapi import HTTPException, status
from app.shared.infrastructure.models.auth import AppUserEntity
from app.shared.infrastructure.models.discord import GuildEntity
from app.shared.infrastructure.database.session.context import session_context
from app.shared.interface.logging.api import get_web_logger
from sqlalchemy import select, update
from datetime import datetime
import httpx

logger = get_web_logger()

class GuildManagementService:
    """Handles administrative actions related to guilds."""

    def __init__(self):
        """Initialize GuildManagementService."""
        logger.info("GuildManagementService initialized.")

    async def update_guild_access_status(self, guild_id: str, new_status: str, reviewed_by_user_id: int) -> GuildEntity:
        """Updates the access status of a specific guild and triggers bot action if approved."""
        logger.info(f"Attempting to update guild {guild_id} status to {new_status} by user {reviewed_by_user_id}")

        valid_statuses = ['pending', 'approved', 'rejected', 'blocked', 'suspended']
        normalized_new_status = new_status.lower()
        if normalized_new_status not in valid_statuses:
            logger.error(f"Invalid status '{new_status}' provided for guild {guild_id}.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status: {new_status}")

        try:
            async with session_context() as session:
                stmt = select(GuildEntity).where(GuildEntity.guild_id == guild_id)
                result = await session.execute(stmt)
                guild = result.scalar_one_or_none()

                if not guild:
                    logger.warning(f"Attempted to update status for non-existent guild {guild_id}")
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guild not found")

                guild.access_status = normalized_new_status
                guild.access_reviewed_at = datetime.utcnow() # Use UTC time
                guild.access_reviewed_by = str(reviewed_by_user_id) # Store user ID as string

                await session.commit()
                await session.refresh(guild) # Refresh to get updated data

                logger.info(f"Successfully updated guild {guild_id} status in DB to {normalized_new_status}")

                # --- Trigger Bot Action --- 
                if normalized_new_status == 'approved':
                    logger.info(f"Status updated to approved. Triggering bot's approve_guild workflow for {guild_id} via internal API...")
                    # Define the internal API endpoint URL
                    # TODO: Move this URL to a configuration file/environment variable
                    internal_api_url = f"http://foundrycord-bot:9090/internal/trigger/approve_guild/{guild_id}"

                    try:
                        async with httpx.AsyncClient() as client:
                            response = await client.post(internal_api_url, timeout=10.0) # Added timeout
                            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

                            # Log success based on status code
                            logger.info(f"Internal API call to trigger approve_guild for {guild_id} succeeded with status {response.status_code}.")
                            # Optionally check response content if the API returns data
                            # bot_result = response.json()
                            # logger.info(f"Bot response: {bot_result}")

                    except httpx.HTTPStatusError as http_err:
                        # Error from the bot API itself (e.g., 404, 500)
                        logger.error(f"HTTP error occurred when calling internal API for guild {guild_id}: {http_err}", exc_info=True)
                        # Decide if this should fail the web request or just log. For now, just log.
                    except httpx.RequestError as req_err:
                        # Error during the request (e.g., connection error, timeout)
                        logger.error(f"Request error occurred when calling internal API for guild {guild_id}: {req_err}", exc_info=True)
                        # Decide if this should fail the web request or just log. For now, just log.
                    except Exception as e:
                        # Catch any other unexpected errors during the API call
                        logger.error(f"An unexpected error occurred during the internal API call for guild {guild_id}: {e}", exc_info=True)
                        # Decide if this should fail the web request or just log. For now, just log.
                    finally:
                        logger.info(f"Finished attempt to trigger approve_guild via internal API for guild {guild_id}.")
                # --- End Bot Action ---

                return guild

        except HTTPException as http_exc:
            # Rollback likely handled by context manager on exception
            raise http_exc # Re-raise specific HTTP errors
        except Exception as e:
            # Rollback likely handled by context manager on exception
            logger.exception(f"Database error updating guild {guild_id} status: {e}", exc_info=e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error during status update")
