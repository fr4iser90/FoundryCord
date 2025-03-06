from nextcord.ext import commands
import discord
import asyncio
import logging
from core.services.logging.logging_commands import logger

class RateLimitingMiddleware(commands.Cog):
    def __init__(self, bot, rate_limiting_service):
        self.bot = bot
        self.rate_limiting = rate_limiting_service

    @commands.Cog.listener()
    async def on_command(self, ctx):
        """Handle rate limiting for commands"""
        # Determine rate limit type based on command
        limit_type = 'auth' if ctx.command.name in ['login', 'authenticate'] else \
                    'admin' if ctx.command.name.startswith('admin_') else 'default'
        
        allowed, message = await self.rate_limiting.check_rate_limit(
            ctx.author.id, 
            ctx.command.name,
            limit_type
        )
        
        if not allowed:
            await ctx.send(message)
            ctx.command.reset_cooldown(ctx)
            return False
        return True

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        """Handle Discord rate limit errors"""
        if isinstance(event, discord.errors.RateLimited):
            retry_after = event.retry_after
            logger.warning(f"Rate-Limited! Retry after {retry_after:.2f} seconds.")
            await asyncio.sleep(retry_after)
        else:
            logger.error(f"Unhandled error: {event}")