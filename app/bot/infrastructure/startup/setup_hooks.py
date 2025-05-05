from app.shared.interface.logging.api import get_bot_logger
import nextcord
from typing import TYPE_CHECKING, Optional
import functools # Added for partial

# Updated import paths
from app.bot.infrastructure.startup.lifecycle_manager import BotLifecycleManager
from app.bot.infrastructure.startup.shutdown_handler import ShutdownHandler
from app.bot.application.workflows.database_workflow import DatabaseWorkflow
from app.bot.application.workflows.guild import GuildWorkflow
from app.bot.application.workflows.category_workflow import CategoryWorkflow
from app.bot.application.workflows.channel_workflow import ChannelWorkflow
from app.bot.application.workflows.dashboard_workflow import DashboardWorkflow
from app.bot.application.workflows.task_workflow import TaskWorkflow
from app.bot.application.workflows.user_workflow import UserWorkflow
from app.bot.application.workflows.guild_template_workflow import GuildTemplateWorkflow
from app.bot.application.services.bot_control_service import BotControlService
from app.bot.application.services.dashboard.component_loader_service import ComponentLoaderService
from app.bot.application.services.dashboard.dashboard_data_service import DashboardDataService
from app.bot.infrastructure.factories.service_factory import ServiceFactory
from app.bot.infrastructure.factories.task_factory import TaskFactory
from app.bot.interfaces.api.internal.routes import setup_internal_routes
from app.bot.infrastructure.config.registries.component_registry import ComponentRegistry
from app.bot.infrastructure.factories.component_factory import ComponentFactory
from app.bot.interfaces.api.internal.server import InternalAPIServer
from app.bot.interfaces.dashboards.components.common.embeds.dashboard_embed import DashboardEmbed
from app.bot.interfaces.dashboards.components.common.embeds.error_embed import ErrorEmbed
from app.bot.interfaces.dashboards.components.common.buttons.generic_button import GenericButtonComponent
from app.bot.interfaces.dashboards.components.common.selectors.generic_selector import GenericSelectorComponent
from app.bot.infrastructure.monitoring.collectors.system.impl import SystemCollector
from app.bot.infrastructure.monitoring.collectors.service.impl import ServiceCollector

# Imports for State Collector Registration
from app.shared.infrastructure.state.secure_state_snapshot import get_state_snapshot_service
from app.bot.infrastructure.state.collectors.basic_info import collect_basic_info_func
from app.shared.infrastructure.state.collectors.system_info import get_system_info as collect_system_info_func
from app.bot.infrastructure.state.collectors.performance import collect_performance_metrics_func
from app.bot.infrastructure.state.collectors.discord_api import (
    collect_discord_connection_info_func,
    collect_guilds_summary_func,
    collect_commands_info_func
)
from app.bot.infrastructure.state.collectors.database_status import collect_database_connection_info_func
from app.bot.infrastructure.state.collectors.listeners import collect_active_listeners_func
from app.bot.infrastructure.state.collectors.cog_status import collect_cog_status_func

# Import BotWorkflowManager
from app.bot.application.workflow_manager import BotWorkflowManager

logger = get_bot_logger()

def register_state_collectors(bot):
    """Registers bot state collectors directly with the snapshot service."""
    if getattr(bot, '_state_collectors_registered', False):
        logger.debug("Bot state collectors already registered.")
        return True # Indicate already done

    logger.debug("Registering bot state collectors...")
    snapshot_service = get_state_snapshot_service()
    
    # Helper to create partial functions for collectors needing the bot instance
    def partial_collector(func, bot_instance):
        # The snapshot service passes context, but our func might not use it
        # We create a lambda that accepts context but calls the original func with bot
        return functools.partial(func, bot_instance)
        # Alternate lambda approach if partial causes issues:
        # return lambda context=None: func(bot_instance)

    try:
        # Basic bot state collectors (require no special permissions)
        snapshot_service.register_collector(
            name="bot_basic_info",
            collector_fn=partial_collector(collect_basic_info_func, bot),
            requires_approval=False,
            scope="bot",
            description="Basic bot status and version information"
        )

        # System info uses shared collector (doesn't need bot instance)
        snapshot_service.register_collector(
            name="bot_system_info",
            collector_fn=collect_system_info_func,
            requires_approval=False,
            scope="bot",
            description="Bot host system information (uses shared collector logic)"
        )

        # Performance metrics (doesn't need bot instance)
        snapshot_service.register_collector(
            name="bot_performance",
            collector_fn=collect_performance_metrics_func,
            requires_approval=False,
            scope="bot",
            description="Bot performance metrics"
        )

        # Discord-specific state collectors (require approval)
        snapshot_service.register_collector(
            name="discord_connection",
            collector_fn=partial_collector(collect_discord_connection_info_func, bot),
            requires_approval=True,
            scope="bot",
            description="Discord connection and gateway information"
        )

        snapshot_service.register_collector(
            name="discord_guilds_summary",
            collector_fn=partial_collector(collect_guilds_summary_func, bot),
            requires_approval=True,
            scope="bot",
            description="Summary of connected Discord servers/guilds"
        )

        snapshot_service.register_collector(
            name="discord_commands",
            collector_fn=partial_collector(collect_commands_info_func, bot),
            requires_approval=True,
            scope="bot",
            description="Registered Discord commands information"
        )

        # Advanced state collectors (always require approval)
        snapshot_service.register_collector(
            name="database_connection",
            collector_fn=partial_collector(collect_database_connection_info_func, bot),
            requires_approval=True,
            scope="bot",
            description="Database connection status (from bot's perspective)"
        )

        snapshot_service.register_collector(
            name="active_listeners",
            collector_fn=partial_collector(collect_active_listeners_func, bot),
            requires_approval=True,
            scope="bot",
            description="Currently active event listeners"
        )

        snapshot_service.register_collector(
            name="cog_status",
            collector_fn=partial_collector(collect_cog_status_func, bot),
            requires_approval=True,
            scope="bot",
            description="Status of loaded cogs/extensions"
        )
        logger.debug("Bot state collectors registered successfully.")
        # --- Set Flag ---
        bot._state_collectors_registered = True 
        return True
    except Exception as e:
        logger.error(f"Failed to register bot state collectors: {e}", exc_info=True)
        return False

