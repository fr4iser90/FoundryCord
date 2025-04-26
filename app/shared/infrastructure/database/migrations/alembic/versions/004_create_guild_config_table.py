"""Create guild config table

Revision ID: 004
Revises: 003
Create Date: 2025-04-26 
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '004'
down_revision = '003' # Depends on guild_templates (003) and discord_guilds (002)
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'guild_configs',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True), 
        sa.Column('guild_id', sa.String(20), sa.ForeignKey('discord_guilds.guild_id', name='fk_guild_config_guild', ondelete='CASCADE'), nullable=False),
        sa.Column('guild_name', sa.String(255), nullable=False),
        sa.Column('active_template_id', sa.Integer(), sa.ForeignKey('guild_templates.id', ondelete='SET NULL'), nullable=True), # Added here
        sa.Column('enable_dashboard', sa.Boolean(), nullable=False, server_default='false'), 
        sa.Column('enable_tasks', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('enable_services', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('settings', sa.String(), nullable=True),
        sa.UniqueConstraint('guild_id', name='uq_guild_config')
    )

def downgrade() -> None:
    op.drop_table('guild_configs')