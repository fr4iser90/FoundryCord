import logging
import importlib
from collections.abc import Awaitable
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING
from app.bot.infrastructure.factories.service_factory import ServiceFactory
from app.shared.interfaces.logging.api import get_bot_logger

from app.bot.infrastructure.config.registries.component_registry import ComponentRegistry
from app.bot.infrastructure.factories.component_factory import ComponentFactory
from app.bot.infrastructure.factories.task_factory import TaskFactory

# Use TYPE_CHECKING to avoid circular import during runtime
if TYPE_CHECKING:
    from app.bot.infrastructure.startup.bot import FoundryCord


logger = get_bot_logger()

class BotComponentFactory:
    """
    Composite Factory attempting to provide access to various factories and registries.
    Consider if its role overlaps too much with ServiceFactory.
    """

    def __init__(self, bot: 'FoundryCord'):
        """Initialize the factory with a bot instance."""
        self.bot = bot
        self.initialized = False
        self.settings = {}
        self._load_settings()

        self.component_registry: Optional[ComponentRegistry] = None
        self.data_source_registry = None
        self.service_factory: Optional[ServiceFactory] = None
        self.task_factory: Optional[TaskFactory] = None
        self.workflow_factory = None
        self.manager_factory = None
        self.repository_factory = None
        self.interface_factories: Dict[str, Any] = {}
        self.service_factories: Dict[str, Any] = {}

        if hasattr(self.bot, 'service_factory') and self.bot.service_factory is not None:
             self.service_factory = self.bot.service_factory
             logger.debug(f"[BotComponentFactory.__init__] Assigned existing service factory: {type(self.service_factory).__name__}")
        else:
             logger.warning("[BotComponentFactory.__init__] Bot has no service_factory attribute during init.")


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

    async def initialize_dependencies(self):
         """Initializes or retrieves dependent factories and registries."""
         logger.info("[BotComponentFactory] Initializing dependencies...")
         if not self.service_factory:
              logger.error("[BotComponentFactory] Cannot initialize dependencies: ServiceFactory is missing.")
              return False

         self.component_registry = self.service_factory.get_service('component_registry')
         if not self.component_registry:
              logger.error("[BotComponentFactory] Failed to get ComponentRegistry from ServiceFactory.")
         else:
              logger.info(f"[BotComponentFactory] ComponentRegistry retrieved: {type(self.component_registry).__name__}")

         self.data_source_registry = self.service_factory.get_service('data_source_registry')
         if not self.data_source_registry:
              logger.warning("[BotComponentFactory] Failed to get DataSourceRegistry from ServiceFactory (might be expected if not used/registered).")
         else:
              logger.info(f"[BotComponentFactory] DataSourceRegistry retrieved: {type(self.data_source_registry).__name__}")

         self.task_factory = self.service_factory.get_service('task_factory')
         if not self.task_factory:
              logger.info("[BotComponentFactory] TaskFactory not found as service, creating new instance.")
              self.task_factory = TaskFactory(self.bot)
              # Optionally register it back?
              # self.service_factory.register_service('task_factory', self.task_factory)
         else:
              logger.info(f"[BotComponentFactory] TaskFactory retrieved: {type(self.task_factory).__name__}")

         self.interface_factories = self._initialize_interface_factories()
         logger.info("[BotComponentFactory] Dependencies initialized.")
         self.initialized = True
         return True

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

    def _initialize_interface_factories(self) -> Dict[str, Any]:
        """Initialize UI component factories by retrieving them from the ServiceFactory."""
        if not self.component_registry:
             logger.error("Cannot initialize interface factories: ComponentRegistry not available.")
             return {}
        if not self.service_factory:
             logger.error("Cannot initialize interface factories: ServiceFactory not available.")
             return {}

        # Retrieve UI factories from ServiceFactory instead of direct import/instantiation
        button_factory = self.service_factory.get_service('button_factory')
        embed_factory = self.service_factory.get_service('embed_factory')

        if not button_factory:
            logger.warning("_initialize_interface_factories: ButtonFactory not found in ServiceFactory.")
        if not embed_factory:
            logger.warning("_initialize_interface_factories: EmbedFactory not found in ServiceFactory.")

        return {
            'button': button_factory, # Use retrieved instance (or None if not found)
            'embed': embed_factory,   # Use retrieved instance (or None if not found)
            'dashboard': self.component_registry,
        }

    # --- Methods below might need review based on the final role of this factory ---

    def get_factory(self, factory_type: str):
        """Get a factory by type."""
        # This relies on self.factories which doesn't seem to be populated consistently.
        # Consider if this method is still needed or should use self.interface_factories etc.
        logger.warning("BotComponentFactory.get_factory might be unreliable.")
        if factory_type in self.interface_factories:
             return self.interface_factories[factory_type]
        # Add checks for other factory types if necessary
        return None

    def create(self, factory_type: str, *args, **kwargs):
        """Create a component using the specified factory."""
        factory = self.get_factory(factory_type)

        if not factory:
            logger.error(f"Factory not found for type: {factory_type}")
            return None

        # Assuming the retrieved factory has a 'create' method
        if hasattr(factory, 'create') and callable(factory.create):
            return factory.create(*args, **kwargs)
        else:
             logger.error(f"Retrieved factory for type '{factory_type}' has no 'create' method.")
             return None

    def create_service(self, service_type: str, *args, **kwargs) -> Optional[Any]:
         """Creates a service using the bot's main ServiceFactory."""
         if not self.service_factory:
              logger.error("Cannot create service: ServiceFactory not available.")
              return None
         return self.service_factory.create_or_get(service_type, *args, **kwargs)

    def create_task(self, task_name: str, coro_func: Callable[..., Awaitable], *args, **kwargs):
         """Create a task using the Task factory."""
         if not self.task_factory:
              logger.error("Cannot create task: TaskFactory not available.")
              return None
         return self.task_factory.create(task_name, coro_func, *args, **kwargs)

    def create_command(self, name: str, command_cog, **kwargs):
        """Create a command component dictionary."""
        return {
            'name': name,
            'cog': command_cog,
            'type': 'command',
            'config': kwargs,
            'guild_only': kwargs.get('guild_only', False)
        }

    def create_middleware(self, name: str, middleware_cog, **kwargs):
        """Create a middleware component dictionary."""
        return {
            'name': name,
            'cog': middleware_cog,
            'type': 'middleware',
            'config': kwargs,
            'priority': kwargs.get('priority', 5)
        }

    def batch_create_services(self, service_configs: List[Dict]) -> List[Any]:
        """Create multiple services from a list of configurations using the main ServiceFactory."""
        services = []
        for config in service_configs:
            service = self.create_service(
                config['name'], # Assuming 'name' is the service_type key
                # Pass other args/kwargs if needed by create_or_get
                **config.get('config', {})
            )
            if service:
                services.append(service)
        return services

    def batch_create_tasks(self, task_configs: List[Dict]) -> List[Any]:
        """Create multiple tasks from a list of configurations using the TaskFactory."""
        tasks = []
        for config in task_configs:
            task = self.create_task(
                config['name'],
                config['func'], # Assuming 'func' holds the coroutine function
                *config.get('args', []),
                **config.get('config', {})
            )
            if task:
                tasks.append(task)
        return tasks