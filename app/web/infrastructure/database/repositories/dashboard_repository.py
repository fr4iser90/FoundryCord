from typing import List, Optional, Dict, Any
import uuid
import json
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.web.domain.dashboard_builder.models import Dashboard, DashboardCreate, DashboardUpdate, Widget, WidgetCreate
from app.web.domain.dashboard_builder.repositories import DashboardRepository
from app.web.infrastructure.database.models import DashboardModel, WidgetModel


class SQLAlchemyDashboardRepository(DashboardRepository):
    """SQLAlchemy implementation of DashboardRepository using DashboardMessage table"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def get_dashboard(self, dashboard_id: str) -> Optional[Dashboard]:
        """Get a dashboard by ID"""
        query = select(DashboardModel).where(DashboardModel.dashboard_type.like(f"%{dashboard_id}%"))
        result = await self.session.execute(query)
        dashboard_model = result.scalars().first()
        
        if not dashboard_model:
            return None
            
        return self._model_to_entity(dashboard_model, dashboard_id)
        
    async def get_user_dashboards(self, user_id: str) -> List[Dashboard]:
        """Get all dashboards for a user"""
        query = select(DashboardModel).where(DashboardModel.dashboard_type.like(f"{user_id}_%"))
        result = await self.session.execute(query)
        dashboard_models = result.scalars().all()
        
        dashboards = []
        for model in dashboard_models:
            # Extract dashboard ID from dashboard_type
            parts = model.dashboard_type.split('_')
            if len(parts) > 1:
                dashboard_id = parts[1]
                dashboards.append(self._model_to_entity(model, dashboard_id))
        
        return dashboards
        
    async def create_dashboard(self, user_id: str, dashboard: DashboardCreate) -> Dashboard:
        """Create a new dashboard by storing it in DashboardMessage"""
        dashboard_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Create a dashboard_type that includes user_id and dashboard_id
        dashboard_type = f"{user_id}_{dashboard_id}"
        
        # Store dashboard data in message_id as a reference for now
        # In a real implementation, you might store this in a JSON field
        # or implement full serialization to the message content
        dashboard_model = DashboardModel(
            dashboard_type=dashboard_type,
            message_id=0,  # Placeholder
            channel_id=0,  # Placeholder
            updated_at=now
        )
        
        self.session.add(dashboard_model)
        await self.session.commit()
        await self.session.refresh(dashboard_model)
        
        # Build the entity to return
        return Dashboard(
            id=dashboard_id,
            user_id=user_id,
            title=dashboard.title,
            description=dashboard.description or "",
            layout_config=dashboard.layout_config or {},
            is_public=dashboard.is_public or False,
            created_at=now,
            updated_at=now,
            widgets=[]  # No widgets initially
        )
        
    async def update_dashboard(self, dashboard_id: str, dashboard: DashboardUpdate) -> Optional[Dashboard]:
        """Update an existing dashboard"""
        query = select(DashboardModel).where(DashboardModel.id == dashboard_id).options(selectinload(DashboardModel.widgets))
        result = await self.session.execute(query)
        dashboard_model = result.scalars().first()
        
        if not dashboard_model:
            return None
            
        # Update dashboard properties
        dashboard_model.title = dashboard.title
        dashboard_model.description = dashboard.description
        dashboard_model.layout_config = dashboard.layout_config
        dashboard_model.is_public = dashboard.is_public
        dashboard_model.updated_at = datetime.utcnow()
        
        await self.session.commit()
        await self.session.refresh(dashboard_model)
        
        return self._model_to_entity(dashboard_model, dashboard_id)
        
    async def delete_dashboard(self, dashboard_id: str) -> bool:
        """Delete a dashboard"""
        query = select(DashboardModel).where(DashboardModel.id == dashboard_id)
        result = await self.session.execute(query)
        dashboard_model = result.scalars().first()
        
        if not dashboard_model:
            return False
            
        await self.session.delete(dashboard_model)
        await self.session.commit()
        
        return True
        
    async def add_widget(self, dashboard_id: str, widget: WidgetCreate) -> Optional[Widget]:
        """Add a widget to a dashboard"""
        # Check if dashboard exists
        query = select(DashboardModel).where(DashboardModel.id == dashboard_id)
        result = await self.session.execute(query)
        dashboard_model = result.scalars().first()
        
        if not dashboard_model:
            return None
            
        widget_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        widget_model = WidgetModel(
            id=widget_id,
            dashboard_id=dashboard_id,
            widget_type=widget.widget_type,
            title=widget.title,
            position_x=widget.position_x,
            position_y=widget.position_y,
            width=widget.width,
            height=widget.height,
            config=widget.config,
            created_at=now,
            updated_at=now
        )
        
        self.session.add(widget_model)
        await self.session.commit()
        await self.session.refresh(widget_model)
        
        return Widget(
            id=widget_model.id,
            dashboard_id=widget_model.dashboard_id,
            widget_type=widget_model.widget_type,
            title=widget_model.title,
            position_x=widget_model.position_x,
            position_y=widget_model.position_y,
            width=widget_model.width,
            height=widget_model.height,
            config=widget_model.config,
            created_at=widget_model.created_at,
            updated_at=widget_model.updated_at
        )
        
    async def update_widget(self, widget_id: str, widget_data: dict) -> Optional[Widget]:
        """Update a widget"""
        query = select(WidgetModel).where(WidgetModel.id == widget_id)
        result = await self.session.execute(query)
        widget_model = result.scalars().first()
        
        if not widget_model:
            return None
            
        # Update widget fields
        for key, value in widget_data.items():
            if hasattr(widget_model, key):
                setattr(widget_model, key, value)
                
        widget_model.updated_at = datetime.utcnow()
        
        await self.session.commit()
        await self.session.refresh(widget_model)
        
        return Widget(
            id=widget_model.id,
            dashboard_id=widget_model.dashboard_id,
            widget_type=widget_model.widget_type,
            title=widget_model.title,
            position_x=widget_model.position_x,
            position_y=widget_model.position_y,
            width=widget_model.width,
            height=widget_model.height,
            config=widget_model.config,
            created_at=widget_model.created_at,
            updated_at=widget_model.updated_at
        )
        
    async def delete_widget(self, widget_id: str) -> bool:
        """Delete a widget"""
        query = select(WidgetModel).where(WidgetModel.id == widget_id)
        result = await self.session.execute(query)
        widget_model = result.scalars().first()
        
        if not widget_model:
            return False
            
        await self.session.delete(widget_model)
        await self.session.commit()
        
        return True
        
    def _model_to_entity(self, model: DashboardModel, dashboard_id: str) -> Dashboard:
        """Convert a DashboardModel to a Dashboard entity"""
        # Create a basic dashboard entity
        return Dashboard(
            id=dashboard_id,
            user_id=model.user_id,
            title=model.title or "Dashboard", 
            description=model.description or "",
            layout_config=model.layout_config or {},
            is_public=model.is_public or False,
            created_at=model.updated_at,
            updated_at=model.updated_at,
            widgets=[]  # Empty widgets list since we don't store them separately
        ) 