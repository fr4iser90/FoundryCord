from nextcord.ext import commands
import nextcord
from app.bot.infrastructure.logging import logger

class AuthCommands(commands.Cog):
    def __init__(self, bot, auth_service, authorization_service=None):
        self.bot = bot
        self.auth = auth_service  # AuthenticationService
        self.authorization = authorization_service  # AuthorizationService

    @nextcord.slash_command(
        name="login_ip",
        description="Login with your public IP"
    )
    async def login_ip_command(
        self, 
        interaction: nextcord.Interaction, 
        ip: str = nextcord.SlashOption(
            description="Your public IP address (e.g. 84.173.179.225)",
            required=True
        )
    ):
        """Login and whitelist your IP"""
        try:
            # Create session
            token = await self.auth.create_session(interaction.user.id)
            
            # Add IP to whitelist
            if hasattr(self.bot, 'ip_management'):
                await self.bot.ip_management.add_ip(
                    ip=ip,
                    user_id=interaction.user.id,
                    username=interaction.user.name
                )
                await interaction.response.send_message(
                    f"✅ Session created and IP {ip} whitelisted!", 
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    "✅ Session created (IP whitelisting not available)", 
                    ephemeral=True
                )
                
            logger.info(f"IP-Login successful for {interaction.user.name} with IP {ip}")
            
        except Exception as e:
            logger.error(f"IP-Login error: {e}")
            await interaction.response.send_message(
                "❌ Failed to complete IP login", 
                ephemeral=True
            )

    @nextcord.slash_command(name="login", description="Create a new session")
    async def login_command(self, interaction: nextcord.Interaction):
        """Create a new session for the user"""
        try:
            token = await self.auth.create_session(interaction.user.id)
            await interaction.response.send_message("✅ Session created successfully", ephemeral=True)
            logger.info(f"New session created for user {interaction.user.name}")
        except Exception as e:
            logger.error(f"Login error: {e}")
            await interaction.response.send_message("❌ Failed to create session", ephemeral=True)

    @nextcord.slash_command(name="logout", description="End current session")
    async def logout_command(self, interaction: nextcord.Interaction):
        """End the current user session"""
        try:
            if await self.auth.revoke_session(interaction.user.id):
                await interaction.response.send_message("✅ Session ended successfully", ephemeral=True)
                logger.info(f"Session ended for user {interaction.user.name}")
            else:
                await interaction.response.send_message("❌ No active session found", ephemeral=True)
        except Exception as e:
            logger.error(f"Logout error: {e}")
            await interaction.response.send_message("❌ Failed to end session", ephemeral=True)

    @nextcord.slash_command(name="ip_help", description="How to find your IP")
    async def ip_help_command(self, interaction: nextcord.Interaction):
        help_text = """
            To find your public IP:
            1. Visit https://whatismyip.com
            2. Copy your IPv4 address
            3. Use `/login_ip <your_ip>` to login
            """
        await interaction.response.send_message(help_text, ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        try:
            ctx = await self.bot.get_context(message)
            if not ctx.command:
                return

            # Authorization check with rate limiting
            rate_limiter = self.bot.get_cog('RateLimitMiddleware')
            if rate_limiter and not await rate_limiter.check_rate_limit(ctx, 'auth'):
                return

            # Use authorization service for permission checks
            if self.authorization and not await self.authorization.check_authorization(ctx.author):
                sanitized_author = f"User_{hash(str(message.author.id))}"
                logger.warning(f"Unauthorized access attempt by {sanitized_author}")
                await ctx.send("You are not authorized to use this command.")
                return

            # Create session if needed using authentication service
            if str(ctx.author.id) not in self.auth.active_sessions:
                await self.auth.create_session(ctx.author.id)

        except Exception as e:
            logger.error(f"Auth command error: {str(e)}")
            await message.channel.send("An error occurred during authorization check.")