from .logging_service import LoggingService
from .logging_events import LoggingEvents

__all__ = ['LoggingService', 'LoggingEvents']

def setup(bot):
    # Initialize logging service
    logging_service = LoggingService(bot)
    bot.logger = logging_service  # Make logger available globally
    
    # Register events
    events = LoggingEvents(bot, logging_service)
    bot.add_cog(events)