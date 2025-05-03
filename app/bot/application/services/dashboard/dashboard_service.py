"""Dashboard service for coordinating dashboard operations."""
from typing import Dict, Any, List, Optional
import nextcord
from datetime import datetime
import asyncio

from app.shared.interface.logging.api import get_bot_logger
logger = get_bot_logger()

from app.shared.infrastructure.models.dashboards.dashboard_entity import DashboardEntity
from app.shared.domain.repositories import DashboardRepository
from app.bot.infrastructure.factories.component_registry import ComponentRegistry
from app.bot.infrastructure.factories.data_source_registry import DataSourceRegistry
from app.shared.infrastructure.database.core.config import get_session

class DashboardService:
    """Core service for dashboard operations."""
    
    def __init__(self, 
                 bot,
                 repository: DashboardRepository,
                 component_registry: ComponentRegistry,
                 data_source_registry: DataSourceRegistry):
        self.bot = bot
        self.repository = repository
        self.component_registry = component_registry
        self.data_source_registry = data_source_registry
        
    async def get_dashboard(self, dashboard_id: str) -> Optional[DashboardEntity]:
        """Get a dashboard by ID."""
        return await self.repository.get_by_id(dashboard_id)
    
    async def get_dashboard_by_channel(self, channel_id: int) -> Optional[DashboardEntity]:
        """Get a dashboard for a channel."""
        return await self.repository.get_by_channel_id(channel_id)
    
    async def create_dashboard(self, dashboard_data: Dict[str, Any]) -> DashboardEntity:
        """Create a new dashboard from configuration."""
        # Convert raw data to domain model
        dashboard = self._create_dashboard_entity(dashboard_data)
        
        # Save to repository
        saved_dashboard = await self.repository.save(dashboard)
        
        logger.info(f"Created new dashboard: {saved_dashboard.id} ({saved_dashboard.name})")
        return saved_dashboard
    
    async def update_dashboard(self, dashboard_id: str, dashboard_data: Dict[str, Any]) -> Optional[DashboardEntity]:
        """Update an existing dashboard."""
        dashboard = await self.repository.get_by_id(dashboard_id)
        if not dashboard:
            logger.warning(f"Attempted to update non-existent dashboard: {dashboard_id}")
            return None
            
        # Update dashboard properties
        for key, value in dashboard_data.items():
            if hasattr(dashboard, key):
                setattr(dashboard, key, value)
                
        # Update timestamp
        dashboard.updated_at = datetime.now()
        
        # Save updated dashboard
        updated_dashboard = await self.repository.save(dashboard)
        
        logger.info(f"Updated dashboard: {updated_dashboard.id}")
        return updated_dashboard
    
    async def delete_dashboard(self, dashboard_id: str) -> bool:
        """Delete a dashboard."""
        result = await self.repository.delete(dashboard_id)
        if result:
            logger.info(f"Deleted dashboard: {dashboard_id}")
        return result
    
    async def get_all_dashboards(self) -> List[DashboardEntity]:
        """Get all dashboards."""
        try:
            return await self.repository.get_all_dashboards()
        except Exception as e:
            logger.error(f"Error getting all dashboards: {e}")
            return []
    
    # Removed redundant refresh_dashboard_data method
    # Data fetching is handled by DashboardDataService triggered by DashboardController
    
    async def sync_dashboard_from_snapshot(self, channel: nextcord.TextChannel, config_json: Dict[str, Any]) -> bool:
        """Creates or updates a dashboard entity and its config from a snapshot, then activates/updates the controller."""
        logger.info(f"Syncing dashboard from snapshot for channel {channel.id} ({channel.name})")
        
        entity_id = None
        message_id = None
        config_id = None
        
        try:
            # 1. Save/Update the configuration blob
            # Assume config_json contains an 'id' if it was previously saved, otherwise save_dashboard_config generates one
            config_id = await self.repository.save_dashboard_config(config_json)
            if not config_id:
                logger.error(f"Failed to save dashboard config snapshot for channel {channel.id}")
                return False
            logger.debug(f"Saved/updated config blob with ID: {config_id}")

            # 2. Find or Create the DashboardEntity
            existing_entity = await self.repository.get_by_channel_id(channel.id)
            
            dashboard_type = config_json.get('dashboard_type', 'dynamic') # Default type?
            
            if existing_entity:
                logger.debug(f"Found existing DashboardEntity {existing_entity.id} for channel {channel.id}")
                entity_id = existing_entity.id
                message_id = existing_entity.message_id # Store existing message ID
                
                # Check if updates are needed
                update_data = {}
                if existing_entity.config_id != config_id:
                    update_data['config_id'] = config_id
                if existing_entity.dashboard_type != dashboard_type:
                     update_data['dashboard_type'] = dashboard_type
                # Add other fields to check/update if necessary (e.g., from config)
                
                if update_data:
                    update_data['updated_at'] = datetime.now() # Always update timestamp
                    logger.info(f"Updating DashboardEntity {entity_id} with data: {update_data}")
                    # TODO: Need to adapt repository update method or use session directly 
                    # success = await self.repository.update_dashboard(entity_id, update_data)
                    # For now, assume direct update will work if repo method handles it
                    async with self.repository.session_factory() as session:
                       stmt = update(DashboardEntity).where(DashboardEntity.id == entity_id).values(**update_data)
                       await session.execute(stmt)
                       await session.commit()
                       logger.debug(f"Successfully updated DashboardEntity {entity_id}")
                else:
                    logger.debug(f"No updates needed for DashboardEntity {entity_id}")

            else:
                logger.info(f"No existing DashboardEntity found for channel {channel.id}. Creating new one.")
                new_entity = await self.repository.create_dashboard_entity(
                    channel_id=channel.id,
                    guild_id=channel.guild.id,
                    config_id=config_id,
                    dashboard_type=dashboard_type,
                    # Extract other fields from config? Example:
                    name=config_json.get('name', 'Templated Dashboard'),
                    description=config_json.get('description', ''),
                    is_active=True # Assume active when created from template
                )
                if not new_entity:
                    logger.error(f"Failed to create DashboardEntity for channel {channel.id}")
                    return False
                entity_id = new_entity.id
                message_id = None # New entity won't have a message ID yet
                
            # 3. Activate or Update the Controller via Registry
            try:
                # Assuming self.bot has a reference to the registry
                if not hasattr(self.bot, 'dashboard_registry') or not self.bot.dashboard_registry:
                    logger.error("DashboardRegistry not found on bot object!")
                    return False 
                    
                registry = self.bot.dashboard_registry
                success = await registry.activate_or_update_dashboard(
                    channel_id=channel.id, 
                    config_id=config_id, 
                    message_id=message_id # Pass the message_id we found/know
                )
                if not success:
                    logger.error(f"Failed to activate/update dashboard controller for channel {channel.id}")
                    # Don't necessarily fail the whole sync? Maybe just log error.
                    # return False 
                else:
                     logger.info(f"Successfully activated/updated dashboard controller for channel {channel.id}")
            except Exception as reg_err:
                 logger.error(f"Error during dashboard registry activation/update for channel {channel.id}: {reg_err}", exc_info=True)
                 # return False

            # 4. Persist the message_id back to the DB Entity
            # This needs to happen *after* activate_or_update potentially creates/updates the message
            try:
                # Get the potentially updated controller instance
                registry = self.bot.dashboard_registry # Get registry again just in case
                controller = registry.get_dashboard(channel.id)
                
                if controller and controller.message_id:
                    new_message_id = controller.message_id
                    # Check if message_id actually changed or needs storing
                    if message_id != new_message_id: 
                        logger.info(f"Persisting new/updated message_id {new_message_id} for DashboardEntity {entity_id}")
                        # Use the repository's update method or session directly
                        async with self.repository.session_factory() as session:
                            stmt = update(DashboardEntity).where(DashboardEntity.id == entity_id).values(message_id=str(new_message_id)) # Store as string?
                            await session.execute(stmt)
                            await session.commit()
                            logger.debug(f"Successfully persisted message_id {new_message_id} for entity {entity_id}")
                        message_id = new_message_id # Update local variable too
                    else:
                         logger.debug(f"Message ID {message_id} is already persisted for entity {entity_id}. No update needed.")
                elif controller:
                     logger.warning(f"Controller for channel {channel.id} exists, but has no message_id set after activation/update.")
                else:
                     logger.warning(f"Could not retrieve controller for channel {channel.id} after activation/update to persist message_id.")
            except Exception as persist_err:
                 logger.error(f"Error persisting message_id for entity {entity_id} / channel {channel.id}: {persist_err}", exc_info=True)
            # --------------------------------------------------------------------------

            return True # Return True assuming the main parts worked

        except Exception as e:
            logger.error(f"Error in sync_dashboard_from_snapshot for channel {channel.id}: {e}", exc_info=True)
            return False

    def _create_dashboard_entity(self, data: Dict[str, Any]) -> DashboardEntity:
        """Convert dictionary data to a DashboardEntity."""
        from app.shared.infrastructure.models.dashboards.dashboard_entity import DashboardEntity
        from app.shared.infrastructure.models.dashboards.dashboard_component_entity import DashboardComponentEntity
        from app.shared.infrastructure.models.dashboards.component_layout_entity import ComponentLayoutEntity
        
        # Create base dashboard
        dashboard = DashboardEntity(
            id=data.get('id'),
            dashboard_type=data.get('dashboard_type'),
            name=data.get('name'),
            description=data.get('description'),
            channel_id=data.get('channel_id'),
            guild_id=data.get('guild_id'),
            is_active=data.get('is_active', True),
            update_frequency=data.get('update_frequency', 300),
            config=data.get('config', {})
        )
        
        # Add components
        for comp_data in data.get('components', []):
            component = DashboardComponentEntity(
                id=comp_data.get('id'),
                dashboard_id=dashboard.id,
                component_type=comp_data.get('component_type'),
                component_name=comp_data.get('component_name'),
                custom_id=comp_data.get('custom_id'),
                position=comp_data.get('position', 0),
                is_active=comp_data.get('is_active', True),
                config=comp_data.get('config', {})
            )
            dashboard.components.append(component)
            
            # Add layout if specified
            if 'layout' in comp_data:
                layout = ComponentLayoutEntity(
                    component_id=component.id,
                    row_position=comp_data['layout'].get('row', 0),
                    col_position=comp_data['layout'].get('col', 0),
                    width=comp_data['layout'].get('width', 1),
                    height=comp_data['layout'].get('height', 1),
                    style=comp_data['layout'].get('style'),
                    additional_props=comp_data['layout'].get('additional_props')
                )
                component.layout = layout
            
        return dashboard

    async def ensure_dashboard_tables_exist(self):
        """Ensure all required dashboard tables exist in the database."""
        try:
            # Create dashboards table first
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS dashboards (
                    id SERIAL PRIMARY KEY,
                    dashboard_type VARCHAR(50) NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    guild_id VARCHAR(50),
                    channel_id VARCHAR(50),
                    is_active BOOLEAN DEFAULT TRUE,
                    update_frequency INTEGER DEFAULT 300,
                    config JSONB,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Create indexes separately
            await self.db.execute("""
                CREATE INDEX IF NOT EXISTS idx_dashboards_dashboard_type 
                ON dashboards(dashboard_type)
            """)
            
            await self.db.execute("""
                CREATE INDEX IF NOT EXISTS idx_dashboards_guild_id 
                ON dashboards(guild_id)
            """)
            
            # Create dashboard_components table before component_layouts
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS dashboard_components (
                    id SERIAL PRIMARY KEY,
                    dashboard_id INTEGER REFERENCES dashboards(id) ON DELETE CASCADE,
                    component_type VARCHAR(50) NOT NULL,
                    component_name VARCHAR(100),
                    custom_id VARCHAR(100),
                    position INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
                    config JSONB,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Now create component_layouts
            await self.db.execute("""
                CREATE TABLE IF NOT EXISTS component_layouts (
                    id SERIAL PRIMARY KEY,
                    component_id INTEGER REFERENCES dashboard_components(id) ON DELETE CASCADE,
                    row_position INTEGER DEFAULT 0,
                    col_position INTEGER DEFAULT 0,
                    width INTEGER DEFAULT 1,
                    height INTEGER DEFAULT 1,
                    style VARCHAR(50),
                    additional_props JSONB
                )
            """)
            
            self.logger.info("Dashboard tables created successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error ensuring dashboard tables exist: {e}")
            return False 