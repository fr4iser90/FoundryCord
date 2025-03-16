from typing import List
from .services.critical_services_config import CriticalServicesConfig
from .services.module_services_config import ModuleServicesConfig
from .services.dashboard_config import DashboardConfig
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class ServiceConfig:
    @staticmethod
    def register_critical_services(bot) -> List:
        return CriticalServicesConfig.register(bot)
    
    @staticmethod
    def register_module_services(bot) -> List:
        services = ModuleServicesConfig.register(bot)
        services.append(DashboardConfig.register(bot))
        return services