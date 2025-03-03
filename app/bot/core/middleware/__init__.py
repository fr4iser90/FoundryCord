from .auth_middleware import AuthMiddleware
from .logging_middleware import LoggingMiddleware
from .rate_limit_middleware import RateLimitMiddleware
from .encryption_middleware import EncryptionMiddleware

def setup(bot):
    bot.add_cog(LoggingMiddleware(bot))
    bot.add_cog(AuthMiddleware(bot))
    bot.add_cog(RateLimitMiddleware(bot))
    bot.add_cog(EncryptionMiddleware(bot))
