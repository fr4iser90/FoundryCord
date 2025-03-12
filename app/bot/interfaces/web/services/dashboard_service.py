from typing import Dict, Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.future import select
from ..models.database import Dashboard, DashboardComponent
import logging
import json
from datetime import datetime

logger = logging.getLogger("web_interface.dashboard_service")

class DashboardService:
    """
    Service for dashboard-related operations
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_dashboards_by_user(self, user_id: str) -> List[Dashboard]:
        """
        Get all dashboards for a user
        """
        query = select(Dashboard).filter(Dashboard.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_dashboard_by_id(self, dashboard_id: int) -> Optional[Dashboard]:
        """
        Get dashboard by ID
        """
        query = select(Dashboard).filter(Dashboard.id == dashboard_id)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def create_dashboard(
        self,
        user_id: str,
        title: str,
        dashboard_type: str,
        layout: str,
        description: Optional[str] = None,
        is_public: bool = False,
        server_id: Optional[str] = None
    ) -> Dashboard:
        """
        Create a new dashboard
        """
        dashboard = Dashboard(
            user_id=user_id,
            title=title,
            description=description,
            dashboard_type=dashboard_type,
            layout=layout,
            is_public=is_public,
            server_id=server_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.db.add(dashboard)
        await self.db.commit()
        await self.db.refresh(dashboard)
        
        return dashboard
    
    async def update_dashboard(
        self,
        dashboard_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        layout: Optional[str] = None,
        is_public: Optional[bool] = None
    ) -> bool:
        """
        Update a dashboard
        """
        update_data = {}
        
        if title is not None:
            update_data["title"] = title
        
        if description is not None:
            update_data["description"] = description
        
        if layout is not None:
            update_data["layout"] = layout
        
        if is_public is not None:
            update_data["is_public"] = is_public
        
        update_data["updated_at"] = datetime.utcnow()
        
        if not update_data:
            return True
        
        query = (
            update(Dashboard)
            .where(Dashboard.id == dashboard_id)
            .values(**update_data)
        )
        
        await self.db.execute(query)
        await self.db.commit()
        
        return True
    
    async def delete_dashboard(self, dashboard_id: int) -> bool:
        """
        Delete a dashboard
        """
        # First delete related components
        component_query = delete(DashboardComponent).where(
            DashboardComponent.dashboard_id == dashboard_id
        )
        await self.db.execute(component_query)
        
        # Then delete the dashboard
        dashboard_query = delete(Dashboard).where(Dashboard.id == dashboard_id)
        await self.db.execute(dashboard_query)
        
        await self.db.commit()
        
        return True
    
    async def get_dashboard_components(self, dashboard_id: int) -> List[DashboardComponent]:
        """
        Get all components for a dashboard
        """
        query = select(DashboardComponent).filter(
            DashboardComponent.dashboard_id == dashboard_id
        )
        result = await self.db.execute(query)
        return result.scalars().all() 