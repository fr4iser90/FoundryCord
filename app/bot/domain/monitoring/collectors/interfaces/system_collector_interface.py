from abc import ABC, abstractmethod
from typing import List
from app.bot.infrastructure.database.models import MetricModel
from .collector_interface import CollectorInterface

class SystemCollectorInterface(CollectorInterface):
    """System-specific collector interface"""

    @abstractmethod
    async def collect_system_metrics(self) -> List[MetricModel]:
        """Collects all system-related metrics"""
        pass