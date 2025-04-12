"""
Service responsible for server selection logic within the web application.
"""
from fastapi import Request, HTTPException, status
from app.shared.infrastructure.models.auth import AppUserEntity
# Import necessary DB models and session management
from app.shared.infrastructure.models.discord import GuildEntity, DiscordGuildUserEntity
from app.shared.infrastructure.database.session.context import session_context # Or use the factory approach if preferred
from app.shared.interface.logging.api import get_web_logger
from sqlalchemy import select
from sqlalchemy.orm import selectinload # To potentially load relationships if needed by ServerInfo
from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx # Added httpx import

logger = get_web_logger()

class ServerService:
    """Handles logic related to server selection and session management for servers."""

    def __init__(self):
        """Initialize ServerService."""
        logger.info("ServerService initialized.")
        # In a real application, repositories should be injected here
        # For now, we use the session context directly

    async def get_available_servers(self, user: AppUserEntity) -> List[GuildEntity]: # Return type is now List[GuildEntity]
        """Get list of servers the user has access to (approved status)."""
        logger.debug(f"Fetching available servers for user: {user.id}")
        
        servers: List[GuildEntity] = []
        try:
            async with session_context() as session:
                if user.is_owner:
                    # Owners see all approved servers
                    stmt = (
                        select(GuildEntity)
                        .where(GuildEntity.access_status == 'approved')
                        # Optionally load relationships if needed for ServerInfo conversion
                        # .options(selectinload(GuildEntity.some_relationship))
                        .order_by(GuildEntity.name)
                    )
                    result = await session.execute(stmt)
                    servers = result.scalars().all()
                    logger.info(f"Owner {user.id} has access to {len(servers)} approved servers.")
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
                    servers = result.scalars().all()
                    logger.info(f"User {user.id} has access to {len(servers)} approved servers they are members of.")
            
            # --- DEBUG LOGGING --- 
            logger.debug(f"Returning {len(servers)} servers from ServerService.get_available_servers.")
            for i, s in enumerate(servers):
                # Log type and relevant attributes to check before Pydantic conversion
                logger.debug(f"  Server {i}: Type={type(s)}, ID={getattr(s, 'guild_id', 'N/A')}, Name={getattr(s, 'name', 'N/A')}, Status={getattr(s, 'access_status', 'N/A')}, Icon={getattr(s, 'icon_url', 'N/A')}, Members={getattr(s, 'member_count', 'N/A')}") 
            # --- END DEBUG LOGGING ---

            # The list of GuildEntity objects will be automatically converted 
            # by FastAPI using the ServerInfo response_model with orm_mode=True.
            return servers
            
        except Exception as e:
            logger.exception(f"Error fetching available servers for user {user.id}: {e}", exc_info=e)
            # Let the controller/global handler deal with the exception
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve server list")

    async def get_all_manageable_servers(self, user: AppUserEntity) -> List[GuildEntity]:
        """Get all servers relevant for owner management (all statuses)."""
        logger.debug(f"Fetching all manageable servers for owner: {user.id}")
        if not user.is_owner:
            logger.warning(f"Non-owner {user.id} attempted to fetch all manageable servers.")
            # Return empty list or raise 403 - raising is probably better
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners can view all manageable servers.")

        servers: List[GuildEntity] = []
        try:
            async with session_context() as session:
                # Owners see all servers, ordered by name
                stmt = (
                    select(GuildEntity)
                    # Optionally load relationships needed for display later
                    # .options(selectinload(GuildEntity.config), selectinload(GuildEntity.user_roles))
                    .order_by(GuildEntity.name)
                )
                result = await session.execute(stmt)
                servers = result.scalars().all()
                logger.info(f"Owner {user.id} fetching {len(servers)} total servers for management.")
            return servers
        except Exception as e:
            logger.exception(f"Error fetching all manageable servers for owner {user.id}: {e}", exc_info=e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve manageable server list")

    async def get_current_server(self, request: Request, user: AppUserEntity) -> Optional[GuildEntity]: # Return type can also be GuildEntity
        """Get the currently selected server from the user's session."""
        selected_guild_data = request.session.get('selected_guild')
        if not selected_guild_data or 'guild_id' not in selected_guild_data:
            logger.debug(f"No server selected in session for user {user.id}")
            return None

        guild_id = selected_guild_data['guild_id']
        logger.debug(f"Fetching current server {guild_id} from DB for user {user.id}")
        try:
             async with session_context() as session:
                # Fetch the full GuildEntity to ensure data consistency
                stmt = select(GuildEntity).where(GuildEntity.guild_id == guild_id)
                result = await session.execute(stmt)
                guild = result.scalar_one_or_none()
                if not guild:
                     logger.warning(f"Server {guild_id} from session not found in DB.")
                     # Clear invalid session data?
                     request.session.pop('selected_guild', None)
                     return None
                return guild # Return the ORM object
        except Exception as e:
            logger.exception(f"Error fetching current server {guild_id} for user {user.id}: {e}", exc_info=e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve current server")

    async def select_server(self, request: Request, guild_id: str, user: AppUserEntity) -> GuildEntity: # Return GuildEntity
        """Select a server and store its basic info in the session."""
        logger.info(f"User {user.id} attempting to select server: {guild_id}")
        
        try:
            async with session_context() as session:
                # Verify server exists and is approved. Check user access only if not owner.
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
                server = result.scalar_one_or_none()
                
                if not server:
                    logger.warning(f"User {user.id} denied access to select server {guild_id} (not found, not approved, or no access).")
                    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this server")

                # Store essential info in session
                selected_data = {
                    "guild_id": server.guild_id,
                    "name": server.name,
                    "icon_url": str(server.icon_url) if server.icon_url else None # Ensure icon_url is string or None for session
                }
                request.session['selected_guild'] = selected_data
                logger.info(f"Stored selected server in session for user {user.id}: {selected_data}")
                
                # Return the full GuildEntity object
                return server 
                
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            logger.exception(f"Error selecting server {guild_id} for user {user.id}: {e}", exc_info=e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server selection failed")

    async def update_guild_access_status(self, guild_id: str, new_status: str, reviewed_by_user_id: int) -> GuildEntity:
        """Updates the access status of a specific guild and triggers bot action if approved."""
        logger.info(f"Attempting to update server {guild_id} status to {new_status} by user {reviewed_by_user_id}")
        
        valid_statuses = ['pending', 'approved', 'rejected', 'blocked', 'suspended']
        normalized_new_status = new_status.lower()
        if normalized_new_status not in valid_statuses:
            logger.error(f"Invalid status '{new_status}' provided for server {guild_id}.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status: {new_status}")

        try:
            async with session_context() as session:
                stmt = select(GuildEntity).where(GuildEntity.guild_id == guild_id)
                result = await session.execute(stmt)
                guild = result.scalar_one_or_none()
                
                if not guild:
                    logger.warning(f"Attempted to update status for non-existent server {guild_id}")
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Server not found")
                
                guild.access_status = normalized_new_status
                guild.access_reviewed_at = datetime.utcnow() # Use UTC time
                guild.access_reviewed_by = str(reviewed_by_user_id) # Store user ID as string
                
                await session.commit()
                await session.refresh(guild) # Refresh to get updated data
                
                logger.info(f"Successfully updated server {guild_id} status in DB to {normalized_new_status}")

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
            raise http_exc # Re-raise specific HTTP errors
        except Exception as e:
            logger.exception(f"Database error updating server {guild_id} status: {e}", exc_info=e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database error during status update")

    # --- Placeholder for potential helper --- 
    # async def check_user_guild_access(self, user_id: int, guild_id: str) -> bool:
    #     """Check if user has approved access to the guild."""
    #     # Logic using DiscordGuildUserRepository and/or GuildRepository
    #     return True # Placeholder
