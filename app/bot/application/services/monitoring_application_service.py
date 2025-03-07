from domain.monitoring.services.metric_service import MetricService
from domain.monitoring.services.alert_service import AlertService

class MonitoringApplicationService:
    def __init__(self, metric_service: MetricService, alert_service: AlertService):
        self.metric_service = metric_service
        self.alert_service = alert_service
    
    async def get_full_system_status(self):
        """Get full system status data for UI"""
        # Collect latest metrics
        metrics = await self.metric_service.collect_and_store_metrics()
        
        # Check for alerts
        alerts = await self.alert_service.check_metrics_for_alerts(metrics)
        
        # Format data for UI
        return self._format_data_for_ui(metrics, alerts)
    
    def _format_data_for_ui(self, metrics, alerts):
        # Convert domain objects to a dict structure suitable for UI
        # This is where you'd transform the domain objects to match
        # what your Discord commands expect
        pass