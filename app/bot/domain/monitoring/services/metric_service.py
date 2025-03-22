from app.shared.infrastructure.models import MetricModel, AlertModel
from app.bot.infrastructure.monitoring.collectors.monitoring import collect_all, system_collect_all
from app.bot.infrastructure.repositories.monitoring_repository import MonitoringRepository
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()
from app.bot.infrastructure.monitoring.collectors.system import SystemCollector
from app.bot.infrastructure.monitoring.collectors.service import ServiceCollector


class MetricService:
    def __init__(self, repository: MonitoringRepository):
        self.repository = repository
        # Create collector instances or get them from a factory
        self.system_collector = SystemCollector()
        self.service_collector = ServiceCollector()
        
    async def collect_and_store_metrics(self):
        """Collect all metrics and store them in repository"""
        logger.info("Collecting and storing all metrics...")
        
        # Use instance variables instead of global collectors
        system_metrics = await self.system_collector.collect_all()
        logger.info(f"Collected {len(system_metrics)} system metrics")
        
        service_metrics = await self.service_collector.collect_all()
        logger.info(f"Collected {len(service_metrics)} service metrics")
        
        # Store all metrics
        all_metrics = system_metrics + service_metrics
        for metric in all_metrics:
            await self.repository.save_metric(metric)
            
        logger.info(f"Stored {len(all_metrics)} metrics in repository")
        return all_metrics
    
    async def get_system_overview(self):
        """Get a system overview with the latest metrics"""
        logger.info("Fetching system overview metrics...")
        
        try:
            # Collect system data
            system_data = await self.system_collector.collect_overview()
            
            # Collect service data
            service_data = await self.service_collector.collect_overview()
            
            # Format game server data for monitoring dashboard
            game_servers = {}
            if 'services' in service_data:
                for name, status in service_data['services'].items():
                    if '🎮' in name:
                        game_name = name.replace('🎮 ', '')
                        game_servers[game_name] = {
                            'online': 'Online' in status or '✅' in status,
                            'ports': self._extract_ports(status)
                        }
            
            # Combine all data for the dashboard
            overview = {
                'system': system_data,
                'services': service_data,
                'game_servers': game_servers
            }
            
            logger.info(f"System overview retrieved successfully with {len(game_servers)} game servers")
            return overview
            
        except Exception as e:
            logger.error(f"Error getting system overview: {e}")
            return {'system': {}, 'services': {}, 'game_servers': {}}
    
    def _extract_ports(self, status_text):
        """Extract port numbers from a service status text"""
        ports = []
        if "Port(s):" in status_text:
            try:
                ports_text = status_text.split("Port(s):")[1].strip()
                ports = [int(p.strip()) for p in ports_text.split(',') if p.strip().isdigit()]
            except (IndexError, ValueError):
                pass
        return ports