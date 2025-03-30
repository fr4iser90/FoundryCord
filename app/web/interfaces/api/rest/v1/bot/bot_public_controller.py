from fastapi import APIRouter, Depends, HTTPException
from app.shared.infrastructure.integration.bot_connector import BotConnector, get_bot_connector
from app.web.infrastructure.security.auth import get_current_user

router = APIRouter(prefix="/v1/bot-public-info", tags=["Bot Public Information API"])

class BotPublicController:
    """Controller für öffentliche Bot-Informationen"""
    
    def __init__(self):
        self.router = router
        self._register_routes()
    
    def _register_routes(self):
        """Registriert alle Routes für diesen Controller"""
        self.router.get("/status", endpoint=self.get_bot_status)
        self.router.get("/servers", endpoint=self.get_servers_info)
        self.router.get("/system-resources", endpoint=self.get_system_resources)
        self.router.get("/recent-activities", endpoint=self.get_recent_activities)
        self.router.get("/popular-commands", endpoint=self.get_popular_commands)
    
    async def get_bot_status(self, 
                           bot_connector=Depends(get_bot_connector),
                           current_user=Depends(get_current_user)):
        """Get the current status of the bot"""
        return await bot_connector.get_bot_status()
    
    async def get_servers_info(self, bot_connector: BotConnector = Depends(get_bot_connector)):
        """Get information about servers the bot is in"""
        return await bot_connector.get_servers_info()
    
    async def get_system_resources(self):
        """Get system resource usage"""
        import psutil
        
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "cpu": cpu,
            "memory": {
                "percent": memory.percent,
                "used": f"{memory.used / (1024 * 1024 * 1024):.1f} GB",
                "total": f"{memory.total / (1024 * 1024 * 1024):.1f} GB"
            },
            "disk": {
                "percent": disk.percent,
                "used": f"{disk.used / (1024 * 1024 * 1024):.1f} GB", 
                "total": f"{disk.total / (1024 * 1024 * 1024):.1f} GB"
            }
        }
    
    async def get_recent_activities(self):
        """Get recent bot activities"""
        # Mock data
        return [
            {"type": "join", "guild": "Server Alpha", "timestamp": "2025-03-23T15:30:45"},
            {"type": "command", "command": "/help", "user": "User123", "timestamp": "2025-03-23T15:25:12"},
            {"type": "dashboard", "action": "Created", "user": "Admin456", "timestamp": "2025-03-23T15:10:05"},
            {"type": "system", "message": "Bot restarted", "timestamp": "2025-03-23T14:55:30"},
            {"type": "command", "command": "/status", "user": "User789", "timestamp": "2025-03-23T14:45:18"}
        ]
    
    async def get_popular_commands(self):
        """Get most popular bot commands"""
        # Mock data
        return [
            {"name": "/help", "count": 246},
            {"name": "/status", "count": 189},
            {"name": "/ping", "count": 157},
            {"name": "/dashboard", "count": 98},
            {"name": "/config", "count": 67}
        ]

# Für API-Kompatibilität: Exportiere die einzelnen Funktionen auch direkt
get_bot_status = BotPublicController().get_bot_status
get_servers_info = BotPublicController().get_servers_info
get_system_resources = BotPublicController().get_system_resources
get_recent_activities = BotPublicController().get_recent_activities
get_popular_commands = BotPublicController().get_popular_commands
