from app.shared.interface.logging.api import get_bot_logger
import nextcord

# Import necessary managers, workflows, services, factories etc.
from app.bot.core.lifecycle_manager import BotLifecycleManager
from app.bot.core.shutdown_handler import ShutdownHandler
from app.bot.core.workflow_manager import BotWorkflowManager
from app.bot.core.workflows import (
    DatabaseWorkflow, GuildWorkflow, CategoryWorkflow, ChannelWorkflow,
    DashboardWorkflow, TaskWorkflow, UserWorkflow, GuildTemplateWorkflow
)
from app.bot.application.services.bot_control_service import BotControlService
from app.bot.application.services.dashboard.component_loader_service import ComponentLoaderService
from app.bot.application.services.dashboard.dashboard_data_service import DashboardDataService
from app.bot.infrastructure.factories.component_registry import ComponentRegistry
from app.bot.infrastructure.factories.component_factory import ComponentFactory
from app.bot.infrastructure.internal_api.server import InternalAPIServer
from app.bot.interfaces.dashboards.components.common.embeds.dashboard_embed import DashboardEmbed
from app.bot.interfaces.dashboards.components.common.embeds.error_embed import ErrorEmbed
from app.bot.interfaces.dashboards.components.common.buttons.generic_button import GenericButtonComponent
from app.bot.infrastructure.factories.service_factory import ServiceFactory
from app.bot.infrastructure.factories.data_source_registry import DataSourceRegistry

logger = get_bot_logger()

def setup_core_components(bot):
    """Initializes core managers, registries, factories, and other essential components."""
    logger.info("Setting up core components...")
    try:
        bot.lifecycle = BotLifecycleManager()
        bot.workflow_manager = BotWorkflowManager()
        bot.component_registry = ComponentRegistry()
        bot.data_source_registry = DataSourceRegistry(bot)
        bot.component_factory = ComponentFactory(bot.component_registry)
        bot.shutdown_handler = ShutdownHandler(bot)
        bot.control_service = BotControlService(bot)
        bot.internal_api_server = InternalAPIServer(bot)
        bot._default_components_registered = False
        logger.info("Core components setup complete (incl. DataSourceRegistry).")
    except Exception as e:
        logger.critical(f"Failed to setup core components: {e}", exc_info=True)
        raise

def register_workflows(bot):
    """Instantiates and registers all workflows with the WorkflowManager."""
    if not bot.workflow_manager:
        logger.critical("WorkflowManager not initialized before register_workflows call.")
        return

    logger.info("Setting up and registering workflows...")
    try:
        # Create workflow instances (some require other workflows/bot)
        # Ensure dependencies like database_workflow are created first if needed by others
        # For simplicity here, assume bot object has necessary refs, or pass explicitly
        database_workflow = DatabaseWorkflow(bot)
        guild_workflow = GuildWorkflow(database_workflow, bot=bot)
        category_workflow = CategoryWorkflow(database_workflow, bot=bot)
        channel_workflow = ChannelWorkflow(database_workflow, category_workflow, bot=bot)
        dashboard_workflow = DashboardWorkflow(database_workflow) # bot passed during its initialize
        task_workflow = TaskWorkflow(database_workflow, bot)
        user_workflow = UserWorkflow(database_workflow, bot)
        guild_template_workflow = GuildTemplateWorkflow(database_workflow, guild_workflow, bot)

        # Assign workflows to bot instance for potential direct access (optional)
        bot.database_workflow = database_workflow
        bot.guild_workflow = guild_workflow
        bot.category_workflow = category_workflow
        bot.channel_workflow = channel_workflow
        bot.dashboard_workflow = dashboard_workflow
        bot.task_workflow = task_workflow
        bot.user_workflow = user_workflow
        bot.guild_template_workflow = guild_template_workflow

        # Register workflows with dependencies
        bot.workflow_manager.register_workflow(database_workflow)
        bot.workflow_manager.register_workflow(guild_workflow, ['database'])
        bot.workflow_manager.register_workflow(guild_template_workflow, ['database', 'guild'])
        bot.workflow_manager.register_workflow(category_workflow, ['database'])
        bot.workflow_manager.register_workflow(channel_workflow, ['database', 'category'])
        bot.workflow_manager.register_workflow(dashboard_workflow, ['database'])
        bot.workflow_manager.register_workflow(task_workflow, ['database'])
        bot.workflow_manager.register_workflow(user_workflow, ['database'])

        # Set explicit initialization order
        bot.workflow_manager.set_initialization_order([
            'database', 'guild', 'guild_template', 'category', 'channel',
            'dashboard', 'task', 'user'
        ])
        logger.info("Workflows registered and order set.")
    except Exception as e:
        logger.critical(f"Failed to register workflows: {e}", exc_info=True)

