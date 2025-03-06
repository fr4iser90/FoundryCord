from typing import List, Dict, Any
import nextcord
from ..base.base_factory import BaseFactory

class ModalFactory(BaseFactory):
    def create_input_modal(self,
        title: str,
        custom_id: str,
        fields: List[Dict[str, Any]]
    ) -> nextcord.ui.Modal:
        class CustomModal(nextcord.ui.Modal):
            def __init__(self):
                super().__init__(title=title, custom_id=custom_id)
                for field in fields:
                    self.add_item(
                        nextcord.ui.TextInput(
                            label=field['label'],
                            custom_id=field['id'],
                            style=field.get('style', nextcord.TextInputStyle.short),
                            placeholder=field.get('placeholder', ''),
                            required=field.get('required', True)
                        )
                    )
        return CustomModal()

    def create(self, name: str, **kwargs) -> Dict[str, Any]:
        """Implementation of abstract create method from BaseFactory"""
        modal = self.create_input_modal(
            title=kwargs.get('title', name),
            custom_id=kwargs.get('custom_id', f"{name}_modal"),
            fields=kwargs.get('fields', [])
        )
        
        return {
            'name': name,
            'modal': modal,
            'type': 'modal',
            'config': kwargs
        }