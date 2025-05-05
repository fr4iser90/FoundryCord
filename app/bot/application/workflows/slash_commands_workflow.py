# app/bot/core/workflows/slash_commands_workflow.py
from .base_workflow import BaseWorkflow, WorkflowStatus
from app.shared.interfaces.logging.api import get_bot_logger
logger = get_bot_logger()
from app.bot.infrastructure.discord.command_sync_service import CommandSyncService
import inspect

class SlashCommandsWorkflow(BaseWorkflow):
    """Workflow for registering and syncing slash commands"""
    
    def __init__(self, bot):
        super().__init__("slash_commands")
        self.bot = bot
        
        # Slash commands don't require guild approval
        self.requires_guild_approval = False
    
    async def initialize(self) -> bool:
        """Initialize slash command registration and syncing"""
        try:
            logger.debug("Starting slash commands workflow initialization")
            
            # Initialize command sync service directly on the bot
            if not hasattr(self.bot, 'command_sync_service'):
                enable_guild_sync = self.bot.env_config.is_development
                enable_global_sync = not self.bot.env_config.is_development
                
                # Use the lifecycle manager's setup_command_sync method instead
                await self.bot.lifecycle.setup_command_sync(
                    enable_guild_sync=enable_guild_sync,
                    enable_global_sync=enable_global_sync
                )
            
            # Collect and register commands from cogs
            await self._register_commands()
            
            # Use the lifecycle manager to sync commands
            sync_time = await self.bot.lifecycle.sync_commands()
            logger.info(f"Initial command synchronization completed in {sync_time:.2f} seconds")
            
            # Start background sync for continuous updates if in development
            if self.bot.env_config.is_development:
                await self.bot.lifecycle.sync_commands_background()
                
            # Mark as active for all guilds since commands are global
            if hasattr(self, 'bot') and self.bot:
                for guild in self.bot.guilds:
                    self.guild_status[str(guild.id)] = WorkflowStatus.ACTIVE
            
            return True
            
        except Exception as e:
            logger.error(f"Slash commands workflow initialization failed: {e}")
            raise
    
    async def _register_commands(self):
        """Register all command modules"""
        try:
            from app.bot.infrastructure.config import CommandConfig
            
            if hasattr(CommandConfig, 'register_commands'):
                commands = CommandConfig.register_commands(self.bot)
                
                for command in commands:
                    try:
                        setup_func = command['setup']
                        
                        # Check if setup is a coroutine function
                        if inspect.iscoroutinefunction(setup_func):
                            command_instance = await setup_func(self.bot)
                        else:
                            command_instance = setup_func(self.bot)
                        
                        self.bot.lifecycle.commands.append({
                            'name': command['name'],
                            'instance': command_instance
                        })
                        
                        logger.info(f"Registered command module: {command['name']}")
                    except Exception as e:
                        logger.error(f"Failed to register command {command['name']}: {e}")
            
            logger.info(f"Registered {len(self.bot.lifecycle.commands)} command modules")
            return self.bot.lifecycle.commands
            
        except Exception as e:
            logger.error(f"Command registration failed: {e}")
            raise
            
    async def initialize_for_guild(self, guild_id: str) -> bool:
        """Initialize workflow for a specific guild"""
        # Commands are global, so just mark as active
        self.guild_status[guild_id] = WorkflowStatus.ACTIVE
        return True
    
    async def cleanup(self) -> None:
        """Cleanup command resources"""
        try:
            logger.debug("Starting slash commands cleanup")
            await super().cleanup()
        except Exception as e:
            logger.error(f"Slash commands cleanup failed: {e}")
            
    async def cleanup_guild(self, guild_id: str) -> None:
        """Cleanup resources for a specific guild"""
        # Commands are global, so just remove status
        await super().cleanup_guild(guild_id)

    async def setup(self, bot):
        """Setup function for the command module"""
        try:
            # 1. Check and initialize required services if needed
            if not hasattr(bot, 'required_service'):
                from app.bot.application.services.required_service import setup as setup_service
                bot.required_service = await setup_service(bot)
                
            # 2. Create command cog instance
            commands = YourCommandCog(bot, bot.required_service)
            
            # 3. Add cog to bot (not awaitable)
            bot.add_cog(commands)
            
            # 4. Log success
            logger.info("Your commands initialized successfully")
            
            # 5. Return the command instance
            return commands
            
        except Exception as e:
            logger.error(f"Failed to initialize your commands: {e}")
            raise