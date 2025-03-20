"""Create initial database tables

Revision ID: 001
Revises: 
Create Date: 2023-07-01 10:00:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '001'
down_revision = None  # Erste Migration hat keinen Vorgänger
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Create initial database tables."""
    # Haupt-Tabellen erstellen
    op.create_table(
        'category_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(length=1024), nullable=True),
        sa.Column('is_private', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Erstelle channel_templates Tabelle für 003_seed_channels.py
    op.create_table(
        'channel_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('topic', sa.String(length=1024), nullable=True),
        sa.Column('is_private', sa.Boolean(), nullable=True, default=False),
        sa.Column('category_name', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Erstelle dashboard_components Tabelle für 004_seed_dashboards.py
    op.create_table(
        'dashboard_components',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dashboard_id', sa.String(length=255), nullable=False),
        sa.Column('component_type', sa.String(length=255), nullable=False),
        sa.Column('component_name', sa.String(length=255), nullable=False),
        sa.Column('config', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Erstelle dashboards Tabelle 
    op.create_table(
        'dashboards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('channel_id', sa.String(length=255), nullable=True),
        sa.Column('type', sa.String(length=255), nullable=False),
        sa.Column('config', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    """Drop created tables."""
    # Tabellen in umgekehrter Reihenfolge löschen
    op.drop_table('dashboards')
    op.drop_table('dashboard_components')
    op.drop_table('channel_templates')
    op.drop_table('category_templates') 