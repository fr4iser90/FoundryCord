from ..base.base_factory import BaseFactory
from typing import Callable, Dict, Any

class ServiceFactory(BaseFactory):
    def create(self, name: str, setup_func: Callable, **kwargs) -> Dict[str, Any]:
        """Create a service component"""
        service = {
            'name': name,
            'setup': setup_func,
            'type': 'service',
            'config': kwargs,
            'priority': kwargs.get('priority', 'normal')
        }
        self.register(name, service)
        return service