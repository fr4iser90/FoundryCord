from abc import ABC, abstractmethod
from typing import List
from app.shared.infrastructure.database.models import MetricModel

class CollectorInterface(ABC):
    """Base interface for all metric collectors"""
    @abstractmethod
    async def collect_all(self) -> List[MetricModel]:
        """Collects all metrics and returns them as a list"""
        pass