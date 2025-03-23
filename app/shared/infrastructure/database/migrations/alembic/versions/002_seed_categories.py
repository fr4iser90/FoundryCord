"""Seed categories table

Revision ID: 002
Revises: 001
Create Date: 2023-07-01 12:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

# Deine originalen Homelab-Kategorien - direkt als Konstanten definiert
CATEGORIES = [
    {
        "name": "Homelab",
        "position": 0,
        "description": "Main category for homelab management",
        "is_private": True
    },
    {
        "name": "Homelab Game Servers",
        "position": 1,
        "description": "Category for game servers and related channels",
        "is_private": False
    }
]

def upgrade() -> None:
    """Seed initial categories."""
    # Definiere Tabelle für SQL-Einfügung
    categories_table = table(
        'discord_categories',
        column('name', sa.String),
        column('position', sa.Integer),
        column('description', sa.String),
        column('is_private', sa.Boolean)
    )
    
    # Füge Daten ein
    op.bulk_insert(categories_table, CATEGORIES)

def downgrade() -> None:
    """Remove seeded categories."""
    for category in CATEGORIES:
        op.execute(f"DELETE FROM categories WHERE name = '{category['name']}'") 