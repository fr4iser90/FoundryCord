from typing import List, Dict, Any
import nextcord
from app.bot.infrastructure.factories.base.base_factory import BaseFactory
from . import ButtonFactory

class ViewFactory(BaseFactory):
    def __init__(self, bot):
        super().__init__(bot)
        self.button_factory = ButtonFactory(bot)

    def create_confirm_view(self, callback) -> nextcord.ui.View:
        view = nextcord.ui.View(timeout=180)
        view.add_item(self.button_factory.create_confirm_button())
        view.add_item(self.button_factory.create_cancel_button())
        return view

    def create_pagination_view(self, pages: List[nextcord.Embed]) -> nextcord.ui.View:
        view = nextcord.ui.View(timeout=300)
        # Pagination Logik hier
        return view

    def create(self, name: str, **kwargs) -> Dict[str, Any]:
        """Implementation of abstract create method from BaseFactory"""
        view = nextcord.ui.View(
            timeout=kwargs.get('timeout', 180)
        )
        
        # Add any components from kwargs
        if 'components' in kwargs:
            for component in kwargs['components']:
                view.add_item(component)
                
        return {
            'name': name,
            'view': view,
            'type': 'view',
            'config': kwargs
        }