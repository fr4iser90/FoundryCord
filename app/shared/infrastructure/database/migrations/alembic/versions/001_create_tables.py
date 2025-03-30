"""Create initial database tables

Revision ID: 001
Revises: 
Create Date: 2023-07-01 10:00:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '001'
down_revision = None  # The first migration has no predecessor
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Create initial database tables."""
    
    # ==========================================================================
    # CORE/SYSTEM Tables
    # ==========================================================================
    op.create_table(
        'security_keys',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False, unique=True),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False)
    )
    
    # ==========================================================================
    # Discord Guild Configuration Table
    # ==========================================================================
    op.create_table(
        'guild_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('guild_id', sa.String(length=255), nullable=False, unique=True),
        sa.Column('guild_name', sa.String(length=255), nullable=False),
        sa.Column('enable_categories', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('enable_channels', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('enable_dashboard', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('enable_tasks', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('enable_services', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('settings', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), 
                  onupdate=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # ==========================================================================
    # App Tables - Users and Roles
    # ==========================================================================
    op.create_table(
        'app_roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1024), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    op.create_table(
        'app_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=False),
        sa.Column('discord_id', sa.String(length=255), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('discord_id'),
        sa.ForeignKeyConstraint(['role_id'], ['app_roles.id'])  # Foreign key referencing app_roles
    )
    
    # ==========================================================================
    # DISCORD Tables - Discord-specific Entities
    # ==========================================================================

    op.create_table(
        'discord_server_roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    op.create_table(
        'discord_guilds',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('guild_id', sa.String(20), unique=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('icon_url', sa.String(255), nullable=True),
        sa.Column('owner_id', sa.String(20), nullable=True),
        sa.Column('member_count', sa.Integer(), default=0),
        sa.Column('joined_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'discord_categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(length=1024), nullable=True),
        sa.Column('is_private', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Category mappings table (added to initial migration)
    op.create_table(
        'category_mappings',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('guild_id', sa.String(20), nullable=False),
        sa.Column('category_id', sa.String(20), nullable=False),
        sa.Column('category_name', sa.String(100), nullable=False),
        sa.Column('category_type', sa.String(50), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'),
        # Additional behavior flags
        sa.Column('delete_on_shutdown', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('create_on_startup', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('sync_permissions', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('guild_id', 'category_name', name='uq_guild_category_name')
    )
    
    # Create index for faster lookups
    op.create_index('idx_category_mappings_guild', 'category_mappings', ['guild_id'])
    op.create_index('idx_category_mappings_enabled', 'category_mappings', ['enabled'])
    
    op.create_table(
        'discord_channels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('discord_id', sa.BigInteger(), nullable=True, unique=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1024), nullable=True),
        sa.Column('topic', sa.String(length=1024), nullable=True),
        sa.Column('category_id', sa.Integer(), sa.ForeignKey("discord_categories.id"), nullable=True),
        sa.Column('category_discord_id', sa.BigInteger(), nullable=True),
        sa.Column('type', sa.String(length=50), nullable=False, server_default='TEXT'),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('permission_level', sa.String(length=50), nullable=False, server_default='PUBLIC'),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_created', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('nsfw', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('slowmode_delay', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('thread_config', sa.JSON(), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('category_name', sa.String(length=255), nullable=True),
        sa.Column('is_private', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    
    # Channel mappings table (added to initial migration)
    op.create_table(
        'channel_mappings',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('guild_id', sa.String(20), nullable=False),
        sa.Column('channel_id', sa.String(20), nullable=False),
        sa.Column('channel_name', sa.String(100), nullable=False),
        sa.Column('channel_type', sa.String(50), nullable=False),
        sa.Column('parent_channel_id', sa.String(20), nullable=True),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='true'),
        # Additional behavior flags
        sa.Column('delete_on_shutdown', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('create_on_startup', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('sync_permissions', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('guild_id', 'channel_name', name='uq_guild_channel_name')
    )
    
    # Create index for faster lookups
    op.create_index('idx_channel_mappings_guild', 'channel_mappings', ['guild_id'])
    op.create_index('idx_channel_mappings_enabled', 'channel_mappings', ['enabled'])
    
    op.create_table(
        'discord_guild_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('guild_id', sa.String(255), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('guild_id', 'user_id', name='uq_guild_user'),  # Unique constraint for guild and user
        sa.ForeignKeyConstraint(['user_id'], ['app_users.id']),  # Foreign key referencing app_users
        sa.ForeignKeyConstraint(['role_id'], ['app_roles.id'])  # Foreign key referencing app_roles
    )
    
    # Channel Permissions Table
    op.create_table(
        'discord_channel_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('channel_id', sa.Integer(), nullable=True),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('view', sa.Boolean(), nullable=False, default=False),
        sa.Column('send_messages', sa.Boolean(), nullable=False, default=False),
        sa.Column('manage_messages', sa.Boolean(), nullable=False, default=False),
        sa.Column('manage_channels', sa.Boolean(), nullable=False, default=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['channel_id'], ['discord_channels.id'], ondelete='CASCADE')  # Foreign key referencing discord_channels
    )
    
    # Category Permissions Table
    op.create_table(
        'discord_category_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('view', sa.Boolean(), nullable=False, default=False),
        sa.Column('send_messages', sa.Boolean(), nullable=False, default=False),
        sa.Column('manage_messages', sa.Boolean(), nullable=False, default=False),
        sa.Column('manage_channels', sa.Boolean(), nullable=False, default=False),
        sa.Column('manage_category', sa.Boolean(), nullable=False, default=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['category_id'], ['discord_categories.id'], ondelete='CASCADE')  # Foreign key referencing discord_categories
    )
    
    # Server Permissions Table
    op.create_table(
        'discord_server_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('guild_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('view', sa.Boolean(), nullable=False, default=False),
        sa.Column('send_messages', sa.Boolean(), nullable=False, default=False),
        sa.Column('manage_messages', sa.Boolean(), nullable=False, default=False),
        sa.Column('manage_channels', sa.Boolean(), nullable=False, default=False),
        sa.Column('manage_category', sa.Boolean(), nullable=False, default=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['guild_id'], ['discord_guilds.id'], ondelete='CASCADE')  # Foreign key referencing discord_guilds
    )
    
    # ==========================================================================
    # DASHBOARD Core Tables - UI and Dashboard Components
    # ==========================================================================
    op.create_table(
        'dashboard_instances',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('channel_id', sa.String(length=255), nullable=True),
        sa.Column('type', sa.String(length=255), nullable=False),
        sa.Column('config', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'dashboard_components',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dashboard_id', sa.Integer(), sa.ForeignKey('dashboard_instances.id'), nullable=False),  # Foreign key referencing dashboard_instances
        sa.Column('component_type', sa.String(length=255), nullable=False),
        sa.Column('component_name', sa.String(length=255), nullable=False),
        sa.Column('config', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
        
    # ==========================================================================
    # Specific Dashboard Tables - Project Management
    # ==========================================================================
    op.create_table(
        'dashboard_project_projects',
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
        sa.Index('idx_projects_guild_id', 'guild_id')  # Index for guild_id
    )
    
    op.create_table(
        'dashboard_project_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('dashboard_project_projects.id', ondelete='CASCADE'), nullable=False),  # Foreign key referencing dashboard_project_projects
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), server_default='todo', nullable=False),
        sa.Column('priority', sa.String(20), nullable=True),
        sa.Column('assigned_to', sa.String(20), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('task_data', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'dashboard_project_members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('dashboard_project_projects.id', ondelete='CASCADE'), nullable=False),  # Foreign key referencing dashboard_project_projects
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('app_users.id'), nullable=False),  # Foreign key referencing app_users
        sa.Column('joined_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id', 'user_id', name='uq_project_member')  # Unique constraint for project and user
    )

    # ==========================================================================
    # WebInterface Tables - UI and Dashboard Components
    # ==========================================================================
    op.create_table(
        'webinterface_widget_layouts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('app_users.id'), nullable=False),  # Foreign key referencing app_users
        sa.Column('guild_id', sa.String(20), nullable=True),
        sa.Column('page_id', sa.String(50), nullable=False),
        sa.Column('layout_data', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), 
                  onupdate=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'guild_id', 'page_id', name='uq_widget_layout')  # Unique constraint for user, guild, and page
    )

def downgrade() -> None:
    """Drop created tables in reverse order."""
    
    # PROJECT Tables
    op.drop_table('dashboard_project_members')
    op.drop_table('dashboard_project_tasks')
    op.drop_table('dashboard_project_projects')
    
    # DASHBOARD Tables
    op.drop_table('dashboard_components')
    op.drop_table('dashboard_instances')
    
    # WebInterface Tables
    op.drop_table('webinterface_widget_layouts')
    
    # DISCORD Tables
    op.drop_table('discord_server_permissions')
    op.drop_table('discord_category_permissions')
    op.drop_table('discord_channel_permissions')
    op.drop_table('discord_guild_users')
    op.drop_table('discord_channels')
    op.drop_table('discord_categories')
    op.drop_table('discord_guilds')
    op.drop_table('discord_server_roles')
    
    # AUTH Tables
    op.drop_table('app_users')
    op.drop_table('app_roles')
    
    # CORE Tables
    op.drop_table('security_keys')
    
    # Drop the guild_configs table
    op.drop_table('guild_configs')