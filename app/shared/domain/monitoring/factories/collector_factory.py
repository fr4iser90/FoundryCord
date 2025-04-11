"""Factory for creating monitoring collectors"""
from abc import ABC, abstractmethod
from typing import Dict, Any

class CollectorFactory(ABC):
    """Abstract factory for creating monitoring collectors"""
    
    @abstractmethod
    def create_system_collector(self, **kwargs: Dict[str, Any]):
        """Create a system metrics collector"""
        pass
    
    @abstractmethod
    def create_service_collector(self, **kwargs: Dict[str, Any]):
        """Create a service metrics collector"""
        pass 