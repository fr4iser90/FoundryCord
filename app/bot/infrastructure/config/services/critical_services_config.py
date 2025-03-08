from typing import List
from infrastructure.logging import setup as setup_logging
from services.auth import setup as setup_auth
from infrastructure.encryption import setup as setup_encryption
from infrastructure.rate_limiting import setup as setup_rate_limiting
from infrastructure.logging import logger

class CriticalServicesConfig:
    @staticmethod
    def register(bot) -> List:
        return [
            bot.service_factory.create("Logging", setup_logging),
            bot.service_factory.create("Auth", setup_auth),
            bot.service_factory.create("Encryption", setup_encryption),
            bot.service_factory.create("RateLimiting", setup_rate_limiting)
        ]