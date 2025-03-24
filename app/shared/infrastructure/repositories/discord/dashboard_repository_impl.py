from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.infrastructure.models import DashboardEntity, DashboardComponentEntity, ComponentLayoutEntity, ContentTemplateEntity
from typing import Optional, List, Dict, Any
from app.shared.domain.repositories.discord.dashboard_repository import DashboardRepository

class DashboardRepositoryImpl(DashboardRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    # === DashboardEntity Methods ===
    
    async def get_dashboard_by_id(self, dashboard_id: int) -> Optional[DashboardEntity]:
        """Get a dashboard by its ID"""
        result = await self.session.execute(select(DashboardEntity).where(DashboardEntity.id == dashboard_id))
        return result.scalar_one_or_none()
    
    async def get_dashboard_by_type(self, dashboard_type: str, guild_id: str = None) -> Optional[DashboardEntity]:
        """Get a dashboard by its type and optionally guild ID"""
        query = select(DashboardEntity).where(DashboardEntity.dashboard_type == dashboard_type)
        if guild_id:
            query = query.where(DashboardEntity.guild_id == guild_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_dashboards_by_channel(self, channel_id: int) -> List[DashboardEntity]:
        """Get all dashboards for a specific channel"""
        result = await self.session.execute(select(DashboardEntity).where(DashboardEntity.channel_id == channel_id))
        return result.scalars().all()
    
    async def create_dashboard(self, title: str, dashboard_type: str, guild_id: str, 
                               channel_id: int, **kwargs) -> DashboardEntity:
        """Create a new dashboard"""
        dashboard = DashboardEntity(
            title=title,
            dashboard_type=dashboard_type,
            guild_id=guild_id,
            channel_id=channel_id,
            message_id=kwargs.get('message_id'),
            position=kwargs.get('position', 0),
            is_active=kwargs.get('is_active', True),
            update_frequency=kwargs.get('update_frequency', 300),
            config=kwargs.get('config')
        )
        self.session.add(dashboard)
        await self.session.commit()
        return dashboard
    
    async def update_dashboard(self, dashboard: DashboardEntity) -> DashboardEntity:
        """Update an existing dashboard"""
        self.session.add(dashboard)
        await self.session.commit()
        return dashboard
    
    async def delete_dashboard(self, dashboard: DashboardEntity) -> None:
        """Delete a dashboard and all its components"""
        await self.session.delete(dashboard)
        await self.session.commit()
    
    async def create_or_update_dashboard(self, dashboard_type: str, title: str, description: str, guild_id: str) -> DashboardEntity:
        """Create a new dashboard or update if it already exists"""
        # Check if dashboard already exists for this type and guild
        existing = await self.get_dashboard_by_type(dashboard_type, guild_id)
        
        if existing:
            # Update existing dashboard
            existing.title = title
            # Use config to store description since there's no description field directly
            if not existing.config:
                existing.config = {}
            existing.config['description'] = description
            self.session.add(existing)
            await self.session.commit()
            return existing
        else:
            # Create new dashboard - we need a channel_id which we don't have yet
            # Using a placeholder value that will be updated when dashboard is deployed
            channel_id = int(guild_id)  # Temporary placeholder
            
            dashboard = DashboardEntity(
                title=title,
                dashboard_type=dashboard_type,
                guild_id=guild_id,
                channel_id=channel_id,  # Will be updated when dashboard is deployed
                config={'description': description}
            )
            self.session.add(dashboard)
            await self.session.commit()
            return dashboard
    
    # === Component Methods ===
    
    async def get_component_by_id(self, component_id: int) -> Optional[DashboardComponentEntity]:
        """Get a component by its ID"""
        result = await self.session.execute(select(DashboardComponentEntity).where(DashboardComponentEntity.id == component_id))
        return result.scalar_one_or_none()
    
    async def get_components_by_dashboard(self, dashboard_id: int) -> List[DashboardComponentEntity]:
        """Get all components for a dashboard"""
        result = await self.session.execute(
            select(DashboardComponentEntity)
            .where(DashboardComponentEntity.dashboard_id == dashboard_id)
            .order_by(DashboardComponentEntity.position)
        )
        return result.scalars().all()
    
    async def create_component(self, dashboard_id: int, component_type: str, component_name: str, **kwargs) -> DashboardComponentEntity:
        """Create a new dashboard component"""
        component = DashboardComponentEntity(
            dashboard_id=dashboard_id,
            component_type=component_type,
            component_name=component_name,
            custom_id=kwargs.get('custom_id'),
            position=kwargs.get('position', 0),
            is_active=kwargs.get('is_active', True),
            config=kwargs.get('config')
        )
        self.session.add(component)
        await self.session.commit()
        return component
    
    async def update_component(self, component: DashboardComponentEntity) -> DashboardComponentEntity:
        """Update an existing component"""
        self.session.add(component)
        await self.session.commit()
        return component
    
    async def delete_component(self, component: DashboardComponentEntity) -> None:
        """Delete a component"""
        await self.session.delete(component)
        await self.session.commit()
    
    # === Layout Methods ===
    
    async def get_layout_by_component(self, component_id: int) -> Optional[ComponentLayoutEntity]:
        """Get layout for a specific component"""
        result = await self.session.execute(
            select(ComponentLayoutEntity).where(ComponentLayoutEntity.component_id == component_id)
        )
        return result.scalar_one_or_none()
    
    async def create_or_update_layout(self, component_id: int, row: int, column: int, **kwargs) -> ComponentLayoutEntity:
        """Create or update layout for a component"""
        layout = await self.get_layout_by_component(component_id)
        
        if layout:
            layout.row = row
            layout.column = column
            layout.width = kwargs.get('width', layout.width)
            layout.height = kwargs.get('height', layout.height)
            layout.style = kwargs.get('style', layout.style)
            layout.additional_props = kwargs.get('additional_props', layout.additional_props)
        else:
            layout = ComponentLayoutEntity(
                component_id=component_id,
                row=row,
                column=column,
                width=kwargs.get('width', 1),
                height=kwargs.get('height', 1),
                style=kwargs.get('style'),
                additional_props=kwargs.get('additional_props')
            )
            
        self.session.add(layout)
        await self.session.commit()
        return layout
    
    # === Content Template Methods ===
    
    async def get_templates_by_component(self, component_id: int, locale: str = None) -> List[ContentTemplateEntity]:
        """Get content templates for a component"""
        query = select(ContentTemplateEntity).where(ContentTemplateEntity.component_id == component_id)
        if locale:
            query = query.where(ContentTemplateEntity.locale == locale)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def create_template(self, component_id: int, template_type: str, 
                              content: str, **kwargs) -> ContentTemplateEntity:
        """Create a content template"""
        template = ContentTemplateEntity(
            component_id=component_id,
            template_type=template_type,
            locale=kwargs.get('locale', 'en-US'),
            title=kwargs.get('title'),
            content=content,
            variables=kwargs.get('variables')
        )
        self.session.add(template)
        await self.session.commit()
        return template
    
    async def update_template(self, template: ContentTemplateEntity) -> ContentTemplateEntity:
        """Update a content template"""
        self.session.add(template)
        await self.session.commit()
        return template
    
    async def delete_template(self, template: ContentTemplateEntity) -> None:
        """Delete a content template"""
        await self.session.delete(template)
        await self.session.commit()
    
    async def get_all_dashboard_types(self) -> List[str]:
        """Get all available dashboard types"""
        query = select(distinct(DashboardEntity.dashboard_type))
        result = await self.session.execute(query)
        return [row[0] for row in result.fetchall()]
    
    async def get_dashboard_config(self, dashboard_type: str) -> Dict[str, Any]:
        """Get complete configuration for a dashboard type"""
        dashboard = await self.get_dashboard_by_type(dashboard_type)
        if not dashboard:
            return {}
        
        # Build complete configuration
        config = {
            "id": dashboard.id,
            "title": dashboard.title,
            "type": dashboard.dashboard_type,
            "components": {}
        }
        
        # Get all component types for this dashboard
        component_types = ["button", "embed", "selector", "view", "modal"]
        for component_type in component_types:
            components = await self.get_components_by_type(
                dashboard_type=dashboard_type,
                component_type=component_type
            )
            config["components"][component_type] = [
                {
                    "id": comp.id,
                    "title": comp.title,
                    "custom_id": comp.custom_id,
                    # Add other relevant fields
                }
                for comp in components
            ]
        
        return config
