import nextcord
from typing import Dict, Optional, Callable
from ......common.selectors.base_selector import BaseSelector

class StatusSelector(BaseSelector):
    """Status selection implementation"""
    
    def __init__(
        self,
        status_emojis: Dict[str, str],
        status_names: Dict[str, str],
        current_status: Optional[str] = None,
        callback: Optional[Callable] = None
    ):
        options = [
            nextcord.SelectOption(
                label=status_names.get(status, status.capitalize()),
                emoji=emoji,
                value=status,
                default=status == current_status
            )
            for status, emoji in status_emojis.items()
        ]
        
        super().__init__(
            options=options,
            placeholder="Status wählen",
            custom_id="status_select",
            callback=callback
        )
