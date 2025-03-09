import nextcord
from typing import Callable, Optional
from interfaces.dashboards.components.common.buttons.base_button import BaseButton

class GameServerButton(BaseButton):
    """Button for game server dashboard"""
    
    def __init__(
        self, 
        label: str, 
        custom_id: str = None,
        emoji: str = None,
        callback: Callable = None,
        style: nextcord.ButtonStyle = nextcord.ButtonStyle.primary,
        is_disabled: bool = False,
        row: Optional[int] = None
    ):
        super().__init__(
            label=label,
            custom_id=custom_id,
            emoji=emoji,
            callback=callback,
            style=style,
            is_disabled=is_disabled,
            row=row
        )
    
    def _get_button_style(self) -> nextcord.ButtonStyle:
        """Determine button style based on status or default"""
        if self.server_status == "online":
            return nextcord.ButtonStyle.success
        elif self.server_status == "offline":
            return nextcord.ButtonStyle.danger
        elif self.server_status == "warning":
            return nextcord.ButtonStyle.secondary
        else:
            return self.style or nextcord.ButtonStyle.primary