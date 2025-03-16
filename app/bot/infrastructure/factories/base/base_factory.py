from abc import ABC, abstractmethod
from typing import Any, Dict
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class BaseFactory(ABC):
    def __init__(self, bot):
        self.bot = bot
        self._registry = {}
        
    @abstractmethod
    def create(self, name: str, **kwargs) -> Dict[str, Any]:
        pass
        
    def register(self, key: str, component: Any) -> None:
        """Register a component in the factory registry"""
        self._registry[key] = component
        logger.debug(f"Registered {key} in {self.__class__.__name__}")
        
    def get(self, key: str) -> Any:
        """Get a registered component"""
        return self._registry.get(key)
        
    def validate_config(self, config: Dict) -> bool:
        """Validate component configuration"""
        return True