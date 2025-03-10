from infrastructure.database.models import MetricModel, AlertModel
from ..collectors import system_collector, service_collector
from ..repositories.monitoring_repository import MonitoringRepository
import logging

logger = logging.getLogger('homelab_bot')

class MetricService:
    def __init__(self, repository: MonitoringRepository):
        self.repository = repository
        
    async def collect_and_store_metrics(self):
        """Collect all metrics and store them in repository"""
        logger.info("Collecting and storing all metrics...")
        
        # Collect system metrics
        system_metrics = await system_collector.collect_all()
        logger.info(f"Collected {len(system_metrics)} system metrics")
        
        # Collect service metrics
        service_metrics = await service_collector.collect_all()
        logger.info(f"Collected {len(service_metrics)} service metrics")
        
        # Store all metrics
        all_metrics = system_metrics + service_metrics
        for metric in all_metrics:
            await self.repository.save_metric(metric)
            
        logger.info(f"Stored {len(all_metrics)} metrics in repository")
        return all_metrics
    
    async def get_system_overview(self):
        """Get a system overview with the latest metrics"""
        # Implementation depends on your specific needs
        pass

       data = await collect_service_data()