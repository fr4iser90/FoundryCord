from typing import Dict, Type
from app.bot.domain.monitoring.collectors.interfaces.collector_interface import CollectorInterface
from app.bot.infrastructure.monitoring.collectors.service.impl import ServiceCollector
from app.bot.infrastructure.monitoring.collectors.system.impl import SystemCollector

class CollectorFactory:
    def __init__(self):
        self._collectors: Dict[str, Type[CollectorInterface]] = {
            'service': ServiceCollector,
            'system': SystemCollector
        }
    
    def create(self, collector_type: str) -> CollectorInterface:
        if collector_type not in self._collectors:
            raise ValueError(f"Unknown collector type: {collector_type}")
        return self._collectors[collector_type]()