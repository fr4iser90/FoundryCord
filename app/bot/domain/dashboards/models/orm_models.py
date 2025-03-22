"""ORM models for dashboard persistence.

This module provides domain-centric access to dashboard database models.
Instead of redefining tables, it imports and uses the existing database models.
"""
from typing import Dict, List, Any, Optional

# Import the actual database models - these are the source of truth
from app.shared.infrastructure.models import Dashboard as DBDashboard
from app.shared.infrastructure.models import DashboardComponent as DBDashboardComponent

# Import domain models for conversion
from app.bot.domain.dashboards.models.dashboard_model import DashboardModel
from app.bot.domain.dashboards.models.component_model import ComponentModel

class DashboardORM:
    """Adapter between Dashboard domain models and database ORM models.
    
    This class provides methods to convert between domain models and database models.
    It doesn't define new tables but uses the existing ones.
    """
    
    @staticmethod
    def from_domain(dashboard_model: DashboardModel) -> DBDashboard:
        """Convert domain model to database model."""
        db_dashboard = DBDashboard(
            id=dashboard_model.id if hasattr(dashboard_model, 'id') else None,
            title=dashboard_model.title,
            dashboard_type=dashboard_model.type,
            guild_id=dashboard_model.guild_id,
            channel_id=dashboard_model.channel_id,
            message_id=dashboard_model.message_id,
            position=dashboard_model.position,
            is_active=dashboard_model.is_active,
            update_frequency=dashboard_model.update_frequency,
            config=dashboard_model.config
        )
        
        # Add components if they exist
        if hasattr(dashboard_model, 'components') and dashboard_model.components:
            db_dashboard.components = [
                ComponentORM.from_domain(comp, db_dashboard.id) 
                for comp in dashboard_model.components
            ]
            
        return db_dashboard
    
    @staticmethod
    def to_domain(db_dashboard: DBDashboard) -> DashboardModel:
        """Convert database model to domain model."""
        return DashboardModel(
            id=db_dashboard.id,
            title=db_dashboard.title,
            type=db_dashboard.dashboard_type,
            guild_id=db_dashboard.guild_id,
            channel_id=db_dashboard.channel_id,
            message_id=db_dashboard.message_id,
            position=db_dashboard.position,
            is_active=db_dashboard.is_active,
            update_frequency=db_dashboard.update_frequency,
            config=db_dashboard.config or {},
            components=[ComponentORM.to_domain(comp) for comp in db_dashboard.components]
        )


class ComponentORM:
    """Adapter between Component domain models and database ORM models."""
    
    @staticmethod
    def from_domain(component_model: ComponentModel, dashboard_id: Optional[int] = None) -> DBDashboardComponent:
        """Convert domain model to database model."""
        return DBDashboardComponent(
            id=component_model.id if hasattr(component_model, 'id') and not isinstance(component_model.id, str) else None,
            dashboard_id=dashboard_id,
            component_type=component_model.type,
            component_name=component_model.title or f"Component-{component_model.type}",
            custom_id=str(component_model.id),
            position=component_model.position_x,  # Use x position as order
            is_active=True,
            config=component_model.config,
            # Create the layout relationship
            layout=ComponentLayoutORM.from_domain(component_model)
        )
    
    @staticmethod
    def to_domain(db_component: DBDashboardComponent) -> ComponentModel:
        """Convert database model to domain model."""
        # Get the layout data if it exists
        pos_x = 0
        pos_y = 0
        width = 1
        height = 1
        
        if db_component.layout:
            pos_x = db_component.layout.column
            pos_y = db_component.layout.row
            width = db_component.layout.width
            height = db_component.layout.height
            
        return ComponentModel(
            id=str(db_component.id),
            type=db_component.component_type,
            title=db_component.component_name,
            position_x=pos_x,
            position_y=pos_y,
            width=width,
            height=height,
            config=db_component.config or {}
        )


class ComponentLayoutORM:
    """Helper for component layout conversion."""
    
    @staticmethod
    def from_domain(component_model: ComponentModel):
        """Create a component layout from a domain model."""
        from app.shared.infrastructure.models.component_layout import ComponentLayout
        
        return ComponentLayout(
            row=component_model.position_y,
            column=component_model.position_x,
            width=component_model.width,
            height=component_model.height,
            style=None,
            additional_props={}
        )

# Add references to the actual database models
# These are just shortcuts to the underlying models
Dashboard = DBDashboard
DashboardComponent = DBDashboardComponent 