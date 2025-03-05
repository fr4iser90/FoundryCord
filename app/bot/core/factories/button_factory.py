from typing import Optional
import nextcord
from .base_factory import BaseFactory

class ButtonFactory(BaseFactory):
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