from typing import List, Dict, Any, Optional
import nextcord

class ViewFactory:
    """Factory for creating UI Views"""
    
    def __init__(self, bot):
        self.bot = bot
        
    def create_view(self, timeout: Optional[float] = 180) -> nextcord.ui.View:
        """Create a basic view with optional timeout"""
        view = nextcord.ui.View(timeout=timeout)
        return view
        
    def add_button(self, view: nextcord.ui.View, button_config: Dict[str, Any]) -> nextcord.ui.View:
        """Add a button to a view based on configuration"""
        # Use late binding to avoid circular import
        from .button_factory import ButtonFactory
        
        # Get the button factory
        button_factory = ButtonFactory(self.bot)
        
        # Create the button based on configuration
        button_type = button_config.get('type', 'primary')
        if button_type == 'confirm':
            button = button_factory.create_confirm_button(
                label=button_config.get('label', 'Confirm'),
                custom_id=button_config.get('custom_id')
            )
        elif button_type == 'cancel':
            button = button_factory.create_cancel_button(
                label=button_config.get('label', 'Cancel'),
                custom_id=button_config.get('custom_id')
            )
        else:
            button = button_factory.create_button(
                label=button_config.get('label', 'Button'),
                style=button_config.get('style', nextcord.ButtonStyle.primary),
                custom_id=button_config.get('custom_id')
            )
            
        # Add the button to the view
        view.add_item(button)
        return view

    def create_confirm_view(self, callback) -> nextcord.ui.View:
        view = nextcord.ui.View(timeout=180)
        view.add_item(self.button_factory.create_confirm_button())
        view.add_item(self.button_factory.create_cancel_button())
        return view

    def create_pagination_view(self, pages: List[nextcord.Embed]) -> nextcord.ui.View:
        view = nextcord.ui.View(timeout=300)
        # Pagination Logik hier
        return view

    def create(self, name: str, **kwargs) -> Dict[str, Any]:
        """Implementation of abstract create method from BaseFactory"""
        view = nextcord.ui.View(
            timeout=kwargs.get('timeout', 180)
        )
        
        # Add any components from kwargs
        if 'components' in kwargs:
            for component in kwargs['components']:
                view.add_item(component)
                
        return {
            'name': name,
            'view': view,
            'type': 'view',
            'config': kwargs
        }