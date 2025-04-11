"""System metrics collector interface"""
from abc import ABC, abstractmethod
from typing import List
from app.shared.infrastructure.models import MetricModel

class SystemCollectorInterface(ABC):
    @abstractmethod
    async def collect_all(self) -> List[MetricModel]:
        """Collect all system metrics"""
        pass 