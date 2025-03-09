import nextcord
from typing import Optional, Callable
from ......common.selectors.base_selector import BaseSelector

class PrioritySelector(BaseSelector):
    """Priority selection implementation"""
    
    def __init__(
        self,
        current_priority: Optional[str] = None,
        callback: Optional[Callable] = None
    ):
        options = [
            nextcord.SelectOption(
                label="Hoch",
                emoji="🔴",
                value="high",
                default="high" == current_priority
            ),
            nextcord.SelectOption(
                label="Mittel",
                emoji="🟡",
                value="medium",
                default="medium" == current_priority
            ),
            nextcord.SelectOption(
                label="Niedrig",
                emoji="🟢",
                value="low",
                default="low" == current_priority
            )
        ]
        
        super().__init__(
            options=options,
            placeholder="Priorität wählen",
            custom_id="priority_select",
            callback=callback
        )