def register_default_components(bot):
    """Registers the default UI components AND necessary generic types."""
    if not bot.component_registry:
        logger.error("Cannot register default components: bot.component_registry is None.")
        return
    if bot._default_components_registered:
        logger.debug("Default components already registered.")
        return

    logger.info("Registering default and generic components...")
    try:
        # CORE EMBED COMPONENTS
        bot.component_registry.register_component(
            component_type="dashboard_embed",
            component_class=DashboardEmbed,
            description="Standard dashboard embed",
            default_config={
                "title": "Dashboard",
                "color": nextcord.Color.blurple().value,
                "timestamp": True
            }
        )
        bot.component_registry.register_component(
            component_type="error_embed",
            component_class=ErrorEmbed,
            description="Embed for displaying errors",
            default_config={
                "title": "Error",
                "description": "An error occurred",
                "color": nextcord.Color.red().value,
                "error_code": None
            }
        )

        # Register IMPLEMENTATIONS FOR GENERIC DB TYPES
        logger.info("Registering implementation classes for generic database component types...")

        # Register 'embed' type -> Use the existing DashboardEmbed class
        bot.component_registry.register_component(
            component_type="embed",
            component_class=DashboardEmbed,
            description="Generic embed component implementation (uses DashboardEmbed)"
        )
        logger.info("Registered 'embed' type to use DashboardEmbed class.")

        # Register 'button' type -> Use the new GenericButtonComponent class
        bot.component_registry.register_component(
            component_type="button",
            component_class=GenericButtonComponent,
            description="Generic button component implementation"
        )
        logger.info("Registered 'button' type to use GenericButtonComponent class.")

        bot._default_components_registered = True
        logger.info(f"Finished registering default/generic components. Total implementation types registered: {len(bot.component_registry.get_all_component_types())}")
    except NameError as ne:
        logger.error(f"Failed to register a component - Class not found (NameError): {ne}. Ensure component classes are imported.", exc_info=True)
    except Exception as e:
        logger.error(f"Error registering default/generic components: {e}", exc_info=True)

def register_core_services(service_factory: ServiceFactory, bot):
    """Registers essential services with the ServiceFactory SYNCHRONOUSLY."""
    if not service_factory:
        logger.error("Service Factory is None. Cannot register core services.")
        return

    logger.info("Registering core services with Service Factory (synchronous)...")
    try:
        # 1. Register ComponentRegistry
        if hasattr(bot, 'component_registry') and bot.component_registry:
            if hasattr(service_factory, 'register_service'):
                service_factory.register_service(
                    'component_registry',
                    bot.component_registry,
                    overwrite=True
                )
                logger.info("Registered service: component_registry")
            else:
                logger.error("service_factory is missing register_service method (ComponentRegistry).")
        else:
            logger.error("bot.component_registry not found. Cannot register.")

        # 2. Instantiate and Register DashboardDataService
        logger.debug("Instantiating DashboardDataService...")
        dashboard_data_service_instance = DashboardDataService(bot, service_factory)
        if hasattr(service_factory, 'register_service'):
            service_factory.register_service(
                'dashboard_data_service',
                dashboard_data_service_instance,
                overwrite=True
            )
            logger.info("Registered service: dashboard_data_service")
        else:
            logger.error("service_factory is missing register_service method (DashboardDataService).")

        # 3. Instantiate and Register ComponentLoaderService
        logger.debug("Instantiating ComponentLoaderService...")
        component_loader_instance = ComponentLoaderService(bot)
        if hasattr(service_factory, 'register_service') and hasattr(service_factory, 'has_service'):
            if not service_factory.has_service('component_loader'):
                service_factory.register_service(
                    'component_loader',
                    component_loader_instance,
                    overwrite=True
                )
                logger.info("Registered service: component_loader")
            else:
                logger.info("ComponentLoaderService already registered.")
        else:
            logger.error("Service Factory instance is missing expected registration methods.")

        # 4. Register DataSourceRegistry
        if hasattr(bot, 'data_source_registry') and bot.data_source_registry:
            if hasattr(service_factory, 'register_service'):
                service_factory.register_service(
                    'data_source_registry',
                    bot.data_source_registry,
                    overwrite=True
                )
                logger.info("Registered service: data_source_registry")
            else:
                logger.error("service_factory is missing register_service method (DataSourceRegistry).")
        else:
            logger.error("bot.data_source_registry not found. Cannot register as service.")

    except Exception as e:
        logger.error(f"Error registering core services SYNCHRONOUSLY in ServiceFactory: {e}", exc_info=True)
        raise

def setup_service_factory_and_register_core_services(bot):
    """Initializes the ServiceFactory and registers core services SYNCHRONOUSLY."""
    logger.info("Setting up Service Factory and registering core services in __init__...")
    try:
        # Create factory first
        bot.service_factory = ServiceFactory(bot)
        logger.info(f"ServiceFactory instantiated in __init__: {type(bot.service_factory).__name__}")
        # Then register services using the created factory
        register_core_services(bot.service_factory, bot)
        logger.info("Service Factory setup and core service registration complete.")
    except Exception as e:
        logger.critical(f"CRITICAL FAILURE during Service Factory setup in __init__: {e}", exc_info=True)
        raise RuntimeError("Failed to initialize core Service Factory") from e

async def setup_hook(bot):
    """
    Asynchronous setup hook called by nextcord after __init__ but before on_ready.
    KEEP THIS EMPTY regarding ServiceFactory.
    Use this for other async setup tasks if needed later (like loading cogs/extensions).
    """
    logger.info("Executing setup_hook (ServiceFactory initialization moved to __init__)...")
    pass
