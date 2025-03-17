"""Repository interface for dashboards."""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
import json

from app.bot.domain.dashboards.models.dashboard_model import DashboardModel
from app.bot.domain.dashboards.models.component_model import ComponentModel
from app.bot.domain.dashboards.models.data_source_model import DataSourceModel

from app.shared.infrastructure.database.management.connection import get_session
from app.shared.infrastructure.database.models import Dashboard as DashboardEntity
from app.shared.interface.logging.api import get_bot_logger

logger = get_bot_logger()

class DashboardRepository(ABC):
    """Repository interface for dashboard storage."""
    
    @abstractmethod
    async def get_by_id(self, dashboard_id: str) -> Optional[DashboardModel]:
        """Get a dashboard by ID."""
        pass
    
    @abstractmethod
    async def get_by_type(self, dashboard_type: str, guild_id: str) -> Optional[DashboardModel]:
        """Get a dashboard by type and guild ID."""
        pass
    
    @abstractmethod
    async def get_by_channel_id(self, channel_id: int) -> Optional[DashboardModel]:
        """Get a dashboard by channel ID."""
        pass
    
    @abstractmethod
    async def list_all(self, guild_id: Optional[str] = None) -> List[DashboardModel]:
        """List all dashboards, optionally filtered by guild ID."""
        pass
    
    @abstractmethod
    async def save(self, dashboard: DashboardModel) -> DashboardModel:
        """Save a dashboard."""
        pass
    
    @abstractmethod
    async def delete(self, dashboard_id: str) -> bool:
        """Delete a dashboard."""
        pass

class DashboardRepository:
    """Repository for storing and retrieving dashboard configurations."""
    
    async def get_all_dashboards(self) -> List[DashboardModel]:
        """Get all dashboard configurations."""
        try:
            session = get_session()
            dashboards = session.query(DashboardEntity).all()
            
            result = []
            for db_dashboard in dashboards:
                dashboard = self._convert_to_model(db_dashboard)
                if dashboard:
                    result.append(dashboard)
            
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving all dashboard configs: {e}")
            return []
    
    async def get_dashboard_config(self, config_id: str) -> Optional[DashboardModel]:
        """Get a dashboard configuration by ID."""
        try:
            session = get_session()
            db_dashboard = session.query(DashboardEntity).filter(
                DashboardEntity.dashboard_id == config_id
            ).first()
            
            if not db_dashboard:
                return None
                
            return self._convert_to_model(db_dashboard)
            
        except Exception as e:
            logger.error(f"Error retrieving dashboard config {config_id}: {e}")
            return None
    
    async def create_dashboard(self, 
                               title: str, 
                               dashboard_type: str,
                               channel_id: int,
                               config: Dict[str, Any] = None,
                               components: List[Dict[str, Any]] = None,
                               data_sources: List[Dict[str, Any]] = None) -> Optional[DashboardModel]:
        """Create a new dashboard configuration."""
        try:
            dashboard_id = str(uuid.uuid4())
            created_at = datetime.now()
            
            # Create the entity
            session = get_session()
            db_dashboard = DashboardEntity(
                dashboard_id=dashboard_id,
                title=title,
                dashboard_type=dashboard_type,
                channel_id=channel_id,
                config=json.dumps(config or {}),
                components=json.dumps(components or []),
                data_sources=json.dumps(data_sources or []),
                created_at=created_at,
                updated_at=created_at,
                active=True
            )
            
            session.add(db_dashboard)
            session.commit()
            
            # Create and return the model
            return self._convert_to_model(db_dashboard)
            
        except Exception as e:
            logger.error(f"Error creating dashboard config: {e}")
            return None
    
    async def update_dashboard(self, 
                              dashboard_model: DashboardModel) -> bool:
        """Update an existing dashboard configuration."""
        try:
            session = get_session()
            db_dashboard = session.query(DashboardEntity).filter(
                DashboardEntity.dashboard_id == dashboard_model.dashboard_id
            ).first()
            
            if not db_dashboard:
                logger.error(f"Dashboard not found for update: {dashboard_model.dashboard_id}")
                return False
            
            # Update fields
            db_dashboard.title = dashboard_model.title
            db_dashboard.dashboard_type = dashboard_model.dashboard_type
            db_dashboard.channel_id = dashboard_model.channel_id
            db_dashboard.config = json.dumps(dashboard_model.config or {})
            db_dashboard.components = json.dumps([c.to_dict() for c in dashboard_model.components])
            db_dashboard.data_sources = json.dumps([ds.to_dict() for ds in dashboard_model.data_sources])
            db_dashboard.updated_at = datetime.now()
            db_dashboard.active = dashboard_model.active
            
            session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error updating dashboard config {dashboard_model.dashboard_id}: {e}")
            return False
    
    async def delete_dashboard(self, config_id: str) -> bool:
        """Delete a dashboard configuration."""
        try:
            session = get_session()
            db_dashboard = session.query(DashboardEntity).filter(
                DashboardEntity.dashboard_id == config_id
            ).first()
            
            if not db_dashboard:
                logger.error(f"Dashboard not found for deletion: {config_id}")
                return False
            
            session.delete(db_dashboard)
            session.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error deleting dashboard config {config_id}: {e}")
            return False
    
    def _convert_to_model(self, db_dashboard: DashboardEntity) -> Optional[DashboardModel]:
        """Convert a database entity to a domain model."""
        try:
            # Parse JSON fields
            config = json.loads(db_dashboard.config) if db_dashboard.config else {}
            components_data = json.loads(db_dashboard.components) if db_dashboard.components else []
            data_sources_data = json.loads(db_dashboard.data_sources) if db_dashboard.data_sources else []
            
            # Create component models
            components = []
            for comp_data in components_data:
                component = ComponentModel(
                    component_id=comp_data.get("id", str(uuid.uuid4())),
                    component_type=comp_data.get("type", ""),
                    config=comp_data.get("config", {}),
                    position=comp_data.get("position", {})
                )
                components.append(component)
            
            # Create data source models
            data_sources = []
            for ds_data in data_sources_data:
                data_source = DataSourceModel(
                    source_id=ds_data.get("id", str(uuid.uuid4())),
                    source_type=ds_data.get("type", ""),
                    config=ds_data.get("config", {})
                )
                data_sources.append(data_source)
            
            # Create dashboard model
            return DashboardModel(
                dashboard_id=db_dashboard.dashboard_id,
                title=db_dashboard.title,
                dashboard_type=db_dashboard.dashboard_type,
                channel_id=db_dashboard.channel_id,
                config=config,
                components=components,
                data_sources=data_sources,
                created_at=db_dashboard.created_at,
                updated_at=db_dashboard.updated_at,
                active=db_dashboard.active
            )
            
        except Exception as e:
            logger.error(f"Error converting dashboard entity to model: {e}")
            return None 