def setup_core_components(bot):
    """Initializes core managers, registries, factories, and other essential components."""
    logger.debug("Setting up core components...")
    try:
        bot.lifecycle = BotLifecycleManager()
        bot.workflow_manager = BotWorkflowManager()
        bot.component_registry = ComponentRegistry()
        bot.component_factory = ComponentFactory(bot.component_registry)
        bot.shutdown_handler = ShutdownHandler(bot)
        bot.control_service = BotControlService(bot)
        bot.internal_api_server = InternalAPIServer(bot)
        bot._default_components_registered = False
        # --- Add Flag Initialization ---
        bot._state_collectors_registered = False
        logger.debug("Core components setup complete (incl. DataSourceRegistry).")
    except Exception as e:
        logger.critical(f"Failed to setup core components: {e}", exc_info=True)
        raise

def register_workflows(bot):
    """Instantiates and registers all workflows with the WorkflowManager."""
    if not bot.workflow_manager:
        logger.critical("WorkflowManager not initialized before register_workflows call.")
        return

    logger.debug("Setting up and registering workflows...")
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
        logger.debug("Workflows registered and order set.")
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

    logger.debug("Registering default and generic components...")
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
        logger.debug("Registering implementation classes for generic database component types...")

        # Register 'embed' type -> Use the existing DashboardEmbed class
        bot.component_registry.register_component(
            component_type="embed",
            component_class=DashboardEmbed,
            description="Generic embed component implementation (uses DashboardEmbed)"
        )
        logger.debug("Registered 'embed' type to use DashboardEmbed class.")

        # Register 'button' type -> Use the new GenericButtonComponent class
        bot.component_registry.register_component(
            component_type="button",
            component_class=GenericButtonComponent,
            description="Generic button component implementation"
        )
        logger.debug("Registered 'button' type to use GenericButtonComponent class.")

        # Register 'selector' type -> Use the new GenericSelectorComponent class
        bot.component_registry.register_component(
            component_type="selector",
            component_class=GenericSelectorComponent,
            description="Generic selector component implementation"
        )
        logger.debug("Registered 'selector' type to use GenericSelectorComponent class.")

        bot._default_components_registered = True
        logger.debug(f"Finished registering default/generic components. Total implementation types registered: {len(bot.component_registry.get_all_component_types())}")
    except NameError as ne:
        logger.error(f"Failed to register a component - Class not found (NameError): {ne}. Ensure component classes are imported.", exc_info=True)
    except Exception as e:
        logger.error(f"Error registering default/generic components: {e}", exc_info=True)

