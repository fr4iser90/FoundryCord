"""Create discord guild tables

Revision ID: 002
Revises: 001
Create Date: 2025-04-26 
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'discord_guilds',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True), 
        sa.Column('guild_id', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('icon_url', sa.String(length=255), nullable=True),
        sa.Column('owner_id', sa.String(length=20), nullable=True),
        sa.Column('member_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('joined_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('access_status', sa.String(length=20), server_default='pending', nullable=False),
        sa.Column('access_requested_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('access_reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('access_reviewed_by', sa.String(length=32), nullable=True),
        sa.Column('access_notes', sa.Text(), nullable=True),
        sa.Column('enable_commands', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('enable_logging', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('enable_automod', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('enable_welcome', sa.Boolean(), server_default='false', nullable=False),
        sa.UniqueConstraint('guild_id')
    )
    # Remaining DISCORD Tables (Roles, Guild Users) - DEPEND ON discord_guilds and app_users/app_roles
    op.create_table(
        'discord_server_roles',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True), 
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('name')
    )
    op.create_table(
        'discord_guild_users',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True), 
        sa.Column('guild_id', sa.String(20), nullable=False), 
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('app_users.id'), nullable=False),
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('app_roles.id'), nullable=False), 
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('guild_id', 'user_id', name='uq_guild_user'),
        # Explicit FK to discord_guilds needed if not implicitly handled
        sa.ForeignKeyConstraint(['guild_id'], ['discord_guilds.guild_id'], name='fk_discord_guild_users_guild') 
    )

def downgrade() -> None:
    op.drop_table('discord_guild_users')
    op.drop_table('discord_server_roles')
    op.drop_table('discord_guilds')