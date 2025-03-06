from datetime import datetime, timedelta
from collections import defaultdict
from core.services.logging.logging_commands import logger

class RateLimitingService:
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

    async def check_rate_limit(self, user_id, command_name, limit_type='default'):
        """Check if a command execution is within rate limits"""
        current_time = datetime.now()
        
        # Check if user is blocked
        if user_id in self.blocked_users:
            logger.warning(f"Blocked user {user_id} attempted to use command {command_name}")
            return False, "You are temporarily blocked due to too many attempts."

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
                return False, "You have been temporarily blocked due to rate limit violations."
            return False, f"Rate limit exceeded. Please wait {window} seconds."
            
        # Record the command usage
        self.command_cooldowns[user_id][command_name] = current_time
        return True, None

    def _cleanup_old_entries(self, user_id, window):
        """Clean up expired rate limit entries"""
        current_time = datetime.now()
        cutoff = current_time - timedelta(seconds=window)
        self.command_cooldowns[user_id] = {
            cmd: time for cmd, time in self.command_cooldowns[user_id].items()
            if time > cutoff
        }