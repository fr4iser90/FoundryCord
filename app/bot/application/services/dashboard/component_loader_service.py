from typing import Dict, Any, List, Optional
from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

class ComponentLoaderService:
    """Service for loading dashboard components from database"""
    
    def __init__(self, bot):
        self.bot = bot
        
    async def load_components_for_dashboard(self, dashboard_id: str) -> Dict[str, Any]:
        """Load all components for a specific dashboard"""
        try:
            dashboard_repo = self.bot.service_factory.get_service('dashboard_repository')
            if not dashboard_repo:
                logger.error("Dashboard repository service not available")
                return {}
                
            components = await dashboard_repo.get_components_for_dashboard(dashboard_id)
            return {comp.component_id: comp for comp in components}
            
        except Exception as e:
            logger.error(f"Error loading components for dashboard {dashboard_id}: {e}")
            return {}
            
    async def load_component_by_type(self, dashboard_id: str, component_type: str) -> List[Any]:
        """Load components of a specific type for a dashboard"""
        try:
            dashboard_repo = self.bot.service_factory.get_service('dashboard_repository')
            if not dashboard_repo:
                logger.error("Dashboard repository service not available")
                return []
                
            components = await dashboard_repo.get_components_by_type(
                dashboard_id=dashboard_id,
                component_type=component_type
            )
            return components
            
        except Exception as e:
            logger.error(f"Error loading {component_type} components for dashboard {dashboard_id}: {e}")
            return []
