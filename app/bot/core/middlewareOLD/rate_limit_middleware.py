import asyncio
import logging
import discord
from nextcord.ext import commands
from datetime import datetime, timedelta
from collections import defaultdict

class RateLimitMiddleware(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.command_cooldowns = defaultdict(lambda: defaultdict(lambda: datetime.min))
        self.failed_attempts = defaultdict(int)
        self.blocked_users = set()
        
        # Configure limits
        self.rate_limits = {
            'default': (5, 60),  # 5 commands per 60 seconds
            'auth': (3, 300),    # 3 auth attempts per 300 seconds
            'admin': (10, 60)    # 10 admin commands per 60 seconds
        }

    async def check_rate_limit(self, ctx, limit_type='default'):
        user_id = ctx.author.id
        current_time = datetime.now()
        
        # Check if user is blocked
        if user_id in self.blocked_users:
            await ctx.send("You are temporarily blocked due to too many attempts.")
            return False

        # Get rate limit settings
        max_attempts, window = self.rate_limits[limit_type]
        
        # Clean up old entries
        self._cleanup_old_entries(user_id, window)
        
        # Check current usage
        recent_commands = len([t for t in self.command_cooldowns[user_id].values() 
                             if current_time - t < timedelta(seconds=window)])
        
        if recent_commands >= max_attempts:
            self.failed_attempts[user_id] += 1
            if self.failed_attempts[user_id] >= 3:
                self.blocked_users.add(user_id)
                await ctx.send("You have been temporarily blocked due to rate limit violations.")
                return False
            await ctx.send(f"Rate limit exceeded. Please wait {window} seconds.")
            return False
            
        # Record the command usage
        self.command_cooldowns[user_id][ctx.command.name] = current_time
        return True

    def _cleanup_old_entries(self, user_id, window):
        current_time = datetime.now()
        cutoff = current_time - timedelta(seconds=window)
        self.command_cooldowns[user_id] = {
            cmd: time for cmd, time in self.command_cooldowns[user_id].items()
            if time > cutoff
        }

    @commands.Cog.listener()
    async def on_command(self, ctx):
        # Determine rate limit type based on command
        limit_type = 'auth' if ctx.command.name in ['login', 'authenticate'] else \
                    'admin' if ctx.command.name.startswith('admin_') else 'default'
        
        if not await self.check_rate_limit(ctx, limit_type):
            ctx.command.reset_cooldown(ctx)
            return False
        return True

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        """Fehler-Handler für Rate-Limiting."""
        if isinstance(event, discord.errors.RateLimited):
            retry_after = event.retry_after  # Zeit bis zur nächsten Anfrage
            logging.warning(f"Rate-Limited! Retry after {retry_after:.2f} seconds.")
            await asyncio.sleep(retry_after)  # Warten bis das Rate-Limit zurückgesetzt wird
        else:
            logging.error(f"Unbehandelte Fehlermeldung: {event}")

    async def delete_message(self, message):
        """Löscht eine Nachricht und behandelt Rate-Limits."""
        try:
            await message.delete()
            await asyncio.sleep(0.75)
        except discord.errors.RateLimited as e:
            retry_after = e.retry_after
            logging.warning(f"Rate-Limited während Löschung! Retry after {retry_after:.2f} seconds.")
            await asyncio.sleep(retry_after)  # Warten, bis das Rate-Limit zurückgesetzt wird
            await message.delete()  # Löscht nach der Verzögerung

def setup(bot):
    bot.add_cog(RateLimitMiddleware(bot))  # Füge die RateLimitMiddleware hinzu
