"""Dashboard database migration helper."""
from typing import Dict, Any, List, Optional
import asyncio

from app.shared.interface.logging.api import get_bot_logger
from app.shared.infrastructure.database.api import get_db

class DashboardMigration:
    """Handles dashboard table migrations and schema updates."""
    
    def __init__(self, bot):
        self.bot = bot
        self.logger = get_bot_logger()
        self.db = get_db()
        
    async def initialize(self):
        """Initialize the migration process with retry logic."""
        max_retries = 5
        retry_delay = 2  # seconds
        
        for attempt in range(1, max_retries + 1):
            try:
                # Test database connection first
                await self.test_connection()
                
                # Ensure database tables exist
                success = await self.ensure_dashboard_tables_exist()
                if success:
                    self.logger.info("Dashboard migration completed successfully")
                    return True
                else:
                    self.logger.error("Dashboard migration failed")
                    if attempt < max_retries:
                        self.logger.info(f"Retrying in {retry_delay} seconds (attempt {attempt}/{max_retries})")
                        await asyncio.sleep(retry_delay)
                    else:
                        return False
            except Exception as e:
                self.logger.error(f"Dashboard migration failed: {e}")
                if attempt < max_retries:
                    self.logger.info(f"Retrying in {retry_delay} seconds (attempt {attempt}/{max_retries})")
                    await asyncio.sleep(retry_delay)
                else:
                    return False
        
        return False
    
    async def test_connection(self):
        """Test database connection before proceeding."""
        try:
            # Simple query to test connection
            await self.db.execute("SELECT 1")
            self.logger.info("Database connection test successful")
            return True
        except Exception as e:
            self.logger.error(f"Database connection test failed: {e}")
            raise
            
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
                    title VARCHAR(100),
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
            
    async def create_welcome_dashboard(self):
        """Create a welcome dashboard if it doesn't exist."""
        try:
            # Check if welcome dashboard already exists
            query = "SELECT id FROM dashboards WHERE dashboard_type = 'welcome' LIMIT 1"
            result = await self.db.fetch(query)
            
            if result and len(result) > 0:
                self.logger.info("Welcome dashboard already exists")
                return False
                
            # Create welcome dashboard
            query = """
                INSERT INTO dashboards (
                    dashboard_type, name, description, is_active, config
                ) VALUES (
                    'welcome', 'Welcome Dashboard', 'Default welcome dashboard', 
                    TRUE, '{"layout": "standard", "theme": "light"}'
                ) RETURNING id
            """
            
            result = await self.db.fetch(query)
            if not result or len(result) == 0:
                self.logger.error("Failed to create welcome dashboard")
                return False
                
            dashboard_id = result[0]['id']
            self.logger.info(f"Created welcome dashboard with ID: {dashboard_id}")
            
            # Create some default components
            await self._create_welcome_components(dashboard_id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating welcome dashboard: {e}")
            return False
            
    async def _create_welcome_components(self, dashboard_id: int):
        """Create default components for the welcome dashboard."""
        try:
            # Create welcome message component
            query = """
                INSERT INTO dashboard_components (
                    dashboard_id, component_type, title, config
                ) VALUES (
                    $1, 'welcome_message', 'Welcome Message', 
                    '{"message": "Welcome to the server!", "show_icon": true}'
                ) RETURNING id
            """
            
            result = await self.db.fetch(query, dashboard_id)
            if result and len(result) > 0:
                component_id = result[0]['id']
                
                # Create layout for this component
                await self.db.execute("""
                    INSERT INTO component_layouts (
                        component_id, row_position, col_position, width, height
                    ) VALUES (
                        $1, 0, 0, 12, 1
                    )
                """, component_id)
            
            # Create server info component
            query = """
                INSERT INTO dashboard_components (
                    dashboard_id, component_type, title, config
                ) VALUES (
                    $1, 'server_info', 'Server Information', 
                    '{"show_member_count": true, "show_channels": true}'
                ) RETURNING id
            """
            
            result = await self.db.fetch(query, dashboard_id)
            if result and len(result) > 0:
                component_id = result[0]['id']
                
                # Create layout for this component
                await self.db.execute("""
                    INSERT INTO component_layouts (
                        component_id, row_position, col_position, width, height
                    ) VALUES (
                        $1, 1, 0, 6, 2
                    )
                """, component_id)
                
            self.logger.info(f"Created default components for dashboard {dashboard_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating welcome components: {e}")
            return False

    async def migrate_all_dashboards(self):
        """Migrate all old dashboards to the new system."""
        # For simplicity, we're just creating a welcome dashboard
        # and not migrating old ones
        result = await self.create_welcome_dashboard()
        return result is not None 