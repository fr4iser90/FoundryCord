from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.web.application.services.auth.dependencies import get_current_user
from app.web.domain.auth.permissions import Role, require_role
from app.shared.interface.logging.api import get_web_logger
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.models.discord.entities import GuildEntity
from sqlalchemy import select
from sqlalchemy.sql import func

logger = get_web_logger()
router = APIRouter(prefix="/owner/servers", tags=["Server Management"])

class ServerManagementController:
    """Controller for server management functionality"""
    
    def __init__(self):
        self.router = router
        self._register_routes()
    
    def _register_routes(self):
        """Register all routes for this controller"""
        self.router.get("")(self.get_servers)
        self.router.post("/add")(self.add_server)
        self.router.get("/{guild_id}/details")(self.get_server_details)
        self.router.post("/{guild_id}/access")(self.update_server_access)
    
    async def get_servers(self, current_user=Depends(get_current_user)):
        """Get all servers with their access status"""
        try:
            await require_role(current_user, Role.OWNER)
            
            async with session_context() as session:
                logger.info("Fetching servers from database...")
                result = await session.execute(select(GuildEntity))
                guilds = result.scalars().all()
                logger.info(f"Found {len(guilds)} guilds in database")
                
                guild_list = []
                for guild in guilds:
                    logger.info(f"Processing guild: {guild.name} (ID: {guild.guild_id}) - Status: {guild.access_status}")
                    guild_list.append({
                        "guild_id": guild.guild_id,
                        "name": guild.name,
                        "access_status": guild.access_status.lower() if guild.access_status else "pending",
                        "member_count": guild.member_count,
                        "joined_at": guild.joined_at,
                        "access_requested_at": guild.access_requested_at,
                        "access_reviewed_at": guild.access_reviewed_at,
                        "access_reviewed_by": guild.access_reviewed_by,
                        "access_notes": guild.access_notes,
                        "icon_url": guild.icon_url,
                        "enable_commands": guild.enable_commands,
                        "enable_logging": guild.enable_logging,
                        "enable_automod": guild.enable_automod,
                        "enable_welcome": guild.enable_welcome
                    })
                
                logger.info(f"Returning {len(guild_list)} guilds")
                return guild_list
                
        except Exception as e:
            logger.error(f"Error getting servers: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def update_server_access(self, guild_id: str, request: Request, current_user=Depends(get_current_user)):
        """Update server access status - Pure database operation"""
        try:
            await require_role(current_user, Role.OWNER)
            
            data = await request.json()
            status = data.get("status")
            notes = data.get("notes")
            
            if not status:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Status is required"
                )
            
            async with session_context() as session:
                result = await session.execute(
                    select(GuildEntity).where(GuildEntity.guild_id == guild_id)
                )
                guild = result.scalar_one_or_none()
                
                if not guild:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Server with ID {guild_id} not found"
                    )
                
                guild.access_status = status
                guild.access_notes = notes
                guild.access_reviewed_at = func.now()
                guild.access_reviewed_by = current_user["id"]
                
                session.add(guild)
                await session.commit()
                
                return {
                    "message": f"Server {guild_id} access updated successfully",
                    "status": status
                }
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating server access: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def get_server_details(self, guild_id: str, current_user=Depends(get_current_user)):
        """Get detailed information about a specific server"""
        try:
            await require_role(current_user, Role.OWNER)
            
            async with session_context() as session:
                result = await session.execute(
                    select(GuildEntity).where(GuildEntity.guild_id == guild_id)
                )
                guild = result.scalar_one_or_none()
                
                if not guild:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Server with ID {guild_id} not found"
                    )
                
                return {
                    "guild_id": guild.guild_id,
                    "name": guild.name,
                    "icon_url": guild.icon_url,
                    "access_status": guild.access_status,
                    "member_count": guild.member_count,
                    "joined_at": guild.joined_at,
                    "access_requested_at": guild.access_requested_at,
                    "access_reviewed_at": guild.access_reviewed_at,
                    "access_reviewed_by": guild.access_reviewed_by,
                    "access_notes": guild.access_notes,
                    "enable_commands": guild.enable_commands,
                    "enable_logging": guild.enable_logging,
                    "enable_automod": guild.enable_automod,
                    "enable_welcome": guild.enable_welcome
                }
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting server details: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def add_server(self, request: Request, current_user=Depends(get_current_user)):
        """Add a new server to the database"""
        try:
            await require_role(current_user, Role.OWNER)
            data = await request.json()
            
            async with session_context() as session:
                guild = GuildEntity(
                    guild_id=data["guild_id"],
                    name=data["name"],
                    access_status="pending",
                    access_requested_at=func.now(),
                    icon_url=data.get("icon_url")
                )
                
                session.add(guild)
                await session.commit()
                
                return {
                    "message": "Server added successfully",
                    "guild_id": guild.guild_id
                }
                
        except Exception as e:
            logger.error(f"Error adding server: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

# Create controller instance
server_management_controller = ServerManagementController()
get_servers = server_management_controller.get_servers
add_server = server_management_controller.add_server
get_server_details = server_management_controller.get_server_details
update_server_access = server_management_controller.update_server_access 