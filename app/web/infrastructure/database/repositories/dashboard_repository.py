from typing import List, Optional, Dict, Any
import uuid
import json
import logging
from datetime import datetime
from sqlalchemy import select, text, Table, MetaData
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.web.domain.dashboard_builder.models import Dashboard, DashboardCreate, DashboardUpdate, Widget, WidgetCreate
from app.web.domain.dashboard_builder.repositories import DashboardRepository
from app.web.infrastructure.database.models import DashboardModel, WidgetModel
from app.shared.interface.logging.api import get_bot_logger

logger = get_bot_logger()

class SQLAlchemyDashboardRepository(DashboardRepository):
    """SQLAlchemy implementation of dashboard repository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_dashboard(self, dashboard_id: str) -> Optional[Dashboard]:
        """Get a dashboard by ID"""
        try:
            # First let's inspect the table to understand its structure
            # We'll use a more general query that's guaranteed to work
            query = f"SELECT * FROM dashboards WHERE id = :dashboard_id LIMIT 1"
            result = await self.session.execute(text(query), {"dashboard_id": dashboard_id})
            row = result.fetchone()
            
            if not row:
                logger.warning(f"Dashboard with ID {dashboard_id} not found")
                return None
            
            # Log column names for debugging
            column_names = row._mapping.keys()
            logger.info(f"Dashboard table columns: {', '.join(column_names)}")
            
            return self._row_to_entity(dashboard_id, row)
            
        except Exception as e:
            logger.error(f"Error getting dashboard: {str(e)}")
            return None
    
    async def get_user_dashboards(self, user_id: str) -> List[Dashboard]:
        """Get all dashboards owned by a user
        
        This is a flexible function that tries different column names
        that might relate dashboards to users.
        """
        try:
            # First, let's get all dashboards and examine their structure
            query_all = "SELECT * FROM dashboards LIMIT 1"
            result_structure = await self.session.execute(text(query_all))
            sample_row = result_structure.fetchone()
            
            if not sample_row:
                # No dashboards at all
                logger.warning("No dashboards found in the database")
                return []
            
            # Check which columns exist
            columns = sample_row._mapping.keys()
            logger.info(f"Dashboard table columns: {', '.join(columns)}")
            
            # Try different possible column names for user association
            possible_user_columns = ['user_id', 'channel_id', 'owner_id', 'creator_id', 'created_by']
            
            # Find which user column exists
            user_column = None
            for col in possible_user_columns:
                if col in columns:
                    user_column = col
                    break
            
            dashboards = []
            
            if user_column:
                # We found a column that might relate to users
                logger.info(f"Using column '{user_column}' to filter dashboards by user")
                query = f"SELECT * FROM dashboards WHERE {user_column} = :user_id"
                result = await self.session.execute(text(query), {"user_id": user_id})
            else:
                # If no user-related column is found, just get all dashboards
                logger.warning("No user-related column found in dashboards table, returning all dashboards")
                query = "SELECT * FROM dashboards"
                result = await self.session.execute(text(query))
            
            rows = result.fetchall()
            
            # Convert rows to dashboard entities
            for row in rows:
                dashboard_id = row.id if hasattr(row, 'id') else str(uuid.uuid4())
                dashboard = self._row_to_entity(dashboard_id, row)
                dashboards.append(dashboard)
            
            return dashboards
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user dashboards: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting user dashboards: {str(e)}")
            return []
    
    async def create_dashboard(self, dashboard: DashboardCreate) -> Optional[Dashboard]:
        """Create a new dashboard"""
        dashboard_id = str(uuid.uuid4())
        try:
            # Get table column names first to ensure we use the right columns
            query_structure = "SELECT * FROM dashboards LIMIT 0"
            result_structure = await self.session.execute(text(query_structure))
            columns = result_structure.keys()
            logger.info(f"Available dashboard columns: {', '.join(columns)}")
            
            # Build a dynamic query based on available columns
            create_values = {}
            if 'id' in columns:
                create_values['id'] = dashboard_id
            if 'title' in columns:
                create_values['title'] = dashboard.title
            if 'description' in columns:
                create_values['description'] = dashboard.description
            if 'is_public' in columns:
                create_values['is_public'] = dashboard.is_public
            if 'user_id' in columns:
                create_values['user_id'] = dashboard.user_id
            if 'channel_id' in columns and hasattr(dashboard, 'channel_id'):
                create_values['channel_id'] = dashboard.channel_id
            if 'layout_config' in columns:
                create_values['layout_config'] = json.dumps(dashboard.layout_config)
            if 'created_at' in columns:
                create_values['created_at'] = datetime.utcnow()
            if 'updated_at' in columns:
                create_values['updated_at'] = datetime.utcnow()
                
            # Only proceed if we have at least some valid columns
            if not create_values:
                logger.error("No valid columns found for creating dashboard")
                return None
                
            # Build the insertion query
            columns_str = ', '.join(create_values.keys())
            placeholders = ', '.join([f":{k}" for k in create_values.keys()])
            query = f"INSERT INTO dashboards ({columns_str}) VALUES ({placeholders}) RETURNING *"
            
            result = await self.session.execute(text(query), create_values)
            await self.session.commit()
            
            row = result.fetchone()
            if not row:
                return None
                
            return self._row_to_entity(dashboard_id, row)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating dashboard: {str(e)}")
            return None
    
    async def update_dashboard(self, dashboard_id: str, dashboard: DashboardUpdate) -> Optional[Dashboard]:
        """Update a dashboard"""
        try:
            # First check if the dashboard exists
            check_query = "SELECT * FROM dashboards WHERE id = :dashboard_id"
            result = await self.session.execute(text(check_query), {"dashboard_id": dashboard_id})
            existing = result.fetchone()
            
            if not existing:
                logger.warning(f"Dashboard with ID {dashboard_id} not found for update")
                return None
            
            # Get available columns
            columns = existing._mapping.keys()
            
            # Build update values
            update_values = {"dashboard_id": dashboard_id}
            set_clauses = []
            
            if 'title' in columns and dashboard.title:
                update_values['title'] = dashboard.title
                set_clauses.append("title = :title")
                
            if 'description' in columns and dashboard.description:
                update_values['description'] = dashboard.description
                set_clauses.append("description = :description")
                
            if 'is_public' in columns and dashboard.is_public is not None:
                update_values['is_public'] = dashboard.is_public
                set_clauses.append("is_public = :is_public")
                
            if 'layout_config' in columns and dashboard.layout_config:
                update_values['layout_config'] = json.dumps(dashboard.layout_config)
                set_clauses.append("layout_config = :layout_config")
                
            if 'updated_at' in columns:
                update_values['updated_at'] = datetime.utcnow()
                set_clauses.append("updated_at = :updated_at")
            
            # Only update if we have something to update
            if not set_clauses:
                logger.warning("No fields to update in dashboard")
                return self._row_to_entity(dashboard_id, existing)
            
            # Build the update query
            set_clause = ", ".join(set_clauses)
            query = f"UPDATE dashboards SET {set_clause} WHERE id = :dashboard_id RETURNING *"
            
            result = await self.session.execute(text(query), update_values)
            await self.session.commit()
            
            row = result.fetchone()
            if not row:
                return None
                
            return self._row_to_entity(dashboard_id, row)
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating dashboard: {str(e)}")
            return None
    
    async def delete_dashboard(self, dashboard_id: str) -> bool:
        """Delete a dashboard"""
        try:
            query = "DELETE FROM dashboards WHERE id = :dashboard_id"
            await self.session.execute(text(query), {"dashboard_id": dashboard_id})
            await self.session.commit()
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting dashboard: {str(e)}")
            return False
    
    async def add_widget(self, dashboard_id: str, widget: WidgetCreate) -> Optional[Widget]:
        """Add a widget to a dashboard
        
        Note: This depends on whether the database has a separate widgets table or if widgets
        are stored as part of the dashboard JSON. We'll implement a more sophisticated approach later.
        """
        # For now, just implement a dummy version that returns a fake widget
        # This will need to be implemented properly based on the actual database schema
        return Widget(
            id=str(uuid.uuid4()),
            dashboard_id=dashboard_id,
            widget_type=widget.widget_type,
            position=widget.position,
            size=widget.size,
            data=widget.data,
            config=widget.config
        )
    
    async def update_widget(self, widget_id: str, widget_data: Dict[str, Any]) -> Optional[Widget]:
        """Update a widget
        
        Note: This is a placeholder implementation. The actual implementation would depend
        on how widgets are stored in the database.
        """
        try:
            # This is a dummy implementation that just returns a mock widget
            # In a real implementation, we would:
            # 1. Find the widget by ID
            # 2. Update its properties
            # 3. Save the changes to the database
            # 4. Return the updated widget
            
            logger.info(f"Placeholder: Update widget {widget_id} with data: {widget_data}")
            
            # Return a mock widget with the updated data
            return Widget(
                id=widget_id,
                dashboard_id=widget_data.get('dashboard_id', 'unknown'),
                widget_type=widget_data.get('widget_type', 'generic'),
                position=widget_data.get('position', {"x": 0, "y": 0}),
                size=widget_data.get('size', {"width": 1, "height": 1}),
                data=widget_data.get('data', {}),
                config=widget_data.get('config', {})
            )
        except Exception as e:
            logger.error(f"Error updating widget: {str(e)}")
            return None
        
    async def delete_widget(self, widget_id: str) -> bool:
        """Delete a widget"""
        # Placeholder - real implementation depends on actual schema
        return True
        
    def _row_to_entity(self, dashboard_id: str, row) -> Dashboard:
        """Convert a database row to a Dashboard entity
        
        This is designed to be very flexible and handle different column names.
        """
        try:
            # Get all available column names
            columns = row._mapping.keys()
            
            # Extract data with fallbacks for missing columns
            user_id = None
            for col in ['user_id', 'channel_id', 'owner_id', 'creator_id', 'created_by']:
                if col in columns and getattr(row, col) is not None:
                    user_id = str(getattr(row, col))
                    break
                    
            title = getattr(row, 'title', None) or getattr(row, 'name', None) or "Dashboard"
            description = getattr(row, 'description', None) or ""
            
            # Handle layout config (might be JSON string or dictionary)
            layout_config = {}
            if 'layout_config' in columns:
                config_data = getattr(row, 'layout_config')
                if isinstance(config_data, str):
                    try:
                        layout_config = json.loads(config_data)
                    except:
                        layout_config = {}
                elif isinstance(config_data, dict):
                    layout_config = config_data
            
            is_public = getattr(row, 'is_public', False)
            created_at = getattr(row, 'created_at', datetime.utcnow())
            updated_at = getattr(row, 'updated_at', datetime.utcnow())
            
            # Construct the Dashboard entity
            return Dashboard(
                id=dashboard_id,
                user_id=user_id or "unknown",
                title=title,
                description=description,
                layout_config=layout_config,
                is_public=is_public,
                created_at=created_at,
                updated_at=updated_at,
                widgets=[]  # We'll handle widgets separately if needed
            )
        except Exception as e:
            logger.error(f"Error converting row to entity: {str(e)}")
            # Return a minimal dashboard as fallback
            return Dashboard(
                id=dashboard_id,
                user_id="unknown",
                title="Dashboard",
                description="",
                layout_config={},
                is_public=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                widgets=[]
            ) 