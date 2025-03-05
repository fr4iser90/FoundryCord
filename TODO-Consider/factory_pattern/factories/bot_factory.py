import logging
from typing import Any, Callable, Dict

logger = logging.getLogger(__name__)

class BotComponentFactory:
    def __init__(self, bot):
        self.bot = bot
        self._component_creators = {}  # Speichert dynamisch registrierte Komponenten-Ersteller
        
    def register_component_creator(self, component_type: str, creator_func: Callable):
        """Dynamisch neue Komponenten-Typen registrieren"""
        self._component_creators[component_type] = creator_func
        logger.debug(f"Registered creator for component type: {component_type}")

    def create_component(self, component_type: str, name: str, **kwargs):
        """Dynamisch Komponenten erstellen"""
        if component_type not in self._component_creators:
            raise ValueError(f"Unknown component type: {component_type}")
            
        creator = self._component_creators[component_type]
        return creator(name, **kwargs)

    # Basis-Komponenten als Convenience-Methoden
    def create_service(self, name: str, setup_func, **kwargs):
        """Erstellt einen Service"""
        return {
            'name': name,
            'setup': setup_func,
            'type': 'service',
            'config': kwargs
        }
    
    def create_task(self, name: str, task_func, *args, **kwargs):
        """Erstellt einen Task"""
        return {
            'name': name,
            'func': task_func,
            'args': args,
            'type': 'task',
            'config': kwargs
        }

    def create_command(self, name: str, command_cog, **kwargs):
        """Erstellt ein Command"""
        return {
            'name': name,
            'cog': command_cog,
            'type': 'command',
            'config': kwargs
        }