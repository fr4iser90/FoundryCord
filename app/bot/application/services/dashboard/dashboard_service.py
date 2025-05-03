"""Dashboard service for coordinating dashboard operations.

TODO: [REFACTORING] This entire service needs significant rework or removal.
It currently relies on deleted models (DashboardEntity, etc.) and the old repository structure.
Its functionality overlaps heavily with DashboardLifecycleService and DashboardRegistry.
"""
from typing import Dict, Any, List, Optional
import nextcord
from datetime import datetime
import asyncio

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

from app.shared.domain.repositories import ActiveDashboardRepository
from app.bot.infrastructure.factories.component_registry import ComponentRegistry
from app.bot.infrastructure.factories.data_source_registry import DataSourceRegistry
# from app.shared.infrastructure.database.core.connection import get_session

class DashboardService:
    """Core service for dashboard operations. (CURRENTLY DISABLED - NEEDS REFACTORING)"""
    
    # def __init__(self, 
    #              bot,
    #              repository: DashboardRepository, # Old interface
    #              component_registry: ComponentRegistry,
    #              data_source_registry: DataSourceRegistry):
    #     self.bot = bot
    #     self.repository = repository
    #     self.component_registry = component_registry
    #     self.data_source_registry = data_source_registry
    
    # async def get_dashboard(self, dashboard_id: str) -> Optional[Any]: # Return Any temporarily
    #     """Get a dashboard by ID."""
    #     logger.warning("DashboardService.get_dashboard needs refactoring.")
    #     return None # await self.repository.get_by_id(dashboard_id)
    
    # async def get_dashboard_by_channel(self, channel_id: int) -> Optional[Any]:
    #     """Get a dashboard for a channel."""
    #     logger.warning("DashboardService.get_dashboard_by_channel needs refactoring.")
    #     return None # await self.repository.get_by_channel_id(channel_id)
    
    # async def create_dashboard(self, dashboard_data: Dict[str, Any]) -> Any:
    #     """Create a new dashboard from configuration."""
    #     logger.warning("DashboardService.create_dashboard needs refactoring.")
    #     # dashboard = self._create_dashboard_entity(dashboard_data)
    #     # saved_dashboard = await self.repository.save(dashboard)
    #     # logger.info(f"Created new dashboard: {saved_dashboard.id} ({saved_dashboard.name})")
    #     # return saved_dashboard
    #     return None
    
    # async def update_dashboard(self, dashboard_id: str, dashboard_data: Dict[str, Any]) -> Optional[Any]:
    #     """Update an existing dashboard."""
    #     logger.warning("DashboardService.update_dashboard needs refactoring.")
    #     # dashboard = await self.repository.get_by_id(dashboard_id)
    #     # if not dashboard:
    #     #     logger.warning(f"Attempted to update non-existent dashboard: {dashboard_id}")
    #     #     return None
    #     # for key, value in dashboard_data.items():
    #     #     if hasattr(dashboard, key):
    #     #         setattr(dashboard, key, value)
    #     # dashboard.updated_at = datetime.now()
    #     # updated_dashboard = await self.repository.save(dashboard)
    #     # logger.info(f"Updated dashboard: {updated_dashboard.id}")
    #     # return updated_dashboard
    #     return None
    
    # async def delete_dashboard(self, dashboard_id: str) -> bool:
    #     """Delete a dashboard."""
    #     logger.warning("DashboardService.delete_dashboard needs refactoring.")
    #     # result = await self.repository.delete(dashboard_id)
    #     # if result:
    #     #     logger.info(f"Deleted dashboard: {dashboard_id}")
    #     # return result
    #     return False
    
    # async def get_all_dashboards(self) -> List[Any]:
    #     """Get all dashboards."""
    #     logger.warning("DashboardService.get_all_dashboards needs refactoring.")
    #     # try:
    #     #     return await self.repository.get_all_dashboards()
    #     # except Exception as e:
    #     #     logger.error(f"Error getting all dashboards: {e}")
    #     #     return []
    #     return []
    
    # async def sync_dashboard_from_snapshot(self, channel: nextcord.TextChannel, config_json: Dict[str, Any]) -> bool:
    #     """Creates or updates a dashboard entity and its config from a snapshot, then activates/updates the controller."""
    #     logger.warning("DashboardService.sync_dashboard_from_snapshot needs refactoring / moved to LifecycleService.")
    #     return False # Placeholder

    # def _create_dashboard_entity(self, data: Dict[str, Any]) -> Any:
    #     """Convert dictionary data to a DashboardEntity. (DISABLED)"""
    #     logger.error("_create_dashboard_entity relies on deleted models and cannot be used.")
    #     return None
        # from app.shared.infrastructure.models.dashboards.dashboard_entity import DashboardEntity
        # from app.shared.infrastructure.models.dashboards.dashboard_component_entity import DashboardComponentEntity
        # from app.shared.infrastructure.models.dashboards.component_layout_entity import ComponentLayoutEntity
        # dashboard = DashboardEntity(...)
        # ... etc ...

    # async def ensure_dashboard_tables_exist(self):
    #     """Ensures necessary dashboard tables exist."""
    #     # This logic likely belongs elsewhere (e.g., migrations / startup checks)
    #     logger.warning("ensure_dashboard_tables_exist check might be obsolete or misplaced.")
    #     return

    # Example placeholder for a potential new method using new models
    # async def get_active_dashboard_info(self, channel_id: str) -> Optional[Dict]:
    #     """Example: Get info about an active dashboard using new repo."""
    #     # Requires injecting ActiveDashboardRepositoryImpl
    #     # active_repo = ActiveDashboardRepositoryImpl(await get_session()) # Example
    #     # active_dashboard = await active_repo.get_by_channel_id(channel_id)
    #     # if active_dashboard and active_dashboard.configuration:
    #     #     return { "config_name": active_dashboard.configuration.name, "message_id": active_dashboard.message_id }
    #     # return None
    #     pass 