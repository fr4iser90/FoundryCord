from typing import Dict, List, Optional, Any
from app.bot.infrastructure.logging import logger
from nextcord.ext import commands
import nextcord
from nextcord import Message
from app.bot.interfaces.dashboards.controller.welcome_dashboard import WelcomeDashboardController

class WelcomeDashboardService:
    """Service für die Geschäftslogik des Welcome Dashboards"""
    
    def __init__(self, bot):
        self.bot = bot
        self.initialized = False
        self.embed_factory = bot.component_factory.factories['embed']
        self.dashboard_ui = None
    
    async def initialize(self) -> None:
        """Initialisiert den Service"""
        try:
            # Initialize UI component
            self.dashboard_ui = WelcomeDashboardController(self.bot).set_service(self)
            await self.dashboard_ui.initialize()
            
            self.initialized = True
            logger.info("Welcome Dashboard Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Welcome Dashboard Service: {e}")
            raise

    async def get_member_count(self) -> int:
        """Holt die aktuelle Mitgliederanzahl"""
        try:
            return len(self.bot.guilds[0].members) if self.bot.guilds else 0
        except Exception as e:
            logger.error(f"Error getting member count: {e}")
            return 0

    async def get_welcome_config(self) -> Dict[str, Any]:
        """Holt die Welcome-Konfiguration"""
        try:
            return {
                'prefix': '!',
                'rules_channel_id': None,  # TODO: Implement
                'role_config': {}  # TODO: Implement
            }
        except Exception as e:
            logger.error(f"Error getting welcome config: {e}")
            return {}

    async def create_welcome_embed(self) -> nextcord.Embed:
        """Creates the welcome embed using the factory"""
        try:
            guild = self.bot.guilds[0]  # Assuming single guild
            return self.embed_factory.create_embed(
                embed_type='welcome',
                guild_name=guild.name,
                member_count=guild.member_count
            )
        except Exception as e:
            logger.error(f"Error creating welcome embed: {e}")
            return self.embed_factory.create_embed(
                embed_type='base',
                title="⚠️ Error",
                description="Could not create welcome message"
            )

    async def update_welcome_message(self, channel_id: int, message: Optional[Message] = None) -> Message:
        """Updates or creates the welcome message"""
        try:
            channel = self.bot.get_channel(channel_id)
            if not channel:
                raise ValueError(f"Channel with ID {channel_id} not found")

            embed = await self.create_welcome_embed()
            
            if message:
                return await message.edit(embed=embed)
            else:
                return await channel.send(embed=embed)
                
        except Exception as e:
            logger.error(f"Error updating welcome message: {e}")
            raise

    async def display_dashboard(self) -> None:
        """Displays the welcome dashboard in the configured channel"""
        try:
            if not self.dashboard_ui:
                logger.error("Dashboard UI not initialized")
                return
            
            await self.dashboard_ui.display_dashboard()
            
            logger.info("Welcome dashboard displayed successfully")
        except Exception as e:
            logger.error(f"Error displaying welcome dashboard: {e}")

async def setup(bot):
    """Setup function for the Welcome Dashboard service"""
    try:
        service = WelcomeDashboardService(bot)
        await service.initialize()
        
        # Display the dashboard after initialization
        await service.display_dashboard()
        
        logger.info("Welcome Dashboard service initialized successfully")
        return service
    except Exception as e:
        logger.error(f"Failed to initialize Welcome Dashboard service: {e}")
        raise