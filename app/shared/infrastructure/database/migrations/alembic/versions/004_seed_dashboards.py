"""seed dashboard components

Revision ID: 004
Revises: 003
Create Date: 2024-03-19 15:18:38.804
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
import json

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
    
    # Dashboards einfügen
    for dashboard in dashboard_instances:
        # SQLAlchemy-Textvorlage mit bindparams verwenden
        query = text("""
        INSERT INTO dashboard_instances (name, channel_id, type, config)
        VALUES (:name, :channel_id, :type, :config)
        """).bindparams(
            name=dashboard['name'],
            channel_id=dashboard['channel_id'],
            type=dashboard['type'],
            config=dashboard['config']
        )
        op.execute(query)
    
    # Komponenten einfügen
    components = [
        {
            'dashboard_id': 'welcome',
            'component_type': 'embed',
            'component_name': 'main_info',
            'config': json.dumps({
                'title': 'Willkommen im Homelab!',
                'description': 'Dein zentrales Portal für alle Homelab-Dienste.',
                'color': 3447003
            })
        },
        {
            'dashboard_id': 'monitoring',
            'component_type': 'embed',
            'component_name': 'system_status',
            'config': json.dumps({
                'title': 'System Status',
                'description': 'Aktuelle Systemmetriken',
                'color': 5763719
            })
        }
    ]
    
    # Komponenten einfügen
    for component in components:
        query = text("""
        INSERT INTO dashboard_components (dashboard_id, component_type, component_name, config)
        VALUES (:dashboard_id, :component_type, :component_name, :config)
        """).bindparams(
            dashboard_id=component['dashboard_id'],
            component_type=component['component_type'],
            component_name=component['component_name'],
            config=component['config']
        )
        op.execute(query)

def downgrade() -> None:
    """Remove seeded dashboard_instances."""
    op.execute("DELETE FROM dashboard_components")
    op.execute("DELETE FROM dashboard_instances") 