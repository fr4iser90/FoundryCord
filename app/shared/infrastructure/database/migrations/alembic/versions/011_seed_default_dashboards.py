"""Seed default dashboard configurations into dashboard_templates

Revision ID: 011
Revises: 010
Create Date: YYYY-MM-DD HH:MM:SS.micros # Will be auto-filled by Alembic later

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


revision = '011'
down_revision = '010' 
branch_labels = None
depends_on = None


dashboard_configurations_table = table(
    'dashboard_configurations',
    column('name', sa.String),
    column('dashboard_type', sa.String),
    column('description', sa.String),
    column('config', sa.JSON) 
)

def upgrade() -> None:
    """Seed the dashboard_templates table with default configurations."""

    default_dashboards = [
        {
            'name': 'Default Welcome Dashboard',
            'dashboard_type': 'welcome',
            'description': 'Standard welcome message and rules display.',
            # Provide the dictionary directly
            'config': {
                "components": [
                    {
                        "instance_id": "welcome_main_embed_instance",
                        "component_key": "welcome_main_embed",
                        "settings": {}
                    },
                    {
                        "instance_id": "welcome_rules_button_instance",
                        "component_key": "welcome_rules_button",
                        "settings": {}
                    }
                ]
            }
        },
        {
            'name': 'Default Monitoring Dashboard',
            'dashboard_type': 'monitoring',
            'description': 'Basic system monitoring overview.',
            'config': {
                "components": [
                    {
                        "instance_id": "monitoring_embed_instance",
                        "component_key": "monitoring_system_info_embed",
                        "settings": {}
                    },
                    {
                        "instance_id": "monitoring_refresh_button_instance",
                        "component_key": "monitoring_refresh_button",
                        "settings": {}
                    }
                ]
            }
        },
        {
            'name': 'Default Project Dashboard',
            'dashboard_type': 'project',
            'description': 'Overview of projects and tasks.',
            'config': {
                "components": [
                     {
                        "instance_id": "project_list_embed_instance",
                        "component_key": "project_list_embed",
                        "settings": {}
                     },
                     {
                        "instance_id": "project_actions_view_instance",
                        "component_key": "project_main_view",
                        "settings": {}
                     }
                ]
            }
        },
         {
            'name': 'Default GameHub Dashboard',
            'dashboard_type': 'gamehub',
            'description': 'Game server information and actions.',
            'config': {
                "components": [
                     {
                        "instance_id": "gamehub_main_embed_instance",
                        "component_key": "gamehub_main_embed",
                        "settings": {}
                     },
                     {
                         "instance_id": "gamehub_actions_view_instance",
                         "component_key": "gamehub_main_view",
                         "settings": {}
                     }
                ]
            }
        }
    ]

    if default_dashboards:
        print(f"Inserting {len(default_dashboards)} default dashboard configurations...")
        op.bulk_insert(dashboard_configurations_table, default_dashboards)
    else:
        print("No default dashboard instances defined to seed.")


def downgrade() -> None:
    """Remove the seeded default dashboard instances."""
    default_names = [
        'Default Welcome Dashboard',
        'Default Monitoring Dashboard',
        'Default Project Dashboard',
        'Default GameHub Dashboard',
    ]

    default_names_sql_string = ", ".join([f"'{name}'" for name in default_names])

    if default_names_sql_string:
        print(f"Deleting default dashboard configurations: {', '.join(default_names)}")
        op.execute(f"DELETE FROM dashboard_configurations WHERE name IN ({default_names_sql_string})")
    else:
        print("No default dashboard names specified for deletion.")
