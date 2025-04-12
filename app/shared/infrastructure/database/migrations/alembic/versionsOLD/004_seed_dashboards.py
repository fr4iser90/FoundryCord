"""seed dashboard components

Revision ID: 004
Revises: 003
Create Date: 2024-03-19 15:18:38.804
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
import json
from sqlalchemy.sql import table, column

# Import die existierenden Dashboard-Definitionen
from app.shared.infrastructure.database.seeds.dashboard_instances.common import *
from app.shared.infrastructure.database.seeds.dashboard_instances.gamehub import *
from app.shared.infrastructure.database.seeds.dashboard_instances.monitoring import *
from app.shared.infrastructure.database.seeds.dashboard_instances.project import *
from app.shared.infrastructure.database.seeds.dashboard_instances.welcome import *

# Korrigierte Revision-IDs
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Seed dashboard components using existing definitions."""
    # Map to store dashboard types and their database IDs
    dashboard_id_map = {}
    
    # Vereinfachte Version, die nur ein Demo-Dashboard erstellt
    dashboard_instances = [
        {
            'name': 'Home Dashboard',
            'channel_id': '000000000000000000',  # Placeholder
            'type': 'welcome',
            'config': json.dumps({'auto_refresh': True, 'refresh_interval': 300})
        },
        {
            'name': 'Monitoring Dashboard',
            'channel_id': '000000000000000000',  # Placeholder
            'type': 'monitoring',
            'config': json.dumps({'auto_refresh': True, 'refresh_interval': 60})
        }
    ]
    
    # Simpler approach - insert dashboards one at a time and then query them
    for dashboard in dashboard_instances:
        # Insert the dashboard without trying to get RETURNING values
        op.execute(
            text("""
            INSERT INTO dashboard_instances (name, channel_id, type, config)
            VALUES (:name, :channel_id, :type, :config)
            """).bindparams(
                name=dashboard['name'],
                channel_id=dashboard['channel_id'],
                type=dashboard['type'],
                config=dashboard['config']
            )
        )
    
    # Now query the dashboard IDs separately
    for dashboard in dashboard_instances:
        conn = op.get_bind()
        result = conn.execute(
            text("""
            SELECT id FROM dashboard_instances WHERE type = :type
            """).bindparams(type=dashboard['type'])
        )
        dashboard_id = result.scalar()
        dashboard_id_map[dashboard['type']] = dashboard_id
    
    # Komponenten einfügen with correct IDs
    components = [
        {
            'dashboard_type': 'welcome',  # Changed from dashboard_id to dashboard_type
            'component_type': 'embed',
            'component_name': 'main_info',
            'config': json.dumps({
                'title': 'Willkommen im Homelab!',
                'description': 'Dein zentrales Portal für alle Homelab-Dienste.',
                'color': 3447003
            })
        },
        {
            'dashboard_type': 'monitoring',  # Changed from dashboard_id to dashboard_type
            'component_type': 'embed',
            'component_name': 'system_status',
            'config': json.dumps({
                'title': 'System Status',
                'description': 'Aktuelle Systemmetriken',
                'color': 5763719
            })
        }
    ]
    
    # Insert components using the actual integer IDs
    for component in components:
        # Get the actual integer ID for this dashboard type
        dashboard_id = dashboard_id_map[component['dashboard_type']]
        
        op.execute(
            text("""
            INSERT INTO dashboard_components (dashboard_id, component_type, component_name, config)
            VALUES (:dashboard_id, :component_type, :component_name, :config)
            """).bindparams(
                dashboard_id=dashboard_id,  # Now using the integer ID
                component_type=component['component_type'],
                component_name=component['component_name'],
                config=component['config']
            )
        )

def downgrade() -> None:
    """Remove seeded dashboard_instances."""
    op.execute("DELETE FROM dashboard_components")
    op.execute("DELETE FROM dashboard_instances") 