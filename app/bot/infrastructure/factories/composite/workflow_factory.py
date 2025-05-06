"""Workflow factory for creating and configuring bot workflows."""
from typing import Dict, Any, Optional
import asyncio
from app.shared.interfaces.logging.api import get_bot_logger
logger = get_bot_logger()

# Interface Imports
from app.bot.application.interfaces.bot import Bot as BotInterface
# from app.bot.application.interfaces.service_factory import ServiceFactory as ServiceFactoryInterface # Not directly typed here
from app.bot.application.interfaces.component_registry import ComponentRegistry as ComponentRegistryInterface

# Import domain models
from app.shared.infrastructure.models.dashboards.dashboard_entity import DashboardEntity
from app.shared.domain.repositories import ActiveDashboardRepository

# Import debug components
from app.bot import debug_component_registry, debug_component_factory

# Import application services
from app.bot.application.services.config import BotConfigService
from app.shared.domain.auth.services import AuthenticationService
from app.bot.application.services.project_management import ProjectManagementService
# from app.bot.infrastructure.config.registries.component_registry import ComponentRegistry # Removed concrete import
from app.bot.interfaces.api.internal.websocket_manager import WebsocketManager

class WorkflowFactory:
    """Factory for creating bot workflows."""
    
    def __init__(self, bot):
        """Initialize the factory with a bot instance."""
        self.bot = bot
        
    async def create_channel_workflow(self):
        """Create a channel workflow."""
        logger.info("Creating channel workflow")
        
        # Simple stub implementation - replace with actual workflow
        class ChannelWorkflow:
            def __init__(self, bot):
                self.bot = bot
                
            async def initialize(self):
                logger.info("Initializing channel workflow")
                return True
                
            async def cleanup(self):
                logger.info("Cleaning up channel workflow")
                return True
                
        workflow = ChannelWorkflow(self.bot)
        await workflow.initialize()
        return workflow
        
    async def create_dashboard_workflow(self):
        """Create a dashboard workflow using domain models."""
        logger.info("Creating dashboard workflow with domain model integration")
        
        # Implementing DDD-based dashboard workflow
        class DashboardWorkflow:
            def __init__(self, bot):
                self.bot = bot
                self.repository = None
                self.dashboard_controllers = {}
                
                # Ensure component factory and registry are accessed via self.bot, assuming they are pre-initialized
                if not hasattr(self.bot, 'component_registry'):
                    # This indicates a setup issue if bot is not fully prepped.
                    # Forcing instantiation here is not ideal for this factory's role.
                    logger.error("CRITICAL: bot.component_registry not found during DashboardWorkflow init in WorkflowFactory. Bot should be pre-configured.")
                    # Fallback or raise error, rather than local import/creation.
                    # For now, this will likely fail if not present.
                    
                if not hasattr(self.bot, 'component_factory'):
                    logger.error("CRITICAL: bot.component_factory not found during DashboardWorkflow init in WorkflowFactory. Bot should be pre-configured.")
                    # Fallback or raise error.
                    
            async def initialize(self):
                logger.info("Initializing dashboard workflow with domain model")
                
                # Initialize domain repositories
                self.repository = DashboardRepository()
                
                # Load dashboard configurations from database
                await self.load_dashboards()
                
                return True
                
            async def load_dashboards(self):
                """Load dashboard configurations from database"""
                try:
                    # Get all dashboard configurations from repository
                    dashboards = await self.repository.get_all_dashboards()
                    
                    logger.info(f"Loaded {len(dashboards)} dashboards from repository")
                    
                    # Create controllers for each dashboard
                    for dashboard in dashboards:
                        await self.create_dashboard_controller(dashboard)
                        
                except Exception as e:
                    logger.error(f"Error loading dashboards: {e}")
                    
            async def create_dashboard_controller(self, dashboard: DashboardEntity):
                """Create a controller for a dashboard model"""
                try:
                    # Debug logging
                    logger.info(f"Creating dashboard controller for dashboard: {dashboard.id}, type: {dashboard.dashboard_type}")
                    
                    # Make sure dashboard has all required attributes
                    if not hasattr(dashboard, 'dashboard_type') or not dashboard.dashboard_type:
                        logger.warning(f"Dashboard {dashboard.id} missing type, setting default")
                        dashboard.dashboard_type = "default"
                        
                    # Use component factory to create dashboard controller
                    if not hasattr(self.bot, 'component_factory'):
                        logger.warning("Bot missing component factory during create_dashboard_controller, using debug instance")
                        # This debug fallback is also questionable in a production factory.
                        self.bot.component_factory = debug_component_factory
                        # self.bot.component_registry = debug_component_registry # This line was problematic, registry should be on bot
                    
                    # Access component_factory from bot, assuming it holds an instance that uses ComponentRegistryInterface
                    controller = await self.bot.component_factory.create(
                        'dashboard', 
                        dashboard_id=dashboard.id,
                        dashboard_type=dashboard.dashboard_type,
                        channel_id=dashboard.channel_id
                    )
                    
                    if controller:
                        self.dashboard_controllers[dashboard.id] = controller
                        logger.info(f"Created controller for dashboard {dashboard.id}")
                    
                except Exception as e:
                    logger.error(f"Error creating dashboard controller: {str(e)}")
                    import traceback
                    logger.error(traceback.format_exc())
                
            async def cleanup(self):
                logger.info("Cleaning up dashboard workflow")
                return True
                
            async def start_background_tasks(self):
                logger.info("Starting dashboard background tasks")
                return True
                
        workflow = DashboardWorkflow(self.bot)
        await workflow.initialize()
        return workflow
        
    async def create_command_workflow(self):
        """Create a command workflow."""
        logger.info("Creating command workflow")
        
        # Simple stub implementation - replace with actual workflow
        class CommandWorkflow:
            def __init__(self, bot):
                self.bot = bot
                
            async def initialize(self):
                logger.info("Initializing command workflow")
                return True
                
            async def cleanup(self):
                logger.info("Cleaning up command workflow")
                return True
                
        workflow = CommandWorkflow(self.bot)
        await workflow.initialize()
        return workflow
        
    async def create_task_workflow(self):
        """Create a task workflow."""
        logger.info("Creating task workflow")
        
        # Simple stub implementation - replace with actual workflow
        class TaskWorkflow:
            def __init__(self, bot):
                self.bot = bot
                
            async def initialize(self):
                logger.info("Initializing task workflow")
                return True
                
            async def cleanup(self):
                logger.info("Cleaning up task workflow")
                return True
                
            async def start_background_tasks(self):
                logger.info("Starting task background tasks")
                return True
                
        workflow = TaskWorkflow(self.bot)
        await workflow.initialize()
        return workflow 