from domain.monitoring.repositories.monitoring_repository import MonitoringRepository
from domain.monitoring.models.metric import Metric
from domain.monitoring.models.alert import Alert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..models.database_models import MetricModel, AlertModel

class MonitoringRepositoryImpl(MonitoringRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def save_metric(self, metric: Metric) -> None:
        db_metric = MetricModel(
            name=metric.name,
            value=metric.value,
            unit=metric.unit,
            timestamp=metric.timestamp,
            metadata=metric.metadata
        )
        self.session.add(db_metric)
        await self.session.commit()
    
    # Implement other methods...