def register_core_services(service_factory: ServiceFactory, bot):
    """Synchronously register essential core services needed early.

    Args:
        service_factory (ServiceFactory): The factory instance.
        bot: The bot instance.
    """
    logger.debug("Registering core services with Service Factory (synchronous)...")
    try:
        # Register Component Registry instance (already created)
        if hasattr(bot, 'component_registry') and bot.component_registry:
            if hasattr(service_factory, 'register_service'):
                service_factory.register_service(
                    'component_registry',
                    bot.component_registry,
                    overwrite=True
                )
                logger.debug("Registered service: component_registry")
            else:
                logger.error("service_factory is missing register_service method (ComponentRegistry).")
        else:
            logger.error("bot.component_registry not found. Cannot register.")

        # 2. Instantiate and Register SystemCollector (Moved Up)
        logger.debug("Instantiating SystemCollector...")
        system_collector_instance = SystemCollector()
        if hasattr(service_factory, 'register_service') and hasattr(service_factory, 'has_service'):
            if not service_factory.has_service('system_collector'):
                service_factory.register_service(
                    'system_collector',
                    system_collector_instance,
                    overwrite=True # Allow overwrite if somehow registered elsewhere
                )
                logger.debug("Registered service: system_collector")
            else:
                logger.info("SystemCollector already registered.")
        else:
            logger.error("service_factory is missing register_service/has_service method (SystemCollector).")

        # 3. Instantiate and Register ServiceCollector
        logger.debug("Instantiating ServiceCollector...")
        service_collector_instance = ServiceCollector()
        if hasattr(service_factory, 'register_service') and hasattr(service_factory, 'has_service'):
            if not service_factory.has_service('service_collector'):
                service_factory.register_service(
                    'service_collector',
                    service_collector_instance,
                    overwrite=True
                )
                logger.debug("Registered service: service_collector")
            else:
                logger.info("ServiceCollector already registered.")
        else:
            logger.error("service_factory is missing register_service/has_service method (ServiceCollector).")

        # 4. Instantiate and Register DashboardDataService (Now depends on SystemCollector being registered)
        logger.debug("Instantiating DashboardDataService...")
        dashboard_data_service_instance = DashboardDataService(bot, service_factory)
        if hasattr(service_factory, 'register_service'):
            service_factory.register_service(
                'dashboard_data_service',
                dashboard_data_service_instance,
                overwrite=True
            )
            logger.debug("Registered service: dashboard_data_service")
        else:
            logger.error("service_factory is missing register_service method (DashboardDataService).")

        # 5. Instantiate and Register ComponentLoaderService
        logger.debug("Instantiating ComponentLoaderService...")
        component_loader_instance = ComponentLoaderService(bot)
        if hasattr(service_factory, 'register_service') and hasattr(service_factory, 'has_service'):
            if not service_factory.has_service('component_loader'):
                service_factory.register_service(
                    'component_loader',
                    component_loader_instance,
                    overwrite=True
                )
                logger.debug("Registered service: component_loader")
            else:
                logger.info("ComponentLoaderService already registered.")
        else:
            logger.error("service_factory is missing register_service method (ComponentLoaderService).")

        # 6. Register State Collectors (New)
        register_state_collectors(bot) # Call the new registration function

    except Exception as e:
        logger.critical(f"CRITICAL ERROR DURING CORE SERVICE REGISTRATION: {e}", exc_info=True)
        # Potentially re-raise or handle appropriately

def setup_service_factory_and_register_core_services(bot):
    """Sets up the Service Factory and registers core services."""
    logger.debug("Setting up Service Factory and registering core services in __init__...")
    try:
        if not bot.service_factory:
            # Pass bot instance to the factory constructor
            bot.service_factory = ServiceFactory(bot)
            logger.debug(f"ServiceFactory instantiated in __init__: {bot.service_factory}")
            # Register core services immediately after factory creation
            register_core_services(bot.service_factory, bot)
            # Register state collectors AFTER factory is created but before full init
            register_state_collectors(bot) # Assuming bot instance is needed
        else:
            logger.warning("ServiceFactory already exists.")

        logger.debug("Service Factory setup and core service registration complete.")
    except Exception as e:
        logger.critical(f"Failed to setup Service Factory or register core services: {e}", exc_info=True)
        bot.service_factory = None # Ensure it's None if setup fails
        # Re-raise or handle as appropriate for critical setup failure
        raise

async def setup_hook(bot):
    """
    Asynchronous setup hook called by nextcord after __init__ but before on_ready.
    KEEP THIS EMPTY regarding ServiceFactory.
    Use this for other async setup tasks if needed later (like loading cogs/extensions).
    """
    logger.info("Executing setup_hook (ServiceFactory initialization moved to __init__)...")
    pass

# Define setup_bot_services, setup_bot_workflows, etc., if they are distinct steps
# For now, assume register_core_services covers the main service setup.
async def setup_bot_services(bot):
    logger.info("Running setup_bot_services (currently handled by register_core_services)...")
    # Add any specific async service setup here if needed later
    pass

async def setup_bot_workflows(bot):
    logger.info("Running setup_bot_workflows (currently handled by register_workflows)...")
    # Add any specific async workflow setup here if needed later
    pass

async def setup_bot_tasks(bot):
    logger.info("Running setup_bot_tasks...")
    # Example: Initialize TaskWorkflow if it exists
    if hasattr(bot, 'task_workflow') and bot.task_workflow:
        await bot.task_workflow.initialize() # Assuming TaskWorkflow has an async initialize
    pass

async def setup_factories_and_registries(bot):
    logger.info("Running setup_factories_and_registries (handled in __init__ / register_core_services)...")
    # ComponentRegistry, DataSourceRegistry, ServiceFactory are handled synchronously
    # Initialize ComponentRegistry definitions from DB (async)
    if bot.component_registry:
        await bot.component_registry.initialize(bot)
    pass

async def setup_event_listeners(bot):
    logger.info("Setting up event listeners...")
    # Example: bot.add_listener(some_listener_func, 'on_message')
    pass

async def setup_bot_components(bot):
    logger.info("Running setup_bot_components...")
    # Add any specific bot component setup here if needed later
    pass
