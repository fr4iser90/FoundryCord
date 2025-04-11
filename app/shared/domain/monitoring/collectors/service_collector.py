"""Service metrics collector interface"""
from abc import ABC, abstractmethod
from typing import List
from app.shared.infrastructure.models import MetricModel

class ServiceCollectorInterface(ABC):
    @abstractmethod
    async def collect_all(self) -> List[MetricModel]:
        """Collect all service metrics"""
        pass 