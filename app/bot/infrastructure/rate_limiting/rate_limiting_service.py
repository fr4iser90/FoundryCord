from datetime import datetime, timedelta
from collections import defaultdict
from app.shared.logging import logger

class RateLimitingService:
    def __init__(self, bot):
        self.bot = bot
        self.command_cooldowns = defaultdict(lambda: defaultdict(lambda: datetime.min))
        self.interaction_cooldowns = defaultdict(lambda: defaultdict(lambda: datetime.min))
        self.failed_attempts = defaultdict(int)
        self.blocked_users = set()
        
        # Configure limits
        self.rate_limits = {
            'default': (5, 60),     # 5 commands per 60 seconds
            'auth': (3, 300),       # 3 auth attempts per 300 seconds
            'admin': (10, 60),      # 10 admin commands per 60 seconds
            'button': (15, 60),     # 15 button clicks per 60 seconds
            'select': (10, 60),     # 10 select menu interactions per 60 seconds
            'dashboard': (20, 60),  # 20 dashboard interactions per 60 seconds
            'modal': (5, 60)        # 5 modal submissions per 60 seconds
        }

    async def check_rate_limit(self, user_id, action_name, limit_type='default'):
        """Check if a command or interaction is within rate limits"""
        current_time = datetime.now()
        
        # Check if user is blocked
        if user_id in self.blocked_users:
            logger.warning(f"Blocked user {user_id} attempted to use {action_name}")
            return False, "You are temporarily blocked due to too many attempts."

        # Get rate limit settings
        max_attempts, window = self.rate_limits.get(limit_type, self.rate_limits['default'])
        
        # Clean up old entries
        self._cleanup_old_entries(user_id, window, is_interaction=limit_type not in ['default', 'auth', 'admin'])
        
        # Get appropriate cooldowns dict based on limit type
        cooldowns = self.interaction_cooldowns if limit_type not in ['default', 'auth', 'admin'] else self.command_cooldowns
        
        # Check current usage
        recent_actions = len([t for t in cooldowns[user_id].values() 
                             if current_time - t < timedelta(seconds=window)])
        
        if recent_actions >= max_attempts:
            self.failed_attempts[user_id] += 1
            if self.failed_attempts[user_id] >= 3:
                logger.warning(f"User {user_id} blocked for excessive {limit_type} usage")
                self.blocked_users.add(user_id)
                return False, "You have been temporarily blocked due to rate limit violations."
            return False, f"Rate limit exceeded. Please wait {window} seconds."
            
        # Record the action usage
        cooldowns[user_id][action_name] = current_time
        return True, None

    def _cleanup_old_entries(self, user_id, window, is_interaction=False):
        """Clean up expired rate limit entries"""
        current_time = datetime.now()
        cutoff = current_time - timedelta(seconds=window)
        
        # Choose the appropriate dictionary
        cooldowns = self.interaction_cooldowns if is_interaction else self.command_cooldowns
        
        cooldowns[user_id] = {
            action: time for action, time in cooldowns[user_id].items()
            if time > cutoff
        }
        
    async def unblock_user(self, user_id):
        """Manually unblock a user"""
        if user_id in self.blocked_users:
            self.blocked_users.remove(user_id)
            self.failed_attempts[user_id] = 0
            return True
        return False
        
    async def get_rate_limit_status(self, user_id):
        """Get rate limit status for a user"""
        is_blocked = user_id in self.blocked_users
        failed_attempts = self.failed_attempts.get(user_id, 0)
        
        command_usage = {}
        for limit_type, (max_attempts, window) in self.rate_limits.items():
            # Get appropriate cooldowns dict based on limit type
            cooldowns = self.interaction_cooldowns if limit_type not in ['default', 'auth', 'admin'] else self.command_cooldowns
            
            # Count recent actions
            current_time = datetime.now()
            recent_actions = len([t for t in cooldowns[user_id].values() 
                                if current_time - t < timedelta(seconds=window)])
            
            command_usage[limit_type] = {
                'recent': recent_actions,
                'max': max_attempts,
                'window': window
            }
            
        return {
            'is_blocked': is_blocked,
            'failed_attempts': failed_attempts,
            'usage': command_usage
        }
