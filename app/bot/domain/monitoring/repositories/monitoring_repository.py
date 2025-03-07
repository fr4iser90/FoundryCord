from abc import ABC, abstractmethod
from typing import List, Optional
from ..models.metric import Metric
from ..models.alert import Alert

class MonitoringRepository(ABC):
    @abstractmethod
    async def save_metric(self, metric: Metric) -> None:
        """Save a metric to the repository"""
        pass
        
    @abstractmethod
    async def get_metrics(self, name: str, limit: int = 100) -> List[Metric]:
        """Get metrics by name"""
        pass
        
    @abstractmethod
    async def save_alert(self, alert: Alert) -> None:
        """Save an alert to the repository"""
        pass
        
    @abstractmethod
    async def get_active_alerts(self) -> List[Alert]:
        """Get all active (unacknowledged) alerts"""
        pass
