import nextcord
from typing import Optional, List, Callable
from .base_view import BaseView
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class DashboardView(BaseView):
    """Base class for all dashboard views"""
    
    def __init__(
        self,
        buttons: Optional[List[nextcord.ui.Button]] = None,
        selects: Optional[List[nextcord.ui.Select]] = None,
        timeout: Optional[int] = None
    ):
        super().__init__(timeout=timeout)
        
        if buttons:
            for button in buttons:
                self.add_item(button)
                
        if selects:
            for select in selects:
                self.add_item(select)
    
    def add_refresh_button(self, callback: Optional[Callable] = None):
        """Adds a standard refresh button"""
        from ..buttons import RefreshButton
        refresh_btn = RefreshButton(callback=callback)
        self.add_item(refresh_btn) 