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

logger = get_bot_logger()

def setup_core_components(bot):
    """Initializes core managers, registries, factories, and other essential components."""
    logger.info("Setting up core components...")
    try:
        bot.lifecycle = BotLifecycleManager()
        bot.workflow_manager = BotWorkflowManager()
        bot.component_registry = ComponentRegistry()
        bot.component_factory = ComponentFactory(bot.component_registry)
        bot.shutdown_handler = ShutdownHandler(bot)
        bot.control_service = BotControlService(bot)
        bot.internal_api_server = InternalAPIServer(bot)
        # Initialize service_factory to None here, it will be set in setup_hook
        bot.service_factory = None
        bot._default_components_registered = False
        logger.info("Core components setup complete.")
    except Exception as e:
        logger.critical(f"Failed to setup core components: {e}", exc_info=True)
        # Optionally raise exception to halt bot startup

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
    """Registers the default UI components like standard embeds."""
    if not bot.component_registry:
        logger.error("Cannot register default components: bot.component_registry is None.")
        return
    if bot._default_components_registered:
        logger.debug("Default components already registered.")
        return

    logger.info("Registering default components...")
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
        bot._default_components_registered = True
        logger.info(f"Registered {len(bot.component_registry.get_all_component_types())} default components")
    except Exception as e:
        logger.error(f"Error registering default components: {e}", exc_info=True)

async def register_core_services(bot):
    """Registers essential services with the ServiceFactory after it's created."""
    # --- ADD DIAGNOSTIC LOG AT START ---
    factory_type_start = type(getattr(bot, 'service_factory', None)).__name__
    logger.info(f"[DIAGNOSTIC setup_hooks.register_core_services] START: bot.service_factory type is {factory_type_start}")
    # --- END DIAGNOSTIC LOG ---

    if not bot.service_factory:
        logger.error("Service Factory is None or not available at start of register_core_services. Cannot register.")
        return

    logger.info("Registering core services with Service Factory...")
    try:
        # 1. Register ComponentRegistry
        if bot.component_registry:
            if hasattr(bot.service_factory, 'register_service'):
                bot.service_factory.register_service(
                    'component_registry',
                    bot.component_registry,
                    overwrite=True
                )
                logger.info("Registered service: component_registry")
            else:
                logger.error("bot.service_factory is missing register_service method (ComponentRegistry).")
        else:
            logger.error("bot.component_registry not found. Cannot register.")

        # 2. Instantiate and Register DashboardDataService
        logger.debug("Instantiating DashboardDataService...")
        dashboard_data_service_instance = DashboardDataService(bot)
        if hasattr(bot.service_factory, 'register_service'):
            bot.service_factory.register_service(
                'dashboard_data_service',
                dashboard_data_service_instance,
                overwrite=True
            )
            logger.info("Registered service: dashboard_data_service")
        else:
            logger.error("bot.service_factory is missing register_service method (DashboardDataService).")

        # 3. Instantiate and Register ComponentLoaderService
        logger.debug("Instantiating ComponentLoaderService...")
        component_loader_instance = ComponentLoaderService(bot)
        if hasattr(bot.service_factory, 'register_service') and hasattr(bot.service_factory, 'has_service'):
            if not bot.service_factory.has_service('component_loader'):
                bot.service_factory.register_service(
                    'component_loader',
                    component_loader_instance,
                    overwrite=True
                )
                logger.info("Registered service: component_loader")
            else:
                logger.info("ComponentLoaderService already registered.")
        else:
            logger.error("Service Factory instance is missing expected registration methods.")

    except Exception as e:
        logger.error(f"Error registering core services in ServiceFactory: {e}", exc_info=True)

    # --- ADD DIAGNOSTIC LOG AT END ---
    factory_type_end = type(getattr(bot, 'service_factory', None)).__name__
    logger.info(f"[DIAGNOSTIC setup_hooks.register_core_services] END: bot.service_factory type is {factory_type_end}")
    # --- END DIAGNOSTIC LOG ---
