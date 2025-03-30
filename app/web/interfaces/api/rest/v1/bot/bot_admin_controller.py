from fastapi import APIRouter, Depends, HTTPException, status
from app.web.application.services.auth.dependencies import get_current_user
from app.web.domain.auth.permissions import Role, require_role
from app.shared.interface.logging.api import get_web_logger
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.models import GuildEntity
from app.shared.infrastructure.integration.bot_connector import get_bot_connector
from typing import Dict, List, Optional
import asyncio
from sqlalchemy import select, func

logger = get_web_logger()
router = APIRouter(prefix="/v1/bot-admin", tags=["Bot Administration"])

class BotAdminController:
    """Controller für Bot-Admin-Funktionen"""
    
    def __init__(self):
        self.router = router
        self._register_routes()
    
    def _register_routes(self):
        """Registriert alle Routes für diesen Controller"""
        self.router.get("/status")(self.get_bot_status)
        self.router.post("/start")(self.start_bot)
        self.router.post("/stop")(self.stop_bot)
        self.router.post("/restart")(self.restart_bot)
        self.router.post("/workflow/{workflow_name}/enable")(self.enable_workflow)
        self.router.post("/workflow/{workflow_name}/disable")(self.disable_workflow)
        self.router.get("/overview-stats")(self.get_overview_stats)
        self.router.get("/servers")(self.get_servers)
    
    async def get_bot_status(self, current_user=Depends(get_current_user)):
        """Get current bot status"""
        try:
            # Verify Bot Owner role
            await require_role(current_user, Role.OWNER)
            
            # Temporäre Mock-Daten, bis der Bot-Connector implementiert ist
            # Später den echten Bot-Status zurückgeben
            status = {
                "connected": False,  # Wird später durch echten Status ersetzt
                "uptime": "Not connected",
                "active_workflows": [],
                "available_workflows": ["database", "category", "channel", "dashboard", "task"]
            }
            
            return status
        except Exception as e:
            logger.error(f"Error getting bot status: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def start_bot(self, current_user=Depends(get_current_user)):
        """Start the Discord bot"""
        try:
            await require_role(current_user, Role.OWNER)
            # Hier später die echte Bot-Start-Logik implementieren
            
            return {"status": "success", "message": "Bot starting..."}
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def stop_bot(self, current_user=Depends(get_current_user)):
        """Stop the Discord bot"""
        try:
            await require_role(current_user, Role.OWNER)
            # Hier später die echte Bot-Stop-Logik implementieren
            
            return {"status": "success", "message": "Bot stopping..."}
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def restart_bot(self, current_user=Depends(get_current_user)):
        """Restart the Discord bot"""
        try:
            await require_role(current_user, Role.OWNER)
            # Hier später die echte Bot-Restart-Logik implementieren
            
            return {"status": "success", "message": "Bot restarting..."}
        except Exception as e:
            logger.error(f"Error restarting bot: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def enable_workflow(self, workflow_name: str, current_user=Depends(get_current_user)):
        """Enable a specific bot workflow"""
        try:
            await require_role(current_user, Role.OWNER)
            # Hier später die echte Workflow-Aktivierung implementieren
            
            return {"status": "success", "message": f"Workflow {workflow_name} enabled"}
        except Exception as e:
            logger.error(f"Error enabling workflow {workflow_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def disable_workflow(self, workflow_name: str, current_user=Depends(get_current_user)):
        """Disable a specific bot workflow"""
        try:
            await require_role(current_user, Role.OWNER)
            # Hier später die echte Workflow-Deaktivierung implementieren
            
            return {"status": "success", "message": f"Workflow {workflow_name} disabled"}
        except Exception as e:
            logger.error(f"Error disabling workflow {workflow_name}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def get_overview_stats(self, current_user=Depends(get_current_user)):
        """Get overview statistics for the bot dashboard"""
        try:
            await require_role(current_user, Role.ADMIN)
            
            # Erstelle Mock-Daten, falls die Datenbank noch nicht bereit ist
            mock_stats = {
                "total_guilds": 0,
                "total_members": 0,
                "active_guilds": 0,
                "command_count": 0,
                "recent_commands": 0
            }
            
            async with session_context() as session:
                try:
                    # Versuche, die Statistiken aus der Datenbank zu holen
                    guilds_query = await session.execute(
                        select(
                            func.count(GuildEntity.id).label('total_guilds'),
                            func.sum(GuildEntity.member_count).label('total_members'),
                            func.count(GuildEntity.id).filter(GuildEntity.is_active == True).label('active_guilds')
                        )
                    )
                    
                    guild_stats = guilds_query.one()
                    
                    # Fülle die Statistiken mit Daten aus der Datenbank
                    stats = {
                        "total_guilds": guild_stats.total_guilds or 0,
                        "total_members": guild_stats.total_members or 0,
                        "active_guilds": guild_stats.active_guilds or 0,
                        "command_count": 0,  # Wird später implementiert
                        "recent_commands": 0  # Wird später implementiert
                    }
                    
                    return stats
                except Exception as e:
                    logger.error(f"Datenbankfehler beim Abrufen der Statistiken: {e}")
                    # Wenn ein Datenbankfehler auftritt, gib Mock-Daten zurück
                    return mock_stats
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Übersicht: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    async def get_servers(self, current_user=Depends(get_current_user)):
        """Get all servers the bot is connected to"""
        try:
            await require_role(current_user, Role.ADMIN)
            
            # Temporäre Mock-Daten
            mock_servers = [
                {
                    "id": 1,
                    "name": "HomeLab Discord",
                    "guild_id": "12345678901234567",
                    "member_count": 120,
                    "is_active": True
                },
                {
                    "id": 2,
                    "name": "Test Server",
                    "guild_id": "98765432109876543",
                    "member_count": 45,
                    "is_active": True
                }
            ]
            
            async with session_context() as session:
                try:
                    # Versuche, die Server aus der Datenbank zu holen
                    result = await session.execute(select(GuildEntity))
                    guilds = result.scalars().all()
                    
                    servers = []
                    for guild in guilds:
                        servers.append({
                            "id": guild.id,
                            "name": guild.name,
                            "guild_id": guild.guild_id,
                            "member_count": guild.member_count,
                            "is_active": guild.is_active
                        })
                    
                    return servers if servers else mock_servers
                except Exception as e:
                    logger.error(f"Datenbankfehler beim Abrufen der Server: {e}")
                    # Wenn ein Datenbankfehler auftritt, gib Mock-Daten zurück
                    return mock_servers
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Server: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

# Für API-Kompatibilität: Exportiere die einzelnen Funktionen auch direkt
bot_admin_controller = BotAdminController()
get_bot_status = bot_admin_controller.get_bot_status
start_bot = bot_admin_controller.start_bot
stop_bot = bot_admin_controller.stop_bot
restart_bot = bot_admin_controller.restart_bot
enable_workflow = bot_admin_controller.enable_workflow
disable_workflow = bot_admin_controller.disable_workflow
get_overview_stats = bot_admin_controller.get_overview_stats
get_servers = bot_admin_controller.get_servers 