"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2023-11-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create servers table
    op.create_table(
        'servers',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('icon_url', sa.Text(), nullable=True),
        sa.Column('joined_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create user_server association table
    op.create_table(
        'user_server',
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('server_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['server_id'], ['servers.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    
    # Create dashboards table
    op.create_table(
        'dashboards',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('dashboard_type', sa.String(length=50), nullable=False),
        sa.Column('layout', sa.Text(), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('server_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['server_id'], ['servers.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create dashboard_components table
    op.create_table(
        'dashboard_components',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('component_type', sa.String(length=50), nullable=False),
        sa.Column('config', sa.Text(), nullable=False),
        sa.Column('position_x', sa.Integer(), nullable=False),
        sa.Column('position_y', sa.Integer(), nullable=False),
        sa.Column('width', sa.Integer(), nullable=False),
        sa.Column('height', sa.Integer(), nullable=False),
        sa.Column('dashboard_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['dashboard_id'], ['dashboards.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create user_activities table
    op.create_table(
        'user_activities',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('activity_type', sa.String(length=50), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create user_settings table
    op.create_table(
        'user_settings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('theme', sa.String(length=20), nullable=False),
        sa.Column('refresh_rate', sa.Integer(), nullable=False),
        sa.Column('notifications_enabled', sa.Boolean(), nullable=False),
        sa.Column('notify_system_alerts', sa.Boolean(), nullable=False),
        sa.Column('notify_server_status', sa.Boolean(), nullable=False),
        sa.Column('notify_updates', sa.Boolean(), nullable=False),
        sa.Column('notification_method', sa.String(length=20), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create sessions table
    op.create_table(
        'sessions',
        sa.Column('id', sa.String(length=64), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('is_valid', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('sessions')
    op.drop_table('user_settings')
    op.drop_table('user_activities')
    op.drop_table('dashboard_components')
    op.drop_table('dashboards')
    op.drop_table('user_server')
    op.drop_table('servers')
    op.drop_table('users') 