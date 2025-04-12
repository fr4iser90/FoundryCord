# app/shared/infrastructure/integration/bot_connector.py
import asyncio
from typing import Any, Dict, Optional, List
from app.shared.interface.logging.api import get_bot_logger

logger = get_bot_logger()

class BotConnector:
    """Unified connector to interact with the bot from any part of the application"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BotConnector, cls).__new__(cls)
            cls._instance.bot_instance = None
        return cls._instance
        
    def register_bot(self, bot):
        """Register the bot instance with the connector"""
        self.bot_instance = bot
        
    async def get_bot(self):
        """Get the registered bot instance"""
        if not self.bot_instance:
            logger.error("No bot instance registered with connector")
            return None
        return self.bot_instance

    async def execute(self, service_name: str, method_name: str, *args, **kwargs) -> Any:
        """Execute a method on a bot service"""
        logger.info(f"BotConnector.execute called for Service: '{service_name}', Method: '{method_name}'")
        
        if not self.bot_instance:
            logger.error("BotConnector: No bot instance registered.")
            return None
        logger.debug(f"BotConnector: Bot instance found: {type(self.bot_instance)}")
            
        # Get the service from the bot
        service = None
        if service_name == "control":
            service = getattr(self.bot_instance, "control_service", None)
            logger.debug(f"BotConnector: Attempted to get 'control_service'. Found: {service is not None}")
        else:
            # Assume a get_service method exists for other services
            get_service_method = getattr(self.bot_instance, "get_service", None)
            if get_service_method and callable(get_service_method):
                service = get_service_method(service_name)
                logger.debug(f"BotConnector: Attempted to get service '{service_name}' via get_service. Found: {service is not None}")
            else:
                 logger.warning(f"BotConnector: Bot instance lacks a 'get_service' method.")
            
        if not service:
            logger.error(f"BotConnector: Service '{service_name}' not found on bot instance.")
            return None
        logger.debug(f"BotConnector: Service '{service_name}' found: {type(service)}")
            
        # Get and execute the method
        method = getattr(service, method_name, None)
        if not method or not callable(method):
            logger.error(f"BotConnector: Method '{method_name}' not found or not callable on service '{service_name}'.")
            return None
        logger.debug(f"BotConnector: Method '{method_name}' found on service '{service_name}'. Attempting execution...")
            
        try:
            if asyncio.iscoroutinefunction(method):
                result = await method(*args, **kwargs)
            else:
                result = method(*args, **kwargs)
            logger.info(f"BotConnector: Successfully executed {service_name}.{method_name}. Result: {result}")
            return result
        except Exception as e:
            logger.error(f"BotConnector: Error executing {service_name}.{method_name}: {e}", exc_info=True)
            raise

    async def get_status(self):
        """Get the bot status - direct implementation for web API compatibility"""
        if not self.bot_instance:
            return {"status": "offline", "error": "Bot not available"}
        
        try:
            # Try to use the client's get_status method if available
            try:
                return await self.execute('bot_client', 'get_status')
            except:
                # Fall back to direct property access
                return {
                    "status": "online" if self.bot_instance.is_ready() else "connecting",
                    "uptime": self.bot_instance.uptime if hasattr(self.bot_instance, "uptime") else 0,
                    "latency": round(self.bot_instance.latency * 1000, 2) if hasattr(self.bot_instance, "latency") else 0,
                    "guilds": len(self.bot_instance.guilds) if hasattr(self.bot_instance, "guilds") else 0,
                    "initialized_workflows": self.bot_instance.lifecycle.get_initialized_workflows() 
                        if hasattr(self.bot_instance, "lifecycle") else []
                }
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def get_servers_info(self):
        """Get information about all servers the bot is in"""
        if not self.bot_instance or not hasattr(self.bot_instance, "guilds"):
            return []
        
        try:
            # Try to use service method first
            try:
                return await self.execute('bot_client', 'get_servers_info')
            except:
                # Fall back to direct implementation
                return [
                    {
                        "id": str(guild.id),
                        "name": guild.name,
                        "member_count": guild.member_count,
                        "icon_url": str(guild.icon.url) if guild.icon else None,
                        "joined_at": guild.me.joined_at.isoformat() if guild.me.joined_at else None
                    }
                    for guild in self.bot_instance.guilds
                ]
        except Exception as e:
            logger.error(f"Error getting servers info: {e}")
            return []
    
    async def get_recent_activities(self):
        """Get recent bot activities"""
        try:
            return await self.execute('activity_tracker', 'get_recent_activities')
        except Exception as e:
            # Fall back to mock data
            logger.error(f"Error getting recent activities: {e}")
            return [
                {
                    "timestamp": "2025-03-22T07:45:00Z",
                    "type": "command",
                    "content": "User executed /help command",
                    "guild_name": "Test Server"
                },
                {
                    "timestamp": "2025-03-22T07:40:00Z",
                    "type": "join",
                    "content": "Bot joined a new server",
                    "guild_name": "Demo Server"
                }
            ]
    
    async def get_popular_commands(self):
        """Get most popular commands"""
        try:
            return await self.execute('command_tracker', 'get_popular_commands')
        except Exception as e:
            # Fall back to mock data
            logger.error(f"Error getting popular commands: {e}")
            return [
                {"name": "/help", "usage_count": 42},
                {"name": "/info", "usage_count": 37},
                {"name": "/setup", "usage_count": 28}
            ]

    async def get_system_resources(self) -> dict:
        """Get system resource usage"""
        try:
            return await self.execute('system_monitor', 'get_resources')
        except Exception as e:
            logger.error(f"Error getting system resources: {e}")
            return {
                "cpu": 0,
                "memory": 0,
                "error": str(e)
            }
            
    async def get_bot_config(self, current_user=None):
        """Get bot configuration"""
        try:
            return await self.execute('control', 'get_config')
        except Exception as e:
            logger.error(f"Error getting bot config: {e}")
            # Return default config if service call fails
            return {
                "command_prefix": "!",
                "auto_reconnect": True,
                "log_level": "INFO",
                "status_update_interval": 60,
                "max_reconnect_attempts": 5
            }

    async def start_bot(self, current_user=None):
        """Start the bot"""
        try:
            return await self.execute('control', 'start')
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise

    async def stop_bot(self, current_user=None):
        """Stop the bot"""
        try:
            return await self.execute('control', 'stop')
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
            raise

    async def restart_bot(self, current_user=None):
        """Restart the bot"""
        try:
            return await self.execute('control', 'restart')
        except Exception as e:
            logger.error(f"Error restarting bot: {e}")
            raise

    async def join_server(self, guild_id: str, current_user=None):
        """Make bot join a server"""
        try:
            return await self.execute('control', 'join_server', guild_id)
        except Exception as e:
            logger.error(f"Error joining server: {e}")
            raise

    async def leave_server(self, guild_id: str, current_user=None):
        """Make bot leave a server"""
        try:
            return await self.execute('control', 'leave_server', guild_id)
        except Exception as e:
            logger.error(f"Error leaving server: {e}")
            raise

async def get_bot_connector():
    """Async dependency function to get the bot connector instance"""
    return BotConnector()