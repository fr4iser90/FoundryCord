# app/bot/core/checks.py
import nextcord
from nextcord.ext import commands
from app.shared.interface.logging.api import get_bot_logger
from app.bot.core.workflows.guild import ACCESS_APPROVED # Import constant

logger = get_bot_logger()

async def check_guild_approval(ctx: commands.Context) -> bool:
    """Global check to ensure commands are run in approved guilds."""
    if not ctx.guild:
        # Command is run in a DM. Allow for now.
        # Add specific DM logic here if needed later.
        return True

    # Access workflows via the bot instance attached to the context
    bot = ctx.bot
    if not hasattr(bot, 'guild_workflow'):
        logger.warning("GuildWorkflow not found on bot instance during global check. Blocking command.")
        # Fail closed: If workflow isn't ready, block the command
        return False

    guild_id_str = str(ctx.guild.id)
    # Ensure guild_workflow is accessible and has the method
    if not bot.guild_workflow:
         logger.error("GuildWorkflow is None during global check. Blocking command.")
         return False

    try:
        access_status = bot.guild_workflow.get_guild_access_status(guild_id_str)
    except Exception as e:
        logger.error(f"Error getting guild access status in global check for guild {guild_id_str}: {e}", exc_info=True)
        return False # Block command if status check fails

    if access_status != ACCESS_APPROVED:
        logger.warning(
            f"Command '{ctx.command}' blocked in guild '{ctx.guild.name}' ({guild_id_str}) due to status: {access_status}"
        )
        # You might want to add an ephemeral reply here using commands.CheckFailure exception handling
        # Raise a custom exception perhaps? For now, just return False.
        # raise commands.CheckFailure("This command can only be used in approved guilds.")
        return False # Block command execution

    # Guild is approved
    logger.debug(f"Guild {guild_id_str} approved. Allowing command '{ctx.command}'.")
    return True 