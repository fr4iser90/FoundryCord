"""Script to migrate dashboard components from code to database"""
import asyncio
import sys
from pathlib import Path
import os
from app.shared.interface.logging.api import get_db_logger
from typing import Dict, Any, List, Optional
import json
from sqlalchemy import text
from contextlib import asynccontextmanager

logger = get_db_logger()
# Add project root to path to allow imports
project_root = Path(__file__).parents[6]
sys.path.insert(0, str(project_root))

# Importiere die direkte Verbindungskonfiguration
from app.shared.infrastructure.database.management.connection_config import (
    get_async_session, initialize_engine, DATABASE_URL
)
from app.shared.infrastructure.database.repositories.dashboard_repository_impl import DashboardRepository

# Import dashboard components from definition files
from .welcome import WELCOME_BUTTONS, WELCOME_EMBEDS, WELCOME_MODALS, WELCOME_SELECTORS, WELCOME_VIEWS
from .monitoring import MONITORING_BUTTONS, MONITORING_EMBEDS, MONITORING_MODALS, MONITORING_SELECTORS, MONITORING_VIEWS
from .project import PROJECT_BUTTONS, PROJECT_EMBEDS, PROJECT_MODALS, PROJECT_SELECTORS, PROJECT_VIEWS
from .gamehub import GAMEHUB_BUTTONS, GAMEHUB_EMBEDS, GAMEHUB_MODALS, GAMEHUB_SELECTORS, GAMEHUB_VIEWS
from .common import DEFAULT_BUTTONS, DEFAULT_EMBEDS, DEFAULT_MODALS, DEFAULT_SELECTORS, DEFAULT_VIEWS

# Global initialization state
_initialization_lock = asyncio.Lock()
_is_initialized = False
_initialization_complete = asyncio.Event()

@asynccontextmanager
async def get_migration_session():
    """Kontext-Manager für die Datenbanksitzung während der Migration."""
    session = await get_async_session()
    try:
        yield session
    finally:
        await session.close()

async def execute_migration_query(query, params=None):
    """Führt eine SQL-Abfrage aus und kümmert sich um Session-Management.
    
    Args:
        query: SQL-Abfrage als Text
        params: Parameter für die Abfrage (optional)
        
    Returns:
        Ergebnis der Abfrage
    """
    async with get_migration_session() as session:
        try:
            result = await session.execute(text(query), params or {})
            await session.commit()
            return result
        except Exception as e:
            await session.rollback()
            logger.error(f"Migration query error: {e}")
            raise

async def wait_for_database():
    """Wait for the database to be ready, with a proper connection test."""
    max_attempts = 30
    attempt = 0
    delay = 1.0  # Start with 1 second delay
    
    while attempt < max_attempts:
        try:
            engine = await initialize_engine()
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
                logger.info("Database is ready and accepting connections")
                return True
        except Exception as e:
            attempt += 1
            if attempt >= max_attempts:
                logger.error(f"Database connection failed after {max_attempts} attempts: {e}")
                return False
            
            # Exponential backoff with a cap
            delay = min(delay * 1.5, 5.0)
            logger.info(f"Waiting for database to be ready (attempt {attempt}/{max_attempts})... retrying in {delay:.1f}s")
            await asyncio.sleep(delay)
    
    return False

async def initialize_migration_system():
    """Initialize the migration system with proper coordination."""
    global _is_initialized
    
    # Only one initialization process can run at a time
    async with _initialization_lock:
        if _is_initialized:
            return True
        
        # Wait for database to be ready
        if not await wait_for_database():
            logger.error("Failed to establish database connection for migration")
            return False
        
        logger.info(f"Using database URL: {DATABASE_URL.replace(os.environ.get('APP_DB_PASSWORD', ''), '[HIDDEN]')}")
        
        try:
            # Ensure tables exist
            if not await ensure_dashboard_tables_exist():
                logger.error("Failed to create dashboard tables")
                return False
            
            # Mark initialization as complete
            _is_initialized = True
            _initialization_complete.set()
            return True
        except Exception as e:
            logger.error(f"Migration system initialization failed: {e}")
            return False

async def main():
    """Main migration function for dashboard components with proper orchestration"""
    # Initialize the migration system first
    if not await initialize_migration_system():
        logger.error("Migration system initialization failed")
        return False
    
    # Continue with existing migration logic
    try:
        # Get Discord server ID from environment or use a placeholder
        discord_server_id = os.environ.get('DISCORD_SERVER', '151414244603068426')
        
        # Migrate dashboards (in fixed order to avoid dependency issues)
        await migrate_welcome_dashboard(discord_server_id)
        await migrate_monitoring_dashboard(discord_server_id)
        await migrate_project_dashboard(discord_server_id)
        await migrate_gamehub_dashboard(discord_server_id)
        
        logger.info("Dashboard components migration completed successfully")
        return True
    except Exception as e:
        logger.error(f"Dashboard components migration failed: {e}")
        return False

