from abc import ABC, abstractmethod
from typing import List
from infrastructure.database.models import MetricModel

class SystemCollectorInterface(ABC):
    """Interface defining the contract for system metric collection"""
    
    @abstractmethod
    async def collect_all(self) -> List[MetricModel]:
        """Collects all system metrics and returns them as a list"""
        pass
