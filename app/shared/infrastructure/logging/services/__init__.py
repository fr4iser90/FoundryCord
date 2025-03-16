from .base_logging_service import BaseLoggingService

# Export only what's guaranteed to be available
__all__ = ['BaseLoggingService', 'get_bot_logging_service', 'get_web_logging_service']

# Factory functions that only import when called
def get_bot_logging_service():
    """Factory function to get bot logging service"""
    from .bot_logging_service import BotLoggingService
    return BotLoggingService

def get_web_logging_service():
    """Factory function to get web logging service"""
    from .web_logging_service import WebLoggingService
    return WebLoggingService
