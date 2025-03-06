from typing import Optional, Dict, Any
import nextcord
from ..base.base_factory import BaseFactory

class MenuFactory(BaseFactory):
    def create(self, name: str, **kwargs) -> Dict[str, Any]:
        """Implementation of abstract create method from BaseFactory"""
        menu_type = kwargs.get('menu_type', 'role')
        if menu_type == 'role':
            menu = self.create_role_select(
                custom_id=kwargs.get('custom_id', name),
                placeholder=kwargs.get('placeholder', "Select roles"),
                min_values=kwargs.get('min_values', 1),
                max_values=kwargs.get('max_values', 1)
            )
        else:
            menu = self.create_user_select(
                custom_id=kwargs.get('custom_id', name),
                placeholder=kwargs.get('placeholder', "Select users")
            )
        
        return {
            'name': name,
            'menu': menu,
            'type': 'menu',
            'config': kwargs
        }

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