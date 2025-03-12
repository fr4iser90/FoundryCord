from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.bot.infrastructure.database.models import MetricModel
from .collector_interface import CollectorInterface

class ServiceCollectorInterface(CollectorInterface):
    """Service-specific collector interface"""
    @abstractmethod
    async def collect_game_services(self) -> Dict[str, Any]:
        """Collects status of all game services"""
        pass

    @abstractmethod
    async def collect_service_metrics(self) -> List[MetricModel]:
        """Collects all service-related metrics"""
        pass