async def wait_for_initialization():
    """Wait for the migration system to be initialized."""
    if not _is_initialized:
        logger.info("Waiting for dashboard migration system to initialize...")
        await _initialization_complete.wait()
    return _is_initialized

async def ensure_dashboard_tables_exist():
    """Ensure all dashboard-related tables exist in the database."""
    logger.info("Verifying dashboard tables exist...")
    
    async with get_migration_session() as session:
        try:
            # Check if dashboards table exists
            result = await session.execute(text("SELECT to_regclass('public.dashboards')"))
            if result.scalar() is None:
                logger.info("Table dashboards does not exist, creating it...")
                await create_dashboards_table(session)
            
            # Check if dashboard_components table exists
            result = await session.execute(text("SELECT to_regclass('public.dashboard_components')"))
            if result.scalar() is None:
                logger.info("Table dashboard_components does not exist, creating it...")
                await create_dashboard_components_table(session)
            
            # Check if component_layouts table exists
            result = await session.execute(text("SELECT to_regclass('public.component_layouts')"))
            if result.scalar() is None:
                logger.info("Table component_layouts does not exist, creating it...")
                await create_component_layouts_table(session)
            
            await session.commit()
            logger.info("Dashboard tables created successfully")
            return True
        except Exception as e:
            await session.rollback()
            logger.error(f"Error ensuring dashboard tables exist: {e}")
            return False

async def create_dashboards_table(session):
    """Create dashboards table with separate statements to avoid the multi-statement error."""
    # Create table first
    await session.execute(text("""
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
    """))
    
    # Create index for dashboard_type in a separate statement
    await session.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_dashboards_dashboard_type 
        ON dashboards(dashboard_type)
    """))
    
    # Create index for guild_id in a separate statement
    await session.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_dashboards_guild_id 
        ON dashboards(guild_id)
    """))

async def create_dashboard_components_table(session):
    """Create dashboard_components table with separate statements."""
    # Create table first
    await session.execute(text("""
        CREATE TABLE IF NOT EXISTS dashboard_components (
            id SERIAL PRIMARY KEY,
            dashboard_id INTEGER REFERENCES dashboards(id) ON DELETE CASCADE,
            component_type VARCHAR(50) NOT NULL,
            component_name VARCHAR(100) NOT NULL,
            custom_id VARCHAR(100),
            position INTEGER DEFAULT 0,
            config JSONB,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """))
    
    # Create indexes in separate statements
    await session.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_components_dashboard_id 
        ON dashboard_components(dashboard_id)
    """))
    
    await session.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_components_component_type 
        ON dashboard_components(component_type)
    """))
    
    await session.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_components_custom_id 
        ON dashboard_components(custom_id)
    """))

async def create_component_layouts_table(session):
    """Create component_layouts table with separate statements."""
    # Create table first
    await session.execute(text("""
        CREATE TABLE IF NOT EXISTS component_layouts (
            id SERIAL PRIMARY KEY,
            dashboard_id INTEGER REFERENCES dashboards(id) ON DELETE CASCADE,
            layout_name VARCHAR(100) NOT NULL,
            layout_data JSONB,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        )
    """))
    
    # Create indexes in separate statements
    await session.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_layouts_dashboard_id 
        ON component_layouts(dashboard_id)
    """))

async def migrate_welcome_dashboard(discord_server_id):
    """Migrate welcome dashboard components to database"""
    await migrate_dashboard_components(
        dashboard_type="welcome",
        name="Welcome Dashboard",
        description="Dashboard for server welcome and onboarding",
        guild_id=discord_server_id,
        buttons=WELCOME_BUTTONS,
        embeds=WELCOME_EMBEDS,
        modals=WELCOME_MODALS,
        selectors=WELCOME_SELECTORS,
        views=WELCOME_VIEWS
    )

async def migrate_monitoring_dashboard(discord_server_id):
    """Migrate monitoring dashboard components to database"""
    await migrate_dashboard_components(
        dashboard_type="monitoring",
        name="System Monitoring Dashboard",
        description="Dashboard for system monitoring and status",
        guild_id=discord_server_id,
        buttons=MONITORING_BUTTONS,
        embeds=MONITORING_EMBEDS,
        modals=MONITORING_MODALS,
        selectors=MONITORING_SELECTORS,
        views=MONITORING_VIEWS
    )

async def migrate_project_dashboard(discord_server_id):
    """Migrate project dashboard components to database"""
    await migrate_dashboard_components(
        dashboard_type="project",
        name="Project Management Dashboard",
        description="Dashboard for project management and tracking",
        guild_id=discord_server_id,
        buttons=PROJECT_BUTTONS,
        embeds=PROJECT_EMBEDS,
        modals=PROJECT_MODALS,
        selectors=PROJECT_SELECTORS,
        views=PROJECT_VIEWS
    )

