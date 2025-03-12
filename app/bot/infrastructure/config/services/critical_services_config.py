from typing import List
from app.bot.infrastructure.logging import setup as setup_logging
from app.bot.services.auth import setup as setup_auth
from app.bot.infrastructure.encryption import setup as setup_encryption
from app.bot.infrastructure.rate_limiting import setup as setup_rate_limiting
from app.bot.infrastructure.logging import logger

class CriticalServicesConfig:
    @staticmethod
    def register(bot) -> List:
        return [
            bot.service_factory.create("Logging", setup_logging),
            bot.service_factory.create("Auth", setup_auth),
            bot.service_factory.create("Encryption", setup_encryption),
            bot.service_factory.create("RateLimiting", setup_rate_limiting)
        ]