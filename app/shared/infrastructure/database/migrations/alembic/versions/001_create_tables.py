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

    op.create_table(
        'security_keys',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False, unique=True),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False)
    )
    
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(length=1024), nullable=True),
        sa.Column('is_private', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Erstelle channels Tabelle für 003_seed_channels.py
    op.create_table(
        'channels',
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

    # Create Bot-Roles table
    op.create_table(
        'app_roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1024), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create Discord-Roles table
    op.create_table(
        'discord_server_roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=False),
        sa.Column('discord_id', sa.String(length=255), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('discord_id'),
        sa.ForeignKeyConstraint(['role_id'], ['app_roles.id'])
    )

    op.create_table(
        'guild_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('guild_id', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['role_id'], ['app_roles.id']),
        sa.UniqueConstraint('guild_id', 'user_id')  # Ein Benutzer hat nur eine Rolle pro Gilde
    )
    
    # Erstelle guilds Tabelle
    op.create_table(
        'guilds',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('guild_id', sa.String(20), nullable=False, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('icon_url', sa.String(255), nullable=True),
        sa.Column('owner_id', sa.String(20), nullable=True),
        sa.Column('member_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('joined_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Erstelle channel_permissions Tabelle
    op.create_table(
        'channel_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('channel_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.BigInteger(), nullable=False),
        sa.Column('view', sa.Boolean(), nullable=False, default=False),
        sa.Column('send_messages', sa.Boolean(), nullable=False, default=False),
        sa.Column('read_messages', sa.Boolean(), nullable=False, default=False),
        sa.Column('manage_messages', sa.Boolean(), nullable=False, default=False),
        sa.Column('manage_channel', sa.Boolean(), nullable=False, default=False),
        sa.Column('use_bots', sa.Boolean(), nullable=False, default=False),
        sa.Column('embed_links', sa.Boolean(), nullable=False, default=False),
        sa.Column('attach_files', sa.Boolean(), nullable=False, default=False),
        sa.Column('add_reactions', sa.Boolean(), nullable=False, default=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], ondelete='CASCADE')
    )
    
    # Erstelle category_permissions Tabelle
    op.create_table(
        'category_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('view', sa.Boolean(), nullable=False, default=False),
        sa.Column('send_messages', sa.Boolean(), nullable=False, default=False),
        sa.Column('manage_messages', sa.Boolean(), nullable=False, default=False),
        sa.Column('manage_channels', sa.Boolean(), nullable=False, default=False),
        sa.Column('manage_category', sa.Boolean(), nullable=False, default=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE')
    )

    # Korrektur für server_permissions
    op.create_table(
        'server_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('guild_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('view', sa.Boolean(), nullable=False, default=False),
        sa.Column('send_messages', sa.Boolean(), nullable=False, default=False),
        sa.Column('manage_messages', sa.Boolean(), nullable=False, default=False),
        sa.Column('manage_channels', sa.Boolean(), nullable=False, default=False),
        sa.Column('manage_category', sa.Boolean(), nullable=False, default=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['guild_id'], ['guilds.id'], ondelete='CASCADE')  # Korrigiert von category_id
    )

    # Projekte Tabelle
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('guild_id', sa.String(20), nullable=False),
        sa.Column('owner_id', sa.String(20), nullable=False),
        sa.Column('status', sa.String(50), server_default='active', nullable=False),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('project_data', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('idx_projects_guild_id', 'guild_id')
    )
    
    # Tasks Tabelle
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), server_default='todo', nullable=False),
        sa.Column('priority', sa.String(20), nullable=True),
        sa.Column('assigned_to', sa.String(20), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('task_data', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE')
    )
    
    # Projekt-Mitglieder Tabelle
    op.create_table(
        'project_members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('joined_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('project_id', 'user_id', name='uq_project_member')
    )

def downgrade() -> None:
    """Drop created tables in reverse order."""
    op.drop_table('project_members')
    op.drop_table('tasks')
    op.drop_table('projects')
    op.drop_table('server_permissions')
    op.drop_table('category_permissions')
    op.drop_table('channel_permissions')
    op.drop_table('guild_users')
    op.drop_table('users')
    op.drop_table('app_roles')
    op.drop_table('discord_server_roles')
    op.drop_table('guilds')
    op.drop_table('dashboards')
    op.drop_table('dashboard_components')
    op.drop_table('channels')
    op.drop_table('categories')
    op.drop_table('security_keys')