async def migrate_gamehub_dashboard(discord_server_id):
    """Migrate gamehub dashboard components to database"""
    await migrate_dashboard_components(
        dashboard_type="gamehub",
        name="Game Server Hub",
        description="Dashboard for game server management",
        guild_id=discord_server_id,
        buttons=GAMEHUB_BUTTONS,
        embeds=GAMEHUB_EMBEDS,
        modals=GAMEHUB_MODALS,
        selectors=GAMEHUB_SELECTORS,
        views=GAMEHUB_VIEWS
    )

async def migrate_dashboard_components(dashboard_type, name, description, guild_id, buttons=None, embeds=None, modals=None, selectors=None, views=None):
    """Migrate all components for a specific dashboard type"""
    async with get_migration_session() as session:
        try:
            # Check if dashboard already exists
            result = await session.execute(text("""
                SELECT id FROM dashboards
                WHERE dashboard_type = :dashboard_type AND guild_id = :guild_id
            """), {
                "dashboard_type": dashboard_type,
                "guild_id": guild_id
            })
            
            dashboard_id = result.scalar()
            
            if dashboard_id:
                # Update existing dashboard
                await session.execute(text("""
                    UPDATE dashboards
                    SET name = :name, 
                        description = :description,
                        is_active = TRUE,
                        updated_at = NOW()
                    WHERE id = :id
                """), {
                    "name": name,
                    "description": description,
                    "id": dashboard_id
                })
                logger.info(f"Updated existing dashboard: {name} (ID: {dashboard_id})")
            else:
                # Create new dashboard
                result = await session.execute(text("""
                    INSERT INTO dashboards
                    (dashboard_type, name, description, guild_id, is_active)
                    VALUES (:dashboard_type, :name, :description, :guild_id, TRUE)
                    RETURNING id
                """), {
                    "dashboard_type": dashboard_type,
                    "name": name,
                    "description": description,
                    "guild_id": guild_id
                })
                dashboard_id = result.scalar()
                logger.info(f"Created new dashboard: {name} (ID: {dashboard_id})")
            
            # Commit the dashboard creation/update before proceeding with components
            await session.commit()
            
            # Migrate all component types
            if buttons:
                await migrate_components(session, dashboard_id, "button", buttons)
            
            if embeds:
                await migrate_components(session, dashboard_id, "embed", embeds)
                
            if modals:
                await migrate_components(session, dashboard_id, "modal", modals)
                
            if selectors:
                await migrate_components(session, dashboard_id, "selector", selectors)
                
            if views:
                await migrate_components(session, dashboard_id, "view", views)
        except Exception as e:
            await session.rollback()
            logger.error(f"Error migrating dashboard {dashboard_type}: {e}")
            raise

async def migrate_components(session, dashboard_id, component_type, components_dict):
    """Migrate components of a specific type to the database"""
    if not components_dict:
        return
        
    position = 0
    success_count = 0
    error_count = 0
    
    for component_name, component_data in components_dict.items():
        try:
            # Check if component already exists
            result = await session.execute(text("""
                SELECT id FROM dashboard_components
                WHERE dashboard_id = :dashboard_id 
                AND component_type = :component_type
                AND component_name = :component_name
            """), {
                "dashboard_id": dashboard_id,
                "component_type": component_type,
                "component_name": component_name
            })
            
            component_id = result.scalar()
            
            if component_id:
                # Update existing component
                await session.execute(text("""
                    UPDATE dashboard_components
                    SET config = :config,
                        position = :position,
                        is_active = TRUE,
                        updated_at = NOW()
                    WHERE id = :id
                """), {
                    "config": json.dumps(component_data),
                    "position": position,
                    "id": component_id
                })
                success_count += 1
            else:
                # Create new component
                await session.execute(text("""
                    INSERT INTO dashboard_components
                    (dashboard_id, component_type, component_name, custom_id, position, config)
                    VALUES (:dashboard_id, :component_type, :component_name, :custom_id, :position, :config)
                """), {
                    "dashboard_id": dashboard_id,
                    "component_type": component_type,
                    "component_name": component_name,
                    "custom_id": f"{component_type}_{component_name}",
                    "position": position,
                    "config": json.dumps(component_data)
                })
                success_count += 1
            
            # Commit after each component to avoid transaction timeouts
            await session.commit()
            position += 1
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Error migrating {component_type} component {component_name}: {e}")
            error_count += 1
            continue  # Continue with other components even if one fails
    
    logger.info(f"Migrated {success_count} {component_type} components (errors: {error_count})")

# Helper function to run the migration from command line
def run_migration():
    """Run the migration as a standalone script"""
    asyncio.run(main())

if __name__ == "__main__":
    run_migration()
