import logging
from typing import Any, Callable, Dict, List, Optional
from ..service.service_factory import ServiceFactory
from ..service.task_factory import TaskFactory
from ..discord.channel_factory import ChannelFactory
from ..discord.thread_factory import ThreadFactory
from ..discord_ui.message_factory import MessageFactory
from ..discord_ui.button_factory import ButtonFactory
from ..discord_ui.view_factory import ViewFactory
from ..discord_ui.menu_factory import MenuFactory
from ..discord_ui.modal_factory import ModalFactory
from .dashboard_factory import DashboardFactory
from core.services.logging.logging_commands import logger

logger = logging.getLogger(__name__)

class BotComponentFactory:
    def __init__(self, bot):
        self.bot = bot
        self.factories: Dict[str, Any] = {
            'service': ServiceFactory(bot),
            'task': TaskFactory(bot),
            'channel': ChannelFactory(bot),
            'thread': ThreadFactory(bot),
            'message': MessageFactory(bot),
            'button': ButtonFactory(bot),
            'view': ViewFactory(bot),
            'menu': MenuFactory(bot),
            'modal': ModalFactory(bot),
            'dashboard': DashboardFactory(bot)
        }
        self._component_creators = {}  # Stores dynamically registered component creators
        
    def register_component_creator(self, component_type: str, creator_func: Callable):
        """Dynamically register new component types"""
        self._component_creators[component_type] = creator_func
        logger.debug(f"Registered creator for component type: {component_type}")

    def create_component(self, component_type: str, name: str, **kwargs):
        """Dynamically create components"""
        if component_type not in self._component_creators:
            raise ValueError(f"Unknown component type: {component_type}")
            
        creator = self._component_creators[component_type]
        return creator(name, **kwargs)

    def create_service(self, name: str, setup_func, **kwargs):
        """Create a service using the service factory"""
        return self.factories['service'].create(name, setup_func, **kwargs)
    
    def create_task(self, name: str, task_func, *args, **kwargs):
        """Create a task using the task factory"""
        return self.factories['task'].create(name, task_func, *args, **kwargs)

    def create_command(self, name: str, command_cog, **kwargs):
        """Create a command component"""
        return {
            'name': name,
            'cog': command_cog,
            'type': 'command',
            'config': kwargs,
            'guild_only': kwargs.get('guild_only', False)
        }
        
    def create_middleware(self, name: str, middleware_cog, **kwargs):
        """Create a middleware component"""
        return {
            'name': name,
            'cog': middleware_cog,
            'type': 'middleware',
            'config': kwargs,
            'priority': kwargs.get('priority', 5)  # Higher number = higher priority
        }
        
    def batch_create_services(self, service_configs: List[Dict]) -> List[Dict]:
        """Create multiple services from a list of configurations"""
        services = []
        for config in service_configs:
            service = self.create_service(
                config['name'], 
                config['setup'], 
                **config.get('config', {})
            )
            services.append(service)
        return services
        
    def batch_create_tasks(self, task_configs: List[Dict]) -> List[Dict]:
        """Create multiple tasks from a list of configurations"""
        tasks = []
        for config in task_configs:
            task = self.create_task(
                config['name'], 
                config['func'], 
                *config.get('args', []),
                **config.get('config', {})
            )
            tasks.append(task)
        return tasks

    def get_component(self, factory_type: str, name: str):
        """Get a registered component from specific factory"""
        if factory_type not in self.factories:
            raise ValueError(f"Unknown factory type: {factory_type}")
        return self.factories[factory_type].get(name)