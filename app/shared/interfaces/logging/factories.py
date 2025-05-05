# from fastapi import FastAPI
# from app.shared.infrastructure.logging.services.bot_logging_service import BotLoggingService
# from app.shared.infrastructure.logging.services.web_logging_service import WebLoggingService

def create_bot_logging_service(bot):
    """Factory function to create a bot logging service"""
    from app.shared.infrastructure.logging.services.bot_logging_service import BotLoggingService
    return BotLoggingService(bot)

def create_web_logging_service(app):
    """Factory function to create a web logging service"""
    from app.shared.infrastructure.logging.services.web_logging_service import WebLoggingService
    return WebLoggingService(app)
