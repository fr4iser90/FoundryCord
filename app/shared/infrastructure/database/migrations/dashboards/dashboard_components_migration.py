"""Script to migrate dashboard components from code to database"""
import asyncio
import sys
from pathlib import Path
import os
from app.shared.interface.logging.api import get_db_logger



logger = get_db_logger()
# Add project root to path to allow imports
project_root = Path(__file__).parents[6]
sys.path.insert(0, str(project_root))

from app.shared.infrastructure.database.models.config import get_async_session
from app.shared.infrastructure.database.repositories.dashboard_repository_impl import DashboardRepository

# Import dashboard components from definition files
from .welcome import WELCOME_BUTTONS, WELCOME_EMBEDS, WELCOME_MODALS, WELCOME_SELECTORS, WELCOME_VIEWS
from .monitoring import MONITORING_BUTTONS, MONITORING_EMBEDS, MONITORING_MODALS, MONITORING_SELECTORS, MONITORING_VIEWS
from .project import PROJECT_BUTTONS, PROJECT_EMBEDS, PROJECT_MODALS, PROJECT_SELECTORS, PROJECT_VIEWS
from .gamehub import GAMEHUB_BUTTONS, GAMEHUB_EMBEDS, GAMEHUB_MODALS, GAMEHUB_SELECTORS, GAMEHUB_VIEWS
from .common import DEFAULT_BUTTONS, DEFAULT_EMBEDS, DEFAULT_MODALS, DEFAULT_SELECTORS, DEFAULT_VIEWS

async def migrate_dashboard(dashboard_type, name, description, buttons, embeds, modals, selectors, views):
    """Migrate dashboard components to database"""
    logger.info(f"Migrating {dashboard_type} dashboard...")
    async_session = await get_async_session()
    try:
        repository = DashboardRepository(async_session)
        
        # Get Discord server ID from environment or use a placeholder
        discord_server_id = os.environ.get('DISCORD_SERVER', '12345')
        
        # Create or update dashboard
        dashboard = await repository.create_or_update_dashboard(
            dashboard_type=dashboard_type,
            title=name,
            description=description,
            guild_id=discord_server_id
        )
        
        # Buttons
        for button_id, button_data in buttons.items():
            # Create component
            component = await repository.create_component(
                dashboard_id=dashboard.id,
                component_type="button",
                component_name=button_id,
                custom_id=button_data.get("custom_id", button_id),
                position=button_data.get("position", 0),
                config=button_data
            )
            
            # Layout erstellen/aktualisieren
            await repository.create_or_update_layout(
                component_id=component.id,
                row=button_data.get("row", 0),
                column=button_data.get("column", 0),
                width=button_data.get("width", 1),
                height=button_data.get("height", 1)
            )
            
            # Template erstellen (if content exists in button_data)
            if "content" in button_data:
                for locale, content in button_data.get("content", {}).items():
                    await repository.create_template(
                        component_id=component.id,
                        template_type="button_content",
                        content=content.get("text", ""),
                        locale=locale,
                        title=content.get("title", ""),
                        variables=content.get("variables", {})
                    )
        
        # Migrate embeds
        for embed_name, embed_data in embeds.items():
            # Create component
            component = await repository.create_component(
                dashboard_id=dashboard.id,
                component_type="embed",
                component_name=embed_name,
                custom_id=f"{dashboard_type}_{embed_name}",
                position=embed_data.get("position", 0),
                config=embed_data
            )
            
            # Create layout if needed
            if "row" in embed_data or "column" in embed_data:
                await repository.create_or_update_layout(
                    component_id=component.id,
                    row=embed_data.get("row", 0),
                    column=embed_data.get("column", 0),
                    width=embed_data.get("width", 1),
                    height=embed_data.get("height", 1)
                )
            
            # Create templates if content exists
            if "content" in embed_data:
                for locale, content in embed_data.get("content", {}).items():
                    await repository.create_template(
                        component_id=component.id,
                        template_type="embed_content",
                        content=content.get("text", ""),
                        locale=locale,
                        title=content.get("title", ""),
                        variables=content.get("variables", {})
                    )
        
        # Migrate modals
        for modal_name, modal_data in modals.items():
            # Create component
            component = await repository.create_component(
                dashboard_id=dashboard.id,
                component_type="modal",
                component_name=modal_name,
                custom_id=f"{dashboard_type}_{modal_name}",
                position=modal_data.get("position", 0),
                config=modal_data
            )
            
            # Create templates if content exists
            if "content" in modal_data:
                for locale, content in modal_data.get("content", {}).items():
                    await repository.create_template(
                        component_id=component.id,
                        template_type="modal_content",
                        content=content.get("text", ""),
                        locale=locale,
                        title=content.get("title", ""),
                        variables=content.get("variables", {})
                    )
                    
        # Migrate selectors
        for selector_name, selector_data in selectors.items():
            # Create component
            component = await repository.create_component(
                dashboard_id=dashboard.id,
                component_type="selector",
                component_name=selector_name,
                custom_id=f"{dashboard_type}_{selector_name}",
                position=selector_data.get("position", 0),
                config=selector_data
            )
            
            # Create layout if needed
            if "row" in selector_data or "column" in selector_data:
                await repository.create_or_update_layout(
                    component_id=component.id,
                    row=selector_data.get("row", 0),
                    column=selector_data.get("column", 0),
                    width=selector_data.get("width", 1),
                    height=selector_data.get("height", 1)
                )
            
            # Create templates if content exists
            if "content" in selector_data:
                for locale, content in selector_data.get("content", {}).items():
                    await repository.create_template(
                        component_id=component.id,
                        template_type="selector_content",
                        content=content.get("text", ""),
                        locale=locale,
                        title=content.get("title", ""),
                        variables=content.get("variables", {})
                    )
            
        # Migrate views
        for view_name, view_data in views.items():
            # Create component
            component = await repository.create_component(
                dashboard_id=dashboard.id,
                component_type="view",
                component_name=view_name,
                custom_id=f"{dashboard_type}_{view_name}",
                position=view_data.get("position", 0),
                config=view_data
            )
            
            # Create layout if needed
            if "row" in view_data or "column" in view_data:
                await repository.create_or_update_layout(
                    component_id=component.id,
                    row=view_data.get("row", 0),
                    column=view_data.get("column", 0),
                    width=view_data.get("width", 1),
                    height=view_data.get("height", 1)
                )
            
            # Create templates if content exists
            if "content" in view_data:
                for locale, content in view_data.get("content", {}).items():
                    await repository.create_template(
                        component_id=component.id,
                        template_type="view_content",
                        content=content.get("text", ""),
                        locale=locale,
                        title=content.get("title", ""),
                        variables=content.get("variables", {})
                    )
        
        logger.info(f"Dashboard {dashboard_type} migrated successfully")
        
    except Exception as e:
        logger.error(f"Error migrating dashboard {dashboard_type}: {e}")
        raise
    finally:
        await async_session.close()

async def main():
    """Run all migrations"""
    
    await migrate_dashboard(
        dashboard_type="common",
        name="Common Dashboard",
        description="Common dashboard for the server",
        buttons=DEFAULT_BUTTONS,
        embeds=DEFAULT_EMBEDS,
        modals=DEFAULT_MODALS,
        selectors=DEFAULT_SELECTORS,
        views=DEFAULT_VIEWS
    )

    await migrate_dashboard(
        dashboard_type="welcome",
        name="Welcome Dashboard",
        description="Main welcome dashboard for the server",
        buttons=WELCOME_BUTTONS,
        embeds=WELCOME_EMBEDS,
        modals=WELCOME_MODALS,
        selectors=WELCOME_SELECTORS,
        views=WELCOME_VIEWS
    )
    
    await migrate_dashboard(
        dashboard_type="monitoring",
        name="System Monitoring",
        description="System status and monitoring dashboard",
        buttons=MONITORING_BUTTONS,
        embeds=MONITORING_EMBEDS,
        modals=MONITORING_MODALS,
        selectors=MONITORING_SELECTORS,
        views=MONITORING_VIEWS
    )
        
    await migrate_dashboard(
        dashboard_type="project",
        name="Project Dashboard",
        description="Project management dashboard",
        buttons=PROJECT_BUTTONS,
        embeds=PROJECT_EMBEDS,
        modals=PROJECT_MODALS,
        selectors=PROJECT_SELECTORS,
        views=PROJECT_VIEWS
    )
    
    await migrate_dashboard(
        dashboard_type="gamehub",
        name="GameHub Dashboard",
        description="Game server management dashboard",
        buttons=GAMEHUB_BUTTONS,
        embeds=GAMEHUB_EMBEDS,
        modals=GAMEHUB_MODALS,
        selectors=GAMEHUB_SELECTORS,
        views=GAMEHUB_VIEWS
    )
    


    logger.info("Dashboard component migration complete!")

if __name__ == "__main__":
    asyncio.run(main())
