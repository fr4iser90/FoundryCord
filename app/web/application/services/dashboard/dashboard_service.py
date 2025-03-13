from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from app.web.domain.dashboard.models import Dashboard, DashboardCreate, DashboardUpdate, Widget, WidgetCreate
from app.web.domain.dashboard.repositories import DashboardRepository


class DashboardService:
    """Service for managing dashboards"""
    
    def __init__(self, dashboard_repository: DashboardRepository):
        self.dashboard_repository = dashboard_repository
        
    async def get_dashboard(self, dashboard_id: str) -> Optional[Dashboard]:
        """Get a dashboard by ID"""
        return await self.dashboard_repository.get_dashboard(dashboard_id)
        
    async def get_user_dashboards(self, user_id: str) -> List[Dashboard]:
        """Get all dashboards for a user"""
        return await self.dashboard_repository.get_user_dashboards(user_id)
        
    async def create_dashboard(self, user_id: str, dashboard: DashboardCreate) -> Dashboard:
        """Create a new dashboard"""
        return await self.dashboard_repository.create_dashboard(user_id, dashboard)
        
    async def update_dashboard(self, dashboard_id: str, dashboard: DashboardUpdate) -> Optional[Dashboard]:
        """Update an existing dashboard"""
        return await self.dashboard_repository.update_dashboard(dashboard_id, dashboard)
        
    async def delete_dashboard(self, dashboard_id: str) -> bool:
        """Delete a dashboard"""
        return await self.dashboard_repository.delete_dashboard(dashboard_id)
        
    async def add_widget(self, dashboard_id: str, widget: WidgetCreate) -> Optional[Widget]:
        """Add a widget to a dashboard"""
        return await self.dashboard_repository.add_widget(dashboard_id, widget)
        
    async def update_widget(self, widget_id: str, widget_data: dict) -> Optional[Widget]:
        """Update a widget"""
        return await self.dashboard_repository.update_widget(widget_id, widget_data)
        
    async def delete_widget(self, widget_id: str) -> bool:
        """Delete a widget"""
        return await self.dashboard_repository.delete_widget(widget_id)
        
    async def get_available_widgets(self) -> List[Dict[str, Any]]:
        """Get list of available widget types and their configurations"""
        # This would typically come from a configuration file or database
        return [
            {
                "type": "discord_channel",
                "name": "Discord Channel",
                "description": "Shows a Discord channel preview",
                "icon": "message-square",
                "min_width": 2,
                "min_height": 2,
                "config_schema": {
                    "channel_id": {"type": "string", "required": True},
                    "show_members": {"type": "boolean", "default": True}
                }
            },
            {
                "type": "system_stats",
                "name": "System Statistics",
                "description": "Shows system statistics like CPU, memory, etc.",
                "icon": "cpu",
                "min_width": 2,
                "min_height": 1,
                "config_schema": {
                    "refresh_interval": {"type": "number", "default": 5}
                }
            },
            {
                "type": "button_panel",
                "name": "Button Panel",
                "description": "A customizable panel with buttons",
                "icon": "grid",
                "min_width": 2,
                "min_height": 2,
                "config_schema": {
                    "buttons": {"type": "array", "items": {
                        "type": "object",
                        "properties": {
                            "label": {"type": "string"},
                            "action": {"type": "string"},
                            "color": {"type": "string", "default": "primary"}
                        }
                    }}
                }
            }
        ] 