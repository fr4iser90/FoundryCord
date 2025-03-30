from fastapi import APIRouter, Depends, HTTPException
from app.shared.infrastructure.integration.bot_connector import BotConnector, get_bot_connector
from app.web.infrastructure.security.auth import get_current_user

router = APIRouter(prefix="/v1/bot-public-info", tags=["Bot Public Information API"])

@router.get("/status")
async def get_bot_status(bot_connector = Depends(get_bot_connector),
                         current_user = Depends(get_current_user)):
    """Get the current status of the bot"""
    return await bot_connector.get_bot_status()

@router.get("/servers")
async def get_servers_info(
    bot_connector: BotConnector = Depends(get_bot_connector)
):
    """Get information about servers the bot is in"""
    return await bot_connector.get_servers_info()

@router.get("/system-resources")
async def get_system_resources():
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

@router.get("/recent-activities")
async def get_recent_activities():
    """Get recent bot activities"""
    # Mock data
    return [
        {"type": "join", "guild": "Server Alpha", "timestamp": "2025-03-23T15:30:45"},
        {"type": "command", "command": "/help", "user": "User123", "timestamp": "2025-03-23T15:25:12"},
        {"type": "dashboard", "action": "Created", "user": "Admin456", "timestamp": "2025-03-23T15:10:05"},
        {"type": "system", "message": "Bot restarted", "timestamp": "2025-03-23T14:55:30"},
        {"type": "command", "command": "/status", "user": "User789", "timestamp": "2025-03-23T14:45:18"}
    ]

@router.get("/popular-commands")
async def get_popular_commands():
    """Get most popular bot commands"""
    # Mock data
    return [
        {"name": "/help", "count": 246},
        {"name": "/status", "count": 189},
        {"name": "/ping", "count": 157},
        {"name": "/dashboard", "count": 98},
        {"name": "/config", "count": 67}
    ]