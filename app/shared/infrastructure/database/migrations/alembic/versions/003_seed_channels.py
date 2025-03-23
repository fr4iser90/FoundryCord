"""Seed channels

Revision ID: 003
Revises: 002
Create Date: 2023-07-01 13:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

# Deine originalen Channel-Definitionen - direkt definiert
CHANNELS = [
    {
        "name": "welcome",
        "topic": "Welcome Information",
        "is_private": False,
        "category_name": "Homelab"
    },
    {
        "name": "services",
        "topic": "Service Overview",
        "is_private": True,
        "category_name": "Homelab"
    },
    {
        "name": "gamehub",
        "topic": "Gameserver Overview",
        "is_private": False,
        "category_name": "Homelab"
    },
    {
        "name": "infrastructure",
        "topic": "Infrastructure Management",
        "is_private": True,
        "category_name": "Homelab"
    },
    {
        "name": "projects",
        "topic": "Project Management",
        "is_private": True,
        "category_name": "Homelab"
    },
    {
        "name": "backups",
        "topic": "Backup Management",
        "is_private": True,
        "category_name": "Homelab"
    },
    {
        "name": "server-management",
        "topic": "Server Administration",
        "is_private": True,
        "category_name": "Homelab"
    },
    {
        "name": "logs",
        "topic": "System Logs",
        "is_private": True,
        "category_name": "Homelab"
    },
    {
        "name": "monitoring",
        "topic": "System Monitoring",
        "is_private": True,
        "category_name": "Homelab"
    },
    {
        "name": "bot-control",
        "topic": "Bot Management",
        "is_private": True,
        "category_name": "Homelab"
    },
    {
        "name": "alerts",
        "topic": "System Alerts",
        "is_private": True,
        "category_name": "Homelab"
    }
]

def upgrade() -> None:
    """Seed channels."""
    # Definiere Tabelle für SQL-Einfügung
    channels_table = table(
        'discord_channels',
        column('name', sa.String),
        column('topic', sa.String),
        column('is_private', sa.Boolean),
        column('category_name', sa.String)
    )
    
    # Füge Daten ein
    op.bulk_insert(channels_table, CHANNELS)

def downgrade() -> None:
    """Remove seeded channels."""
    for channel in CHANNELS:
        op.execute(f"DELETE FROM channels WHERE name = '{channel['name']}'") 