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
            'config': {
                "components": [
                    {
                        "instance_id": "welcome_main_embed_instance",
                        "component_key": "welcome_main_embed",
                        "settings": {}
                    },
                    {
                        "instance_id": "welcome_rules_button_instance",
                        "component_key": "accept_rules_button",
                        "settings": {}
                    },
                    {
                        "instance_id": "welcome_server_info_button_instance",
                        "component_key": "server_info_button",
                        "settings": {}
                    },
                    {
                        "instance_id": "welcome_bot_info_button_instance",
                        "component_key": "bot_info_button",
                        "settings": {}
                    },
                    {
                        "instance_id": "welcome_tech_selector_instance",
                        "component_key": "tech_selector",
                        "settings": {}
                    }
                ],
                "interactive_components": [
                    "welcome_rules_button_instance",
                    "welcome_server_info_button_instance",
                    "welcome_bot_info_button_instance",
                    "welcome_tech_selector_instance"
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
                        "component_key": "system_status_embed",
                        "settings": {}
                    },
                    {
                        "instance_id": "monitoring_system_details_button",
                        "component_key": "system_details_button",
                        "settings": {}
                    },
                    {
                        "instance_id": "monitoring_cpu_details_button",
                        "component_key": "cpu_details_button",
                        "settings": {}
                    },
                    {
                        "instance_id": "monitoring_memory_details_button",
                        "component_key": "memory_details_button",
                        "settings": {}
                    },
                    {
                        "instance_id": "monitoring_disk_details_button",
                        "component_key": "disk_details_button",
                        "settings": {}
                    },
                    {
                        "instance_id": "monitoring_network_details_button",
                        "component_key": "network_details_button",
                        "settings": {}
                    },
                    {
                        "instance_id": "monitoring_processes_button",
                        "component_key": "processes_button",
                        "settings": {}
                    },
                    {
                        "instance_id": "monitoring_docker_services_button",
                        "component_key": "docker_services_button",
                        "settings": {}
                    },
                    {
                        "instance_id": "monitoring_game_servers_button",
                        "component_key": "game_servers_button",
                        "settings": {}
                    },
                    {
                        "instance_id": "monitoring_view_logs_button",
                        "component_key": "view_logs_button",
                        "settings": {}
                    },
                    {
                        "instance_id": "monitoring_refresh_button",
                        "component_key": "refresh_button",
                        "settings": {}
                    }
                ],
                "interactive_components": [
                    "monitoring_system_details_button",
                    "monitoring_cpu_details_button",
                    "monitoring_memory_details_button",
                    "monitoring_disk_details_button",
                    "monitoring_network_details_button",
                    "monitoring_processes_button",
                    "monitoring_docker_services_button",
                    "monitoring_game_servers_button",
                    "monitoring_view_logs_button",
                    "monitoring_refresh_button"
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
                         "instance_id": "project_create_project_button",
                         "component_key": "create_project_button",
                         "settings": {}
                     },
                     {
                         "instance_id": "project_view_projects_button",
                         "component_key": "view_projects_button",
                         "settings": {}
                     },
                     {
                         "instance_id": "project_my_projects_button",
                         "component_key": "my_projects_button",
                         "settings": {}
                     },
                     {
                         "instance_id": "project_active_projects_button",
                         "component_key": "active_projects_button",
                         "settings": {}
                     },
                     {
                         "instance_id": "project_completed_projects_button",
                         "component_key": "completed_projects_button",
                         "settings": {}
                     },
                     {
                         "instance_id": "project_refresh_projects_button",
                         "component_key": "refresh_projects_button",
                         "settings": {}
                     },
                     {
                         "instance_id": "project_filter_selector_instance",
                         "component_key": "project_filter_selector",
                         "settings": {}
                     },
                     {
                         "instance_id": "project_sort_selector_instance",
                         "component_key": "project_sort_selector",
                         "settings": {}
                     }
                ],
                "interactive_components": [
                     "project_create_project_button",
                     "project_view_projects_button",
                     "project_my_projects_button",
                     "project_active_projects_button",
                     "project_completed_projects_button",
                     "project_refresh_projects_button",
                     "project_filter_selector_instance",
                     "project_sort_selector_instance"
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
                         "instance_id": "gamehub_minecraft_button",
                         "component_key": "minecraft_server_button",
                         "settings": {}
                     },
                     {
                         "instance_id": "gamehub_factorio_button",
                         "component_key": "factorio_server_button",
                         "settings": {}
                     },
                     {
                         "instance_id": "gamehub_valheim_button",
                         "component_key": "valheim_server_button",
                         "settings": {}
                     },
                     {
                         "instance_id": "gamehub_terraria_button",
                         "component_key": "terraria_server_button",
                         "settings": {}
                     },
                     {
                         "instance_id": "gamehub_satisfactory_button",
                         "component_key": "satisfactory_server_button",
                         "settings": {}
                     },
                     {
                         "instance_id": "gamehub_ark_button",
                         "component_key": "ark_server_button",
                         "settings": {}
                     },
                     {
                         "instance_id": "gamehub_refresh_button",
                         "component_key": "refresh_servers_button",
                         "settings": {}
                     },
                     {
                         "instance_id": "gamehub_add_server_button",
                         "component_key": "add_server_button",
                         "settings": {}
                     },
                     {
                         "instance_id": "gamehub_filter_selector",
                         "component_key": "server_filter_selector",
                         "settings": {}
                     }
                ],
                "interactive_components": [
                     "gamehub_minecraft_button",
                     "gamehub_factorio_button",
                     "gamehub_valheim_button",
                     "gamehub_terraria_button",
                     "gamehub_satisfactory_button",
                     "gamehub_ark_button",
                     "gamehub_refresh_button",
                     "gamehub_add_server_button",
                     "gamehub_filter_selector"
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
