from typing import Optional, Dict, Any
import nextcord
from ..base.base_factory import BaseFactory

class ButtonFactory(BaseFactory):
    def create(self, name: str, **kwargs) -> Dict[str, Any]:
        """Implementation of abstract create method from BaseFactory"""
        button_type = kwargs.get('button_type', 'confirm')
        
        if button_type == 'confirm':
            button = self.create_confirm_button(
                custom_id=kwargs.get('custom_id', f"{name}_confirm")
            )
        elif button_type == 'cancel':
            button = self.create_cancel_button(
                custom_id=kwargs.get('custom_id', f"{name}_cancel")
            )
        elif button_type == 'link':
            button = self.create_link_button(
                label=kwargs.get('label', name),
                url=kwargs.get('url', '')
            )
        else:
            raise ValueError(f"Unknown button type: {button_type}")

        return {
            'name': name,
            'button': button,
            'type': 'button',
            'config': kwargs
        }

    def create_confirm_button(self, custom_id: str = "confirm") -> nextcord.ui.Button:
        return nextcord.ui.Button(
            style=nextcord.ButtonStyle.green,
            label="Confirm",
            custom_id=custom_id,
            emoji="✅"
        )

    def create_cancel_button(self, custom_id: str = "cancel") -> nextcord.ui.Button:
        return nextcord.ui.Button(
            style=nextcord.ButtonStyle.red,
            label="Cancel",
            custom_id=custom_id,
            emoji="❌"
        )

    def create_link_button(self, label: str, url: str) -> nextcord.ui.Button:
        return nextcord.ui.Button(
            style=nextcord.ButtonStyle.link,
            label=label,
            url=url
        )