from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import discord

class BaseComponent(ABC):
    """Base class for all dashboard UI components"""
    
    def __init__(self, component_id: str, config: Dict[str, Any]):
        self.component_id = component_id
        self.config = config
    
    @abstractmethod
    async def create(self, ctx: Optional[discord.Interaction] = None) -> Any:
        """Create the component for display"""
        pass
    
    @abstractmethod
    async def update(self, data: Any, ctx: Optional[discord.Interaction] = None) -> Any:
        """Update the component with new data"""
        pass
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """Get a configuration value with fallback to default"""
        return self.config.get(key, default) 