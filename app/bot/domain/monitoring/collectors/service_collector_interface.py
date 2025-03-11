from abc import ABC, abstractmethod
from typing import List
from infrastructure.database.models import MetricModel

class ServiceCollectorInterface(ABC):
    """Interface defining the contract for service metric collection"""
    
    @abstractmethod
    async def collect_all(self) -> List[MetricModel]:
        """Collects all service metrics and returns them as a list"""
        pass
