from typing import Optional
import nextcord
from .base_factory import BaseFactory

class MenuFactory(BaseFactory):
    def create_role_select(self, 
        custom_id: str,
        placeholder: str = "Select roles",
        min_values: int = 1,
        max_values: int = 1
    ) -> nextcord.ui.RoleSelect:
        return nextcord.ui.RoleSelect(
            custom_id=custom_id,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values
        )

    def create_user_select(self, 
        custom_id: str,
        placeholder: str = "Select users"
    ) -> nextcord.ui.UserSelect:
        return nextcord.ui.UserSelect(
            custom_id=custom_id,
            placeholder=placeholder
        )