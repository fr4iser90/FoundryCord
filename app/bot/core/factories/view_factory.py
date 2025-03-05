from typing import List, Optional, Callable
import nextcord
from .base_factory import BaseFactory
from .button_factory import ButtonFactory

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