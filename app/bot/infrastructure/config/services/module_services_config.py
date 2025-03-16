from typing import List
from app.bot.application.services.monitoring.system_monitoring import setup as setup_system_monitoring
from modules.tracker.ip_management import setup as setup_ip_management
from app.bot.application.services.wireguard import setup as setup_wireguard
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class ModuleServicesConfig:
    @staticmethod
    def register(bot) -> List:
        return [
            bot.factory.create_service("System Monitoring", setup_system_monitoring),
            bot.factory.create_service("IP Management", setup_ip_management),
            bot.factory.create_service("Wireguard", setup_wireguard),
        ]