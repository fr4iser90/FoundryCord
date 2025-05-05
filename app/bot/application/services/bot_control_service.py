import asyncio
from typing import Any
from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.repositories.discord.guild_config_repository_impl import GuildConfigRepositoryImpl
from app.shared.infrastructure.database.session.context import session_context


logger = get_bot_logger()

class BotControlService:
    """Service layer responsible for handling control commands for the bot."""

    def __init__(self, bot):
        """Initialize the BotControlService.
        
        Args:
            bot: The instance of the main bot application (e.g., FoundryCord).
        """
        self.bot = bot
        logger.debug("BotControlService initialized.")

    async def trigger_approve_guild(self, guild_id: str) -> bool:
        """
        Triggers the GuildWorkflow's approve_guild method for the specified guild.
        This acts as a bridge between external requests (like from the web UI)
        and the bot's internal workflow logic.

        Args:
            guild_id: The ID of the guild to approve.

        Returns:
            True if the workflow method was called successfully, False otherwise.
        """
        logger.info(f"BotControlService received request to trigger approval for guild: {guild_id}")
        
        if not self.bot or not hasattr(self.bot, 'workflow_manager'):
            logger.error("Bot instance or workflow manager not available in BotControlService.")
            return False

        try:
            # Get the GuildWorkflow instance from the manager
            guild_workflow = self.bot.workflow_manager.get_workflow("guild")
            
            if not guild_workflow:
                logger.error("GuildWorkflow not found in workflow manager.")
                return False
            
            # Call the actual workflow method
            logger.info(f"Calling guild_workflow.approve_guild('{guild_id}')")
            # We assume approve_guild handles its own internal errors and logging
            # The result here indicates if the *bot* successfully processed the approval
            success = await guild_workflow.approve_guild(guild_id)
            logger.info(f"guild_workflow.approve_guild('{guild_id}') returned: {success}")
            return success
        except Exception as e:
            logger.error(f"Error in BotControlService while triggering guild approval for {guild_id}: {e}", exc_info=True)
            return False

    # --- NEW: Method to trigger template application --- 
    async def trigger_apply_template(self, guild_id: str) -> bool:
        """
        Triggers the GuildWorkflow's apply_template method for the specified guild.

        Args:
            guild_id: The ID of the guild to apply the active template to.

        Returns:
            True if the workflow method was called and returned True, False otherwise.
        """
        logger.info(f"BotControlService received request to trigger template application for guild: {guild_id}")
        
        if not self.bot or not hasattr(self.bot, 'workflow_manager'):
            logger.error("Bot instance or workflow manager not available in BotControlService.")
            return False

        try:
            # Get the GuildWorkflow instance from the manager
            guild_workflow = self.bot.workflow_manager.get_workflow("guild")
            
            if not guild_workflow:
                logger.error("GuildWorkflow not found in workflow manager.")
                return False
            
            # --- BEGIN FIX: Fetch config and session before calling apply_template --- 
            try:
                async with session_context() as session:
                    # Fetch the GuildConfig using the session
                    guild_config_repo = GuildConfigRepositoryImpl(session)
                    config = await guild_config_repo.get_by_guild_id(guild_id)
                    if not config:
                        logger.error(f"GuildConfigEntity not found for guild {guild_id} within BotControlService trigger. Cannot apply template.")
                        return False
                    if config.active_template_id is None:
                         logger.error(f"Guild {guild_id} has no active template set in GuildConfig. Cannot apply template.")
                         return False

                    # Call the workflow method with all required arguments
                    logger.info(f"Calling guild_workflow.apply_template with guild_id={guild_id}, config={config.id}, session")
                    success = await guild_workflow.apply_template(
                        guild_id=guild_id, 
                        config=config, 
                        session=session
                    )
                    logger.info(f"guild_workflow.apply_template('{guild_id}') returned: {success}")
                    return success
                
            except Exception as apply_exec_err:
                logger.error(f"Error executing apply_template within session for guild {guild_id}: {apply_exec_err}", exc_info=True)
                return False
            # --- END FIX --- 

        except Exception as e:
            logger.error(f"Error in BotControlService while triggering template application for {guild_id}: {e}", exc_info=True)
            return False
    # --- END NEW METHOD --- 

    # --- Other potential control methods --- 
    async def start(self):
        # Logic to start the bot if it's stopped
        logger.info("Received start command (Not Implemented)")
        return {"status": "error", "message": "Start not implemented via service"}

    async def stop(self):
        # Logic to gracefully stop the bot
        logger.info("Received stop command. Initiating shutdown.")
        if self.bot and hasattr(self.bot, 'shutdown_handler'):
            asyncio.create_task(self.bot.shutdown_handler.shutdown())
            return {"status": "ok", "message": "Shutdown initiated"}
        else:
            logger.error("Cannot initiate shutdown: Bot or shutdown handler not available.")
            return {"status": "error", "message": "Shutdown handler unavailable"}

    async def restart(self):
        # Logic to restart the bot
        logger.info("Received restart command. Initiating restart.")
        if self.bot and hasattr(self.bot, 'shutdown_handler'):
            # Request restart via shutdown handler
            asyncio.create_task(self.bot.shutdown_handler.shutdown(restart=True))
            return {"status": "ok", "message": "Restart initiated"}
        else:
             logger.error("Cannot initiate restart: Bot or shutdown handler not available.")
             return {"status": "error", "message": "Shutdown handler unavailable"}

    async def get_config(self):
        # Logic to retrieve bot configuration
        logger.info("Received get_config command (Not Implemented)")
        return {"error": "Not Implemented"} # Placeholder

    async def join_guild(self, guild_id: str):
        # Logic to make the bot join a guild (likely needs admin privileges)
        logger.info(f"Received join_guild command for {guild_id} (Not Implemented)")
        return {"error": "Not Implemented"} # Placeholder

    async def leave_guild(self, guild_id: str):
        # Logic to make the bot leave a guild
        logger.info(f"Received leave_guild command for {guild_id}")
        try:
            guild = self.bot.get_guild(int(guild_id))
            if guild:
                await guild.leave()
                logger.info(f"Successfully left guild {guild_id}")
                return {"status": "ok", "message": f"Left guild {guild_id}"}
            else:
                logger.warning(f"Cannot leave guild {guild_id}: Bot is not in this guild.")
                return {"status": "error", "message": "Bot not in specified guild"}
        except Exception as e:
             logger.error(f"Error leaving guild {guild_id}: {e}", exc_info=True)
             return {"status": "error", "message": str(e)}
