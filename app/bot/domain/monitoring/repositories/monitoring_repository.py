from abc import ABC, abstractmethod
from typing import List, Optional
from app.shared.infrastructure.database.models import MetricModel, AlertModel
from datetime import datetime
from app.bot.domain.monitoring.models import Metric, Alert
 

class MonitoringRepository(ABC):
    @abstractmethod
    async def save_metric(self, metric: MetricModel) -> None:
        """Save a metric to the repository"""
        pass
        
    @abstractmethod
    async def get_metrics(self, name: str, limit: int = 100) -> List[MetricModel]:
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

    @abstractmethod
    async def acknowledge_alert(self, alert_id: int) -> Optional[Alert]:
        """Mark an alert as acknowledged"""
        pass
    
    @abstractmethod
    async def resolve_alert(self, alert_id: int) -> Optional[Alert]:
        """Mark an alert as resolved"""
        pass
