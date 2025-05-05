from nextcord.ext import commands
import nextcord
import asyncio
from app.shared.interfaces.logging.api import get_bot_logger
logger = get_bot_logger()

class RateLimitingMiddleware(commands.Cog):
    def __init__(self, bot, rate_limiting_service):
        self.bot = bot
        self.rate_limiting = rate_limiting_service

    @commands.Cog.listener()
    async def on_command(self, ctx):
        """Handle rate limiting for traditional prefix commands"""
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
    async def on_interaction(self, interaction):
        """Handle rate limiting for all interactions (slash commands, buttons, etc.)"""
        # Skip interactions if they are already completed
        if interaction.is_expired() or interaction.response.is_done():
            return True
            
        # Determine the interaction type and name
        limit_type = 'default'
        action_name = "unknown_interaction"
        
        try:
            if interaction.type == nextcord.InteractionType.application_command:
                # Slash command
                command_name = interaction.data.get("name", "unknown")
                action_name = f"slash_{command_name}"
                limit_type = 'auth' if 'login' in command_name or 'auth' in command_name else \
                            'admin' if command_name.startswith('admin_') else 'default'
                            
            elif interaction.type == nextcord.InteractionType.component:
                component_type = interaction.data.get("component_type")
                custom_id = interaction.data.get("custom_id", "unknown")
                
                if component_type == 2:  # Button
                    action_name = f"button_{custom_id}"
                    limit_type = 'button'
                    
                elif component_type == 3:  # Select menu
                    action_name = f"select_{custom_id}"
                    limit_type = 'select'
                    
                # Dashboard interactions get a separate limit
                if 'dashboard' in custom_id or any(dashboard_type in custom_id for dashboard_type in 
                   ['welcome', 'monitoring', 'project', 'gamehub', 'minecraft']):
                    limit_type = 'dashboard'
                    
            elif interaction.type == nextcord.InteractionType.modal_submit:
                custom_id = interaction.data.get("custom_id", "unknown")
                action_name = f"modal_{custom_id}"
                limit_type = 'modal'
                
            # Check rate limit
            allowed, message = await self.rate_limiting.check_rate_limit(
                interaction.user.id,
                action_name,
                limit_type
            )
            
            if not allowed:
                # Handle blocked interaction
                try:
                    if not interaction.response.is_done():
                        await interaction.response.send_message(message, ephemeral=True)
                    else:
                        await interaction.followup.send(message, ephemeral=True)
                except Exception as e:
                    logger.error(f"Failed to send rate limit message: {e}")
                    
                logger.warning(f"Rate limited user {interaction.user.id} for {action_name} ({limit_type})")
                return False
                
            return True
                
        except Exception as e:
            logger.error(f"Error in interaction rate limiting: {e}")
            return True  # Allow the interaction on error to avoid blocking legitimate interactions

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        """Handle Discord rate limit errors"""
        if isinstance(event, nextcord.errors.RateLimited):
            retry_after = event.retry_after
            logger.warning(f"Rate-Limited by Discord! Retry after {retry_after:.2f} seconds.")
            await asyncio.sleep(retry_after)
        else:
            logger.error(f"Unhandled error: {event}")
