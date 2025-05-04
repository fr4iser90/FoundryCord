# @/app/bot/core/main.py
import os
import logging
import asyncio
import nextcord
from nextcord.ext import commands
import sys
from typing import Dict, Any, Optional, List

from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.database.service import DatabaseService
from app.shared.infrastructure.logging.services.logging_service import LoggingService

# Import the Bot class from its new location
from .bot import FoundryCord 

# setup_hooks are now primarily used by FoundryCord in bot.py
# from app.bot.infrastructure.startup.setup_hooks import (
#     setup_bot_services, setup_bot_workflows, setup_bot_tasks, 
#     setup_factories_and_registries, setup_event_listeners
# )
# from app.bot.interfaces.commands.checks import check_guild_approval


logger = get_bot_logger()

# Suppress nextcord gateway logs (moved to bot.py)
# logging.getLogger("nextcord.gateway").setLevel(logging.WARNING)
# logging.getLogger("nextcord.client").setLevel(logging.WARNING)
# logging.getLogger("nextcord.http").setLevel(logging.WARNING)

# Remove the FoundryCord class definition (moved to bot.py)
# class FoundryCord(commands.Bot):
#     """Main bot class for the Homelab Discord Bot"""
# ... (rest of the class definition removed) ...


async def main():
    """Main entry point for the bot"""
    try:
        intents = nextcord.Intents.default()
        intents.members = True
        intents.message_content = True

        bot = FoundryCord(command_prefix="!", intents=intents)

        logger.info("Starting the bot...")
        await bot.start(os.getenv('DISCORD_BOT_TOKEN'))

    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        logger.info("Bot shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
