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

async def main():
    """Main migration function for dashboard components"""
    # Stelle sicher, dass wir eine gültige Datenbankverbindung haben
    logger.info(f"Using database URL: {DATABASE_URL.replace(os.environ.get('APP_DB_PASSWORD', ''), '[HIDDEN]')}")
    
    # Ensure dashboard tables exist before trying to access them
    await ensure_dashboard_tables_exist()
    
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
    except Exception as e:
        logger.error(f"Dashboard components migration failed: {e}")
        raise

async def ensure_dashboard_tables_exist():
    """Ensure dashboard tables exist before trying to access them"""
    # Direkter Zugriff mit der neuen Methode
    session = await get_async_session()
    try:
        # First check and fix schema issues with component_layouts
        # This prevents the "column" reserved word error
        await fix_component_layouts_table(session)
        
        # Now proceed with normal checks and creations
        logger.info("Verifying dashboard tables exist...")
        
        # Explicitly check for each table with proper error handling
        tables_to_check = [
            ("dashboards", create_dashboards_table),
            ("dashboard_components", create_dashboard_components_table),
        ]
        
        for table_name, create_func in tables_to_check:
            try:
                # Check if the table exists
                result = await session.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = '{table_name}'
                    );
                """))
                exists = result.scalar()
                
                if not exists:
                    logger.info(f"Table {table_name} does not exist, creating it...")
                    await create_func(session)
                else:
                    logger.info(f"Table {table_name} already exists")
                    
                await session.commit()
            except Exception as e:
                logger.error(f"Error checking/creating table {table_name}: {e}")
                await session.rollback()
                raise
            
    except Exception as e:
        logger.error(f"Error ensuring dashboard tables exist: {e}")
        await session.rollback()
        raise
    finally:
        await session.close()

async def fix_component_layouts_table(session):
    """Check and fix component_layouts table if it exists with the 'column' issue"""
    try:
        # Check if the table exists
        result = await session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'component_layouts'
            );
        """))
        exists = result.scalar()
        
        if exists:
            # Drop the table to recreate it with the correct column names
            logger.info("Dropping component_layouts table to fix 'column' reserved word issue")
            await session.execute(text("DROP TABLE IF EXISTS component_layouts;"))
            await session.commit()
        
        # Create table with correct column names
        await session.execute(text("""
            CREATE TABLE IF NOT EXISTS component_layouts (
                id SERIAL PRIMARY KEY,
                component_id INTEGER REFERENCES dashboard_components(id) ON DELETE CASCADE,
                row_position INTEGER DEFAULT 0,
                col_position INTEGER DEFAULT 0,
                width INTEGER DEFAULT 1,
                height INTEGER DEFAULT 1,
                style VARCHAR(50),
                additional_props JSONB
            );
        """))
        await session.commit()
        logger.info("Component layouts table fixed successfully")
    except Exception as e:
        logger.error(f"Error fixing component_layouts table: {e}")
        await session.rollback()

async def create_dashboards_table(session):
    """Create the dashboards table"""
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
        );
        
        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_dashboards_dashboard_type 
        ON dashboards(dashboard_type);
        
        CREATE INDEX IF NOT EXISTS idx_dashboards_guild_id 
        ON dashboards(guild_id);
    """))
    await session.commit()
    logger.info("Dashboards table created successfully")

async def create_dashboard_components_table(session):
    """Create the dashboard_components table"""
    await session.execute(text("""
        CREATE TABLE IF NOT EXISTS dashboard_components (
            id SERIAL PRIMARY KEY,
            dashboard_id INTEGER REFERENCES dashboards(id) ON DELETE CASCADE,
            component_type VARCHAR(50) NOT NULL,
            component_name VARCHAR(100) NOT NULL,
            custom_id VARCHAR(100),
            position INTEGER DEFAULT 0,
            is_active BOOLEAN DEFAULT TRUE,
            config JSONB,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP DEFAULT NOW()
        );
        
        -- Create indexes
        CREATE INDEX IF NOT EXISTS idx_dashboard_components_dashboard_id
        ON dashboard_components(dashboard_id);
        
        CREATE INDEX IF NOT EXISTS idx_dashboard_components_type
        ON dashboard_components(component_type);
    """))
    await session.commit()
    logger.info("Dashboard components table created successfully")

# Split the migrate_dashboard function into separate functions for each dashboard type
async def migrate_welcome_dashboard(guild_id):
    """Migrate welcome dashboard"""
    logger.info("Migrating welcome dashboard")
    session = await get_async_session()
    try:
        await migrate_dashboard(
            session=session,
            dashboard_type="welcome",
            name="Welcome Dashboard",
            description="Welcome dashboard for new users",
            buttons=WELCOME_BUTTONS,
            embeds=WELCOME_EMBEDS,
            modals=WELCOME_MODALS,
            selectors=WELCOME_SELECTORS,
            views=WELCOME_VIEWS,
            guild_id=guild_id
        )
    finally:
        await session.close()

async def migrate_monitoring_dashboard(guild_id):
    """Migrate monitoring dashboard"""
    logger.info("Migrating monitoring dashboard")
    session = await get_async_session()
    try:
        await migrate_dashboard(
            session=session,
            dashboard_type="monitoring",
            name="Monitoring Dashboard",
            description="System monitoring dashboard",
            buttons=MONITORING_BUTTONS,
            embeds=MONITORING_EMBEDS,
            modals=MONITORING_MODALS,
            selectors=MONITORING_SELECTORS,
            views=MONITORING_VIEWS,
            guild_id=guild_id
        )
    finally:
        await session.close()

async def migrate_project_dashboard(guild_id):
    """Migrate project dashboard"""
    logger.info("Migrating project dashboard")
    session = await get_async_session()
    try:
        await migrate_dashboard(
            session=session,
            dashboard_type="project",
            name="Project Dashboard",
            description="Project management dashboard",
            buttons=PROJECT_BUTTONS,
            embeds=PROJECT_EMBEDS,
            modals=PROJECT_MODALS,
            selectors=PROJECT_SELECTORS,
            views=PROJECT_VIEWS,
            guild_id=guild_id
        )
    finally:
        await session.close()

async def migrate_gamehub_dashboard(guild_id):
    """Migrate gamehub dashboard"""
    logger.info("Migrating gamehub dashboard")
    session = await get_async_session()
    try:
        await migrate_dashboard(
            session=session,
            dashboard_type="gamehub",
            name="Game Hub Dashboard",
            description="Game server management dashboard",
            buttons=GAMEHUB_BUTTONS,
            embeds=GAMEHUB_EMBEDS,
            modals=GAMEHUB_MODALS,
            selectors=GAMEHUB_SELECTORS,
            views=GAMEHUB_VIEWS,
            guild_id=guild_id
        )
    finally:
        await session.close()

async def migrate_dashboard(session, dashboard_type, name, description, buttons, embeds, modals, selectors, views, guild_id=None):
    """Migrate a dashboard template to the database"""
    try:
        # Check if dashboard already exists
        result = await session.execute(text("""
            SELECT id FROM dashboards
            WHERE dashboard_type = :dashboard_type
            AND (guild_id = :guild_id OR (guild_id IS NULL AND :guild_id IS NULL))
        """), {
            "dashboard_type": dashboard_type,
            "guild_id": guild_id
        })
        
        dashboard_id = result.scalar()
        
        if dashboard_id:
            logger.info(f"{dashboard_type} dashboard already exists with ID {dashboard_id}, updating")
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
            logger.info(f"Created new {dashboard_type} dashboard with ID {dashboard_id}")
            
        await session.commit()
        
        # Migrate components
        if dashboard_id:
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
