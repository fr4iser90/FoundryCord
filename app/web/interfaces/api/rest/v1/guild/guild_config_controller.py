from fastapi import APIRouter, Depends, HTTPException, status
from app.web.application.services.auth.dependencies import get_current_user
from app.web.domain.auth.permissions import Role, require_role
from app.shared.interface.logging.api import get_web_logger
from app.shared.infrastructure.database.session import session_context
from app.shared.infrastructure.models import GuildEntity
from typing import Dict, List, Optional
from sqlalchemy import select

logger = get_web_logger()
router = APIRouter(prefix="/v1/guild", tags=["Guild Configuration"])

class GuildConfigController:
    """Controller für Gilde/Server-Konfiguration"""
    
    def __init__(self):
        self.router = router
        self._register_routes()
    
    def _register_routes(self):
        """Registriert alle Routes für diesen Controller"""
        self.router.get("/config/{guild_id}")(self.get_guild_config)
        self.router.post("/config/{guild_id}")(self.update_guild_config)
        self.router.get("/permissions/{guild_id}")(self.get_guild_permissions)
        self.router.post("/permissions/{guild_id}")(self.update_guild_permissions)
    
    async def get_guild_config(self, guild_id: str, current_user=Depends(get_current_user)):
        """Get configuration for a specific guild"""
        try:
            await require_role(current_user, Role.ADMIN)
            
            async with session_context() as session:
                result = await session.execute(
                    select(GuildEntity).where(GuildEntity.guild_id == guild_id)
                )
                guild = result.scalars().first()
                
                if not guild:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Guild with ID {guild_id} not found"
                    )
                
                # In einer realen Implementierung würden wir hier die tatsächliche
                # Konfiguration aus der Datenbank laden
                config = {
                    "id": guild.id,
                    "guild_id": guild.guild_id,
                    "name": guild.name,
                    "prefix": "!",  # Beispiel für ein Konfigurations-Item
                    "welcome_channel": "general",
                    "log_channel": "logs",
                    "enable_automod": True,
                    "custom_roles": [
                        {"name": "Member", "color": "#00ff00", "permissions": ["read", "write"]},
                        {"name": "Moderator", "color": "#ff9900", "permissions": ["read", "write", "moderate"]}
                    ]
                }
                
                return config
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting guild config: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def update_guild_config(self, guild_id: str, config_data: dict, current_user=Depends(get_current_user)):
        """Update configuration for a specific guild"""
        try:
            await require_role(current_user, Role.ADMIN)
            
            # Überprüfe, ob die Gilde existiert
            async with session_context() as session:
                result = await session.execute(
                    select(GuildEntity).where(GuildEntity.guild_id == guild_id)
                )
                guild = result.scalars().first()
                
                if not guild:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Guild with ID {guild_id} not found"
                    )
            
            # In einer realen Implementierung würden wir hier die Konfiguration
            # in der Datenbank aktualisieren
            
            # Gebe die aktualisierte Konfiguration zurück
            # Hier nehmen wir an, dass alle Felder aktualisiert wurden
            updated_config = await self.get_guild_config(guild_id, current_user)
            for key, value in config_data.items():
                if key in updated_config and key not in ["id", "guild_id"]:
                    updated_config[key] = value
            
            return updated_config
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating guild config: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_guild_permissions(self, guild_id: str, current_user=Depends(get_current_user)):
        """Get permissions for a specific guild"""
        try:
            await require_role(current_user, Role.ADMIN)
            
            # Überprüfe, ob die Gilde existiert
            async with session_context() as session:
                result = await session.execute(
                    select(GuildEntity).where(GuildEntity.guild_id == guild_id)
                )
                guild = result.scalars().first()
                
                if not guild:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Guild with ID {guild_id} not found"
                    )
            
            # In einer realen Implementierung würden wir hier die Berechtigungen
            # aus der Datenbank laden
            permissions = {
                "roles": {
                    "admin": ["*"],
                    "moderator": [
                        "manage_messages",
                        "kick_members",
                        "ban_members",
                        "view_logs"
                    ],
                    "member": [
                        "read_messages",
                        "send_messages"
                    ]
                },
                "channels": {
                    "general": {
                        "read": ["@everyone"],
                        "write": ["@everyone"]
                    },
                    "admin-only": {
                        "read": ["admin"],
                        "write": ["admin"]
                    },
                    "moderator-chat": {
                        "read": ["admin", "moderator"],
                        "write": ["admin", "moderator"]
                    }
                }
            }
            
            return permissions
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting guild permissions: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def update_guild_permissions(self, guild_id: str, permissions_data: dict, current_user=Depends(get_current_user)):
        """Update permissions for a specific guild"""
        try:
            await require_role(current_user, Role.ADMIN)
            
            # Überprüfe, ob die Gilde existiert
            async with session_context() as session:
                result = await session.execute(
                    select(GuildEntity).where(GuildEntity.guild_id == guild_id)
                )
                guild = result.scalars().first()
                
                if not guild:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Guild with ID {guild_id} not found"
                    )
            
            # In einer realen Implementierung würden wir hier die Berechtigungen
            # in der Datenbank aktualisieren
            
            # Gebe die aktualisierten Berechtigungen zurück
            # Hier nehmen wir an, dass alle Berechtigungen aktualisiert wurden
            current_permissions = await self.get_guild_permissions(guild_id, current_user)
            
            if "roles" in permissions_data:
                current_permissions["roles"] = permissions_data["roles"]
                
            if "channels" in permissions_data:
                current_permissions["channels"] = permissions_data["channels"]
            
            return current_permissions
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating guild permissions: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

# Für API-Kompatibilität
guild_config_controller = GuildConfigController()
get_guild_config = guild_config_controller.get_guild_config
update_guild_config = guild_config_controller.update_guild_config
get_guild_permissions = guild_config_controller.get_guild_permissions
update_guild_permissions = guild_config_controller.update_guild_permissions 