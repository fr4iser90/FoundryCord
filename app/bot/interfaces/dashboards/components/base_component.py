"""Base component for dashboard UI elements."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, Awaitable
import nextcord

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class DashboardComponent(ABC):
    """Base class for dashboard components."""
    
    def __init__(self, bot, config: Dict[str, Any]):
        self.bot = bot
        self.config = config
        self.id = config.get("id")
        
    @abstractmethod
    async def render_to_embed(self, embed: nextcord.Embed, data: Any, config: Dict[str, Any]) -> None:
        """Render component to an embed."""
        pass
        
    @abstractmethod
    async def create_ui_component(self, view: nextcord.ui.View, data: Any, 
                                 config: Dict[str, Any], dashboard_id: str) -> Optional[nextcord.ui.Item]:
        """Create UI component for interactive view."""
        pass
        
    @abstractmethod
    async def on_interaction(self, interaction: nextcord.Interaction, data: Any, 
                           config: Dict[str, Any], dashboard_id: str) -> None:
        """Handle interaction with this component."""
        pass 