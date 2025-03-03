from nextcord.ext import commands
from core.auth.permissions import is_authorized
from core.utilities.logger import logger

class AuthMiddleware(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        try:
            ctx = await self.bot.get_context(message)
            if not ctx.command:
                return

            # Log request details
            logger.info(f"Auth check for {ctx.command.name} by {message.author}")

            # Basic authorization check
            if not is_authorized(ctx.author):
                logger.warning(f"Unauthorized access attempt by {message.author}")
                await ctx.send("You are not authorized to use this command.")
                return

            # Log successful authorization
            logger.info(f"Authorized access to {ctx.command.name} by {message.author}")

        except Exception as e:
            logger.error(f"Auth middleware error: {str(e)}")
            await message.channel.send("An error occurred during authorization check.")

def setup(bot):
    bot.add_cog(AuthMiddleware(bot))
