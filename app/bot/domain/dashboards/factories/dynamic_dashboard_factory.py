"""
Factory for creating dashboard instances from database configurations.
"""
from typing import Dict, Any, Optional, Type, List
import importlib
import inspect
import nextcord

from app.shared.interface.logging.api import get_bot_logger
from app.bot.interfaces.dashboards.controller.base_dashboard import BaseDashboardController
from app.bot.interfaces.dashboards.controller.dynamic_dashboard import DynamicDashboard
from app.bot.domain.dashboards.models.dashboard_model import DashboardModel
from app.bot.domain.dashboards.repositories.dashboard_repository import DashboardRepository
from app.shared.infrastructure.database.session import get_session

logger = get_bot_logger()

class DynamicDashboardFactory:
    """Factory for creating dashboard instances from database configurations."""
    
    def __init__(self, bot, component_registry=None, data_source_registry=None):
        """Initialize the dashboard factory."""
        self.bot = bot
        self.component_registry = component_registry
        self.data_source_registry = data_source_registry
        # Pass session_factory to repository
        self.dashboard_repository = DashboardRepository(session_factory=get_session)
        
        # Register default dashboard controllers
        self.dashboard_controllers = {}
        self._register_default_controllers()
    
    def _register_default_controllers(self):
        """Register default dashboard controller types."""
        # Import standard dashboard controllers
        from app.bot.interfaces.dashboards.controller.welcome_dashboard import WelcomeDashboard
        from app.bot.interfaces.dashboards.controller.monitoring_dashboard import MonitoringDashboard
        from app.bot.interfaces.dashboards.controller.project_dashboard import ProjectDashboard
        from app.bot.interfaces.dashboards.controller.gamehub_dashboard import GamehubDashboard
        
        # Register them with their type names
        self.register_dashboard_controller("welcome", WelcomeDashboard)
        self.register_dashboard_controller("monitoring", MonitoringDashboard)
        self.register_dashboard_controller("project", ProjectDashboard)
        self.register_dashboard_controller("gamehub", GamehubDashboard)
        # You can register more dashboard types here

    def register_dashboard_controller(self, dashboard_type: str, controller_class: Type[BaseDashboardController]):
        """Register a dashboard controller class for a specific dashboard type."""
        self.dashboard_controllers[dashboard_type] = controller_class
        logger.info(f"Registered dashboard controller for type: {dashboard_type}")
    
    async def create_from_config(self, config_id: str) -> Optional[BaseDashboardController]:
        """Create a dashboard instance from a configuration ID."""
        # Fetch dashboard configuration from repository
        dashboard_config = await self.dashboard_repository.get_dashboard_config(config_id)
        if not dashboard_config:
            logger.error(f"Dashboard configuration not found: {config_id}")
            return None
        
        return await self.create_from_model(dashboard_config)
    
    async def create_from_model(self, dashboard_model: DashboardModel) -> Optional[BaseDashboardController]:
        """Create a dashboard instance from a dashboard model."""
        try:
            # Get dashboard type
            dashboard_type = dashboard_model.dashboard_type
            
            # If we have a specific controller for this type, use it
            if dashboard_type in self.dashboard_controllers:
                controller_class = self.dashboard_controllers[dashboard_type]
                logger.info(f"Creating {dashboard_type} dashboard using registered controller")
                dashboard = controller_class(
                    self.bot,
                    dashboard_model.dashboard_id,
                    dashboard_model.title,
                    dashboard_model.channel_id,
                    dashboard_model.config
                )
            else:
                # Use the dynamic dashboard controller as fallback
                logger.info(f"Creating dynamic dashboard for type: {dashboard_type}")
                dashboard = DynamicDashboard(
                    self.bot,
                    dashboard_model.dashboard_id,
                    dashboard_model.title, 
                    dashboard_model.channel_id,
                    dashboard_model.config
                )
            
            # Attach components based on configuration
            if self.component_registry:
                await self._attach_components(dashboard, dashboard_model.components)
            
            # Attach data sources based on configuration
            if self.data_source_registry:
                await self._attach_data_sources(dashboard, dashboard_model.data_sources)
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error creating dashboard from model: {e}")
            return None
    
    async def _attach_components(self, dashboard, component_configs: List[Dict[str, Any]]):
        """Attach UI components to the dashboard based on configuration."""
        for component_config in component_configs:
            component_type = component_config.get("type")
            if not component_type:
                continue
                
            try:
                # Create component from registry
                component = self.component_registry.create(
                    component_type, 
                    **component_config.get("config", {})
                )
                
                if component:
                    dashboard.add_component(component, component_config.get("position", {}))
            except Exception as e:
                logger.error(f"Error creating component {component_type}: {e}")
    
    async def _attach_data_sources(self, dashboard, data_source_configs: List[Dict[str, Any]]):
        """Attach data sources to the dashboard based on configuration."""
        for source_config in data_source_configs:
            source_id = source_config.get("id")
            source_type = source_config.get("type")
            
            if not source_id or not source_type:
                continue
                
            try:
                # Create data source from registry
                data_source = self.data_source_registry.create(
                    source_type,
                    **source_config.get("config", {})
                )
                
                if data_source:
                    dashboard.add_data_source(source_id, data_source)
            except Exception as e:
                logger.error(f"Error creating data source {source_type}: {e}") 