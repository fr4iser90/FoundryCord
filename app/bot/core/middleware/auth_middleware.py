from nextcord.ext import commands
from core.auth.permissions import is_authorized
from core.utilities.logger import logger
from datetime import datetime, timedelta
import jwt as PyJWT
import os

class AuthMiddleware(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.jwt_secret = os.getenv('JWT_SECRET_KEY')
        if not self.jwt_secret:
            logger.warning("JWT_SECRET_KEY not set! Using fallback secret (not recommended for production)")
            self.jwt_secret = "fallback_secret_key"  # Only for development
        self.session_duration = timedelta(hours=24)
        self.active_sessions = {}

    async def create_session(self, user_id):
        """Create a new session token"""
        expiry = datetime.utcnow() + self.session_duration
        token = PyJWT.encode({
            'user_id': str(user_id),
            'exp': expiry
        }, self.jwt_secret, algorithm='HS256')
        self.active_sessions[str(user_id)] = token
        return token

    async def validate_session(self, user_id, token):
        """Validate a session token"""
        try:
            if str(user_id) not in self.active_sessions:
                return False
            if self.active_sessions[str(user_id)] != token:
                return False
            payload = PyJWT.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload['user_id'] == str(user_id)
        except PyJWT.ExpiredSignatureError:
            del self.active_sessions[str(user_id)]
            return False
        except PyJWT.InvalidTokenError:
            return False

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        try:
            ctx = await self.bot.get_context(message)
            if not ctx.command:
                return

            # Sanitize log data
            sanitized_author = f"User_{hash(str(message.author.id))}"
            logger.info(f"Auth check for {ctx.command.name} by {sanitized_author}")

            # Authorization check with rate limiting
            rate_limiter = self.bot.get_cog('RateLimitMiddleware')
            if rate_limiter and not await rate_limiter.check_rate_limit(ctx, 'auth'):
                return

            if not is_authorized(ctx.author):
                logger.warning(f"Unauthorized access attempt by {sanitized_author}")
                await ctx.send("You are not authorized to use this command.")
                return

            # Create or validate session
            if str(ctx.author.id) not in self.active_sessions:
                await self.create_session(ctx.author.id)

            logger.info(f"Authorized access to {ctx.command.name} by {sanitized_author}")

        except Exception as e:
            logger.error(f"Auth middleware error: {str(e)}")
            await message.channel.send("An error occurred during authorization check.")

def setup(bot):
    bot.add_cog(AuthMiddleware(bot))
