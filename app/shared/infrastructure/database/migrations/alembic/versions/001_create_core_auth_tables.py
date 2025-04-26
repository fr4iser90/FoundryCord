"""Create core auth tables

Revision ID: 001
Revises: 
Create Date: 2025-04-26 
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '001'
down_revision = None # First migration
branch_labels = None
depends_on = None

def upgrade() -> None:
    # CORE/SYSTEM Tables
    op.create_table(
        'security_keys',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False, unique=True),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False)
    )
    # App Tables - Users and Roles
    op.create_table(
        'app_roles',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True), 
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1024), nullable=True),
        sa.Column('permissions', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('name')
    )
    op.create_table(
        'app_users',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True), 
        sa.Column('username', sa.String(length=255), nullable=False),
        sa.Column('discord_id', sa.String(length=255), nullable=False),
        sa.Column('is_owner', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('avatar', sa.String(255), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('last_selected_guild_id', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('discord_id')
    )
    # Session Table
    op.create_table(
        'sessions',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True), 
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('app_users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token', sa.String(255), unique=True, nullable=False),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('user_agent', sa.String(255), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('device_info', sa.JSON(), nullable=True),
    )
    op.create_index('idx_sessions_token', 'sessions', ['token'])
    op.create_index('idx_sessions_user_id', 'sessions', ['user_id'])

def downgrade() -> None:
    op.drop_index('idx_sessions_user_id', table_name='sessions')
    op.drop_index('idx_sessions_token', table_name='sessions')
    op.drop_table('sessions')
    op.drop_table('app_users')
    op.drop_table('app_roles')
    op.drop_table('security_keys')