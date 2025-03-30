from fastapi import APIRouter, Depends, HTTPException, status
from app.web.application.services.auth.dependencies import get_current_user
from app.web.domain.auth.permissions import Role, require_role
from app.shared.interface.logging.api import get_web_logger
from typing import Dict, List, Optional

logger = get_web_logger()
router = APIRouter(prefix="/v1/dashboard", tags=["Dashboard"])

class DashboardController:
    """Controller für Dashboard-Funktionen"""
    
    def __init__(self):
        self.router = router
        self._register_routes()
    
    def _register_routes(self):
        """Registriert alle Routes für diesen Controller"""
        self.router.get("/widgets")(self.get_available_widgets)
        self.router.get("/layouts")(self.get_layouts)
        self.router.post("/layouts")(self.create_layout)
        self.router.get("/layouts/{layout_id}")(self.get_layout)
        self.router.put("/layouts/{layout_id}")(self.update_layout)
        self.router.delete("/layouts/{layout_id}")(self.delete_layout)
    
    async def get_available_widgets(self, current_user=Depends(get_current_user)):
        """Get all available dashboard widgets"""
        try:
            # Beispiel für verfügbare Widgets
            widgets = [
                {
                    "id": "server_stats",
                    "name": "Server Statistics",
                    "description": "Shows server member counts and activity",
                    "type": "chart",
                    "data_source": "/api/v1/bot-public-info/servers",
                    "refresh_rate": 60,
                    "default_size": {"w": 2, "h": 2},
                    "min_size": {"w": 1, "h": 1},
                    "max_size": {"w": 4, "h": 3}
                },
                {
                    "id": "system_resources",
                    "name": "System Resources",
                    "description": "Shows CPU, memory and disk usage",
                    "type": "gauge",
                    "data_source": "/api/v1/bot-public-info/system-resources",
                    "refresh_rate": 30,
                    "default_size": {"w": 1, "h": 1},
                    "min_size": {"w": 1, "h": 1},
                    "max_size": {"w": 2, "h": 2}
                },
                {
                    "id": "recent_activities",
                    "name": "Recent Activities",
                    "description": "Shows recent bot activities",
                    "type": "table",
                    "data_source": "/api/v1/bot-public-info/recent-activities",
                    "refresh_rate": 30,
                    "default_size": {"w": 2, "h": 2},
                    "min_size": {"w": 1, "h": 1},
                    "max_size": {"w": 4, "h": 4}
                },
                {
                    "id": "popular_commands",
                    "name": "Popular Commands",
                    "description": "Shows most used bot commands",
                    "type": "bar-chart",
                    "data_source": "/api/v1/bot-public-info/popular-commands",
                    "refresh_rate": 120,
                    "default_size": {"w": 2, "h": 2},
                    "min_size": {"w": 1, "h": 1},
                    "max_size": {"w": 3, "h": 3}
                }
            ]
            
            return widgets
        except Exception as e:
            logger.error(f"Error getting widgets: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_layouts(self, current_user=Depends(get_current_user)):
        """Get all dashboard layouts for the current user"""
        try:
            # Hier später tatsächliche Layouts aus der Datenbank laden
            layouts = [
                {
                    "id": 1,
                    "name": "Default Layout",
                    "description": "System default dashboard",
                    "is_default": True,
                    "created_at": "2025-03-01T12:00:00",
                    "updated_at": "2025-03-01T12:00:00"
                },
                {
                    "id": 2,
                    "name": "Server Overview",
                    "description": "Focus on server statistics",
                    "is_default": False,
                    "created_at": "2025-03-02T14:30:00",
                    "updated_at": "2025-03-05T09:15:00"
                }
            ]
            
            return layouts
        except Exception as e:
            logger.error(f"Error getting layouts: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def create_layout(self, layout_data: dict, current_user=Depends(get_current_user)):
        """Create a new dashboard layout"""
        try:
            # Hier später tatsächliche Layout-Erstellung in der Datenbank
            new_layout = {
                "id": 3,  # In der echten Implementierung würde dies die DB generieren
                "name": layout_data.get("name", "New Layout"),
                "description": layout_data.get("description", ""),
                "is_default": False,
                "created_at": "2025-03-10T15:45:00",
                "updated_at": "2025-03-10T15:45:00",
                "widgets": layout_data.get("widgets", [])
            }
            
            return new_layout
        except Exception as e:
            logger.error(f"Error creating layout: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_layout(self, layout_id: int, current_user=Depends(get_current_user)):
        """Get a specific dashboard layout"""
        try:
            # Hier später tatsächliches Layout aus der Datenbank laden
            if layout_id == 1:
                return {
                    "id": 1,
                    "name": "Default Layout",
                    "description": "System default dashboard",
                    "is_default": True,
                    "created_at": "2025-03-01T12:00:00",
                    "updated_at": "2025-03-01T12:00:00",
                    "widgets": [
                        {
                            "id": "server_stats",
                            "position": {"x": 0, "y": 0, "w": 2, "h": 2},
                            "config": {"show_offline": True}
                        },
                        {
                            "id": "system_resources",
                            "position": {"x": 2, "y": 0, "w": 1, "h": 1},
                            "config": {"show_disk": True}
                        },
                        {
                            "id": "recent_activities",
                            "position": {"x": 0, "y": 2, "w": 3, "h": 2},
                            "config": {"limit": 10}
                        }
                    ]
                }
            elif layout_id == 2:
                return {
                    "id": 2,
                    "name": "Server Overview",
                    "description": "Focus on server statistics",
                    "is_default": False,
                    "created_at": "2025-03-02T14:30:00",
                    "updated_at": "2025-03-05T09:15:00",
                    "widgets": [
                        {
                            "id": "server_stats",
                            "position": {"x": 0, "y": 0, "w": 3, "h": 2},
                            "config": {"show_offline": True, "show_details": True}
                        },
                        {
                            "id": "popular_commands",
                            "position": {"x": 0, "y": 2, "w": 2, "h": 2},
                            "config": {"limit": 8}
                        }
                    ]
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Layout with ID {layout_id} not found"
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting layout: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def update_layout(self, layout_id: int, layout_data: dict, current_user=Depends(get_current_user)):
        """Update a dashboard layout"""
        try:
            # Hier später tatsächliches Layout in der Datenbank aktualisieren
            existing_layout = await self.get_layout(layout_id, current_user)
            
            # Update layout with new data
            updated_layout = {**existing_layout}  # Copy existing layout
            
            if "name" in layout_data:
                updated_layout["name"] = layout_data["name"]
                
            if "description" in layout_data:
                updated_layout["description"] = layout_data["description"]
                
            if "widgets" in layout_data:
                updated_layout["widgets"] = layout_data["widgets"]
                
            updated_layout["updated_at"] = "2025-03-10T16:30:00"  # In der echten Implementierung aktuelles Datum
            
            return updated_layout
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating layout: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def delete_layout(self, layout_id: int, current_user=Depends(get_current_user)):
        """Delete a dashboard layout"""
        try:
            # Hier später tatsächliches Layout aus der Datenbank löschen
            if layout_id == 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Default layout cannot be deleted"
                )
            
            # Check if layout exists
            await self.get_layout(layout_id, current_user)
            
            return {"message": f"Layout with ID {layout_id} deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting layout: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

# Für API-Kompatibilität: Exportiere die einzelnen Funktionen auch direkt
dashboard_controller = DashboardController()
get_available_widgets = dashboard_controller.get_available_widgets
get_layouts = dashboard_controller.get_layouts
create_layout = dashboard_controller.create_layout
get_layout = dashboard_controller.get_layout
update_layout = dashboard_controller.update_layout
delete_layout = dashboard_controller.delete_layout 