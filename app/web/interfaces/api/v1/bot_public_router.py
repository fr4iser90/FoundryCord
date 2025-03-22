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
async def get_system_resources(bot_connector = Depends(get_bot_connector),
                               current_user = Depends(get_current_user)):
    """Get system resource usage"""
    return await bot_connector.get_system_resources()

@router.get("/recent-activities")
async def get_recent_activities(
    bot_connector: BotConnector = Depends(get_bot_connector)
):
    """Get recent activities"""
    return await bot_connector.get_recent_activities()

@router.get("/popular-commands")
async def get_popular_commands(
    bot_connector: BotConnector = Depends(get_bot_connector)
):
    """Get popular commands"""
    return await bot_connector.get_popular_commands()