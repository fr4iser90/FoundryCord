"""Create dashboard definition and instance tables

Revision ID: 005
Revises: 004
Create Date: 2025-04-26 
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '005'
down_revision = '004' # Depends on guild_template_channels (003) and discord_guilds (002)
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'dashboard_component_definitions',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('dashboard_type', sa.String(length=100), nullable=False), 
        sa.Column('component_type', sa.String(length=50), nullable=False), 
        sa.Column('component_key', sa.String(length=100), nullable=False), 
        sa.Column('definition', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('dashboard_type', 'component_type', 'component_key', name='uq_component_definition')
    )
    op.create_index('idx_component_definition_lookup', 'dashboard_component_definitions', ['dashboard_type', 'component_type', 'component_key'])

    op.create_table(
        'dashboard_configurations',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('dashboard_type', sa.String(length=100), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('config', sa.JSON(), nullable=True), 
        sa.Column('description', sa.String(length=500), nullable=True), 
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('name', name='uq_dashboard_configurations_name')
    )
    op.create_index(op.f('ix_dashboard_configurations_name'), 'dashboard_configurations', ['name'], unique=True)

def downgrade() -> None:
    op.drop_index(op.f('ix_dashboard_configurations_name'), table_name='dashboard_configurations')
    op.drop_constraint('uq_dashboard_configurations_name', 'dashboard_configurations', type_='unique')
    op.drop_table('dashboard_configurations')

    op.drop_index('idx_component_definition_lookup', table_name='dashboard_component_definitions')
    op.drop_table('dashboard_component_definitions')