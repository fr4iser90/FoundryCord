# bot/core/middleware/auth_middleware.py
from nextcord.ext import commands
from core.auth.permissions import is_authorized

class AuthMiddleware(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Check authorization before command execution
        ctx = await self.bot.get_context(message)
        if ctx.command and not is_authorized(ctx.author):
            await ctx.send("Du bist nicht autorisiert, diesen Befehl zu verwenden.")
            return

def setup(bot):
    bot.add_cog(AuthMiddleware(bot))

