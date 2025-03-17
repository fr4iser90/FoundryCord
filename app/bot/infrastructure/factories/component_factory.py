import logging
from typing import Dict, Any, Optional, List

import discord

from app.bot.infrastructure.factories.component_registry import ComponentRegistry
from app.bot.interfaces.dashboards.components.common.base_component import BaseComponent

logger = logging.getLogger("homelab.components")

class ComponentFactory:
    """Factory for creating dashboard UI components"""
    
    def __init__(self, component_registry: ComponentRegistry):
        self.registry = component_registry
        logger.info("Component factory initialized with registry")
    
    async def create(self, component_type: str, **kwargs):
        """
        Create a component or controller based on type
        This is a facade method to direct to the appropriate creator
        """
        if component_type == 'dashboard':
            return await self.create_dashboard_controller(**kwargs)
        else:
            # For regular UI components, use the component creation method
            component_id = kwargs.get('component_id', f"{component_type}_{id(kwargs)}")
            config = kwargs.get('config', {})
            return await self.create_component(component_type, component_id, config)
    
    async def create_dashboard_controller(self, dashboard_id: str, dashboard_type: str, 
                                         channel_id: int, **kwargs):
        """Create a dashboard controller"""
        try:
            # Import here to avoid circular imports
            from app.bot.interfaces.dashboards.controller.base_dashboard import BaseDashboardController
            from app.bot.interfaces.dashboards.controller.system_dashboard import SystemDashboardController
            
            # Map dashboard types to their controller classes
            controller_map = {
                'system': SystemDashboardController,
                'server': SystemDashboardController,  # Reuse system for server for now
                'project': BaseDashboardController,   # Use base for project for now
                'welcome': BaseDashboardController,   # Use base for welcome for now
                'default': BaseDashboardController
            }
            
            # Get the appropriate controller class or fall back to base
            controller_class = controller_map.get(dashboard_type, controller_map['default'])
            
            # Log the dashboard type being created
            logger.info(f"Creating {dashboard_type} dashboard controller for dashboard {dashboard_id}")
            
            # Create and return the controller
            controller = controller_class(
                dashboard_id=dashboard_id,
                channel_id=channel_id,
                **kwargs
            )
            logger.info(f"Created {dashboard_type} dashboard controller for dashboard {dashboard_id}")
            return controller
            
        except Exception as e:
            logger.error(f"Error creating dashboard controller: {str(e)}")
            return None
    
    async def create_component(self, 
                              component_type: str, 
                              component_id: str, 
                              config: Dict[str, Any]) -> Optional[BaseComponent]:
        """Create a component instance from type and configuration"""
        component_def = self.registry.get_component_definition(component_type)
        
        if not component_def:
            logger.error(f"Cannot create component - type '{component_type}' not registered")
            return None
        
        try:
            # Merge default config with provided config
            merged_config = {**component_def.default_config, **config}
            
            # Create component instance
            component = component_def.component_class(
                component_id=component_id,
                config=merged_config
            )
            logger.debug(f"Created component '{component_id}' of type '{component_type}'")
            return component
            
        except Exception as e:
            logger.error(f"Error creating component '{component_id}' of type '{component_type}': {str(e)}")
            return None
    
    async def create_components_from_definitions(self, 
                                               components_data: List[Dict[str, Any]]) -> Dict[str, BaseComponent]:
        """Create multiple components from their definitions"""
        created_components = {}
        
        for comp_data in components_data:
            component_id = comp_data.get('id')
            component_type = comp_data.get('type')
            component_config = comp_data.get('config', {})
            
            if not component_id or not component_type:
                logger.warning(f"Invalid component data - missing id or type: {comp_data}")
                continue
                
            component = await self.create_component(
                component_type=component_type,
                component_id=component_id,
                config=component_config
            )
            
            if component:
                created_components[component_id] = component
        
        return created_components 