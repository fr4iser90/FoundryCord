import logging
from typing import Any, Callable, Dict, List, Optional
from ..service.service_factory import ServiceFactory
from ..service.task_factory import TaskFactory
from ..discord.channel_factory import ChannelFactory
from ..discord.thread_factory import ThreadFactory
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

logger = logging.getLogger(__name__)

from app.bot.infrastructure.factories.component_registry_factory import ComponentRegistryFactory
from app.bot.infrastructure.factories.data_source_registry_factory import DataSourceRegistryFactory
from app.bot.infrastructure.factories.service_factory import ServiceFactory
from app.bot.infrastructure.factories.task_factory import TaskFactory

# Import specific factories (not BaseFactory)
from app.bot.interfaces.dashboards.components.factories.button_factory import ButtonFactory
from app.bot.interfaces.dashboards.components.factories.embed_factory import EmbedFactory

class BotComponentFactory:
    """Factory for creating bot components."""
    
    def __init__(self, bot):
        """Initialize the factory with a bot instance."""
        self.bot = bot
        self.initialized = False
        self.settings = {}
        self._load_settings()
        
    def _load_settings(self):
        """Load factory settings."""
        try:
            # In the future, we could load these from a config file or database
            self.settings = {
                'enable_slash_commands': True,
                'enable_dashboards': True,
                'enable_monitoring': True,
                'development_mode': True
            }
            self.initialized = True
        except Exception as e:
            logger.error(f"Error loading factory settings: {e}")
            self.initialized = False
            
    async def create_service_factory(self):
        """Create a service factory."""
        from app.bot.infrastructure.factories.composite.service_factory import ServiceFactory
        return ServiceFactory(self.bot)
        
    async def create_workflow_factory(self):
        """Create a workflow factory."""
        from app.bot.infrastructure.factories.composite.workflow_factory import WorkflowFactory
        return WorkflowFactory(self.bot)
        
    async def create_manager_factory(self):
        """Create a manager factory."""
        from app.bot.infrastructure.factories.composite.manager_factory import ManagerFactory
        return ManagerFactory(self.bot)
        
    async def create_repository_factory(self):
        """Create a repository factory."""
        from app.bot.infrastructure.factories.composite.repository_factory import RepositoryFactory
        return RepositoryFactory(self.bot)

    def initialize_registries(self):
        """Initialize component and data source registries."""
        # These will be initialized properly during the bot lifecycle
        self.component_registry = ComponentRegistryFactory(self.bot)
        self.data_source_registry = DataSourceRegistryFactory(self.bot)
        self.service_factory = ServiceFactory(self.bot)
        self.task_factory = TaskFactory(self.bot)
    
    def _initialize_interface_factories(self) -> Dict[str, Any]:
        """Initialize UI component factories."""
        return {
            'button': ButtonFactory(self.bot),
            'embed': EmbedFactory(self.bot),
            'dashboard': self.component_registry,  # Use component registry for dashboards
        }
    
    def _initialize_service_factories(self) -> Dict[str, Any]:
        """Initialize service factories."""
        return {
            'data_source': self.data_source_registry,
        }
    
    def get_factory(self, factory_type: str):
        """Get a factory by type."""
        return self.factories.get(factory_type)
    
    def create(self, factory_type: str, *args, **kwargs):
        """Create a component using the specified factory."""
        factory = self.get_factory(factory_type)
        
        if not factory:
            logger.error(f"Factory not found: {factory_type}")
            return None
            
        return factory.create(*args, **kwargs)

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