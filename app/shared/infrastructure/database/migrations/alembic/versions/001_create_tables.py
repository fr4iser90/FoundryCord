"""Create initial database tables

Revision ID: 001
Revises: 
Create Date: 2025-04-12

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '001'
down_revision = None  # The first migration has no predecessor
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Create the initial database tables with the template-focused structure."""

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
    # DISCORD Guild Table
    # ==========================================================================
    op.create_table(
        'discord_guilds',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True), # Added primary key
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
        # sa.PrimaryKeyConstraint('id'), # Defined above
        sa.UniqueConstraint('guild_id')
    )

    # ==========================================================================
    # Discord Guild Configuration Table
    # ==========================================================================
    op.create_table(
        'guild_configs',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True), # Added primary key
        sa.Column('guild_id', sa.String(20), sa.ForeignKey('discord_guilds.guild_id', name='fk_guild_config_guild', ondelete='CASCADE'), nullable=False),
        sa.Column('guild_name', sa.String(255), nullable=False),
        # Removed obsolete enable flags if structure comes from template
        # sa.Column('enable_categories', sa.Boolean(), nullable=False, server_default='true'),
        # sa.Column('enable_channels', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('enable_dashboard', sa.Boolean(), nullable=False, server_default='false'), # Keep this for dashboard activation
        sa.Column('enable_tasks', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('enable_services', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('settings', sa.String(), nullable=True),
        # sa.PrimaryKeyConstraint('id'), # Defined above
        sa.UniqueConstraint('guild_id', name='uq_guild_config')
        # sa.ForeignKeyConstraint(['guild_id'], ['discord_guilds.guild_id'], name='fk_guild_config_guild', ondelete='CASCADE') # Defined above
    )

    # ==========================================================================
    # App Tables - Users and Roles
    # ==========================================================================
    op.create_table(
        'app_roles',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True), # Added primary key
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=1024), nullable=True),
        sa.Column('permissions', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        # sa.PrimaryKeyConstraint('id'), # Defined above
        sa.UniqueConstraint('name')
    )

    op.create_table(
        'app_users',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True), # Added primary key
        sa.Column('username', sa.String(length=255), nullable=False),
        sa.Column('discord_id', sa.String(length=255), nullable=False),
        sa.Column('is_owner', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('avatar', sa.String(255), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        # sa.PrimaryKeyConstraint('id'), # Defined above
        sa.UniqueConstraint('discord_id')
    )

    # ==========================================================================
    # Session Table
    # ==========================================================================
    op.create_table(
        'sessions',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True), # Added primary key
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('app_users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token', sa.String(255), unique=True, nullable=False),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('user_agent', sa.String(255), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('device_info', sa.JSON(), nullable=True),
        # sa.PrimaryKeyConstraint('id') # Defined above
    )
    op.create_index('idx_sessions_token', 'sessions', ['token'])
    op.create_index('idx_sessions_user_id', 'sessions', ['user_id'])

    # ==========================================================================
    # GUILD TEMPLATE Tables - Server-specific Structure Snapshots
    # ==========================================================================
    op.create_table(
        'guild_templates',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('guild_id', sa.String(20), sa.ForeignKey('discord_guilds.guild_id', ondelete='SET NULL'), nullable=True),
        sa.Column('template_name', sa.String(length=255), nullable=False),
        sa.Column('template_description', sa.Text, nullable=True),
        sa.Column('creator_user_id', sa.Integer(), sa.ForeignKey('app_users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('is_shared', sa.Boolean(), server_default='false', nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False)
    )
    op.create_index('idx_guild_templates_guild_id', 'guild_templates', ['guild_id'])
    op.create_index('idx_guild_templates_creator_user_id', 'guild_templates', ['creator_user_id'])

    op.create_table(
        'guild_template_categories',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('guild_template_id', sa.Integer(), sa.ForeignKey('guild_templates.id', ondelete='CASCADE'), nullable=False),
        sa.Column('category_name', sa.String(length=100), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('metadata_json', sa.JSON(), nullable=True)
    )
    op.create_index('idx_guild_template_categories_template_id', 'guild_template_categories', ['guild_template_id'])

    op.create_table(
        'guild_template_channels',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('guild_template_id', sa.Integer(), sa.ForeignKey('guild_templates.id', ondelete='CASCADE'), nullable=False),
        sa.Column('channel_name', sa.String(length=100), nullable=False),
        sa.Column('channel_type', sa.String(length=50), nullable=False), # e.g., 'GUILD_TEXT', 'GUILD_VOICE'
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('topic', sa.Text(), nullable=True),
        sa.Column('is_nsfw', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('slowmode_delay', sa.Integer(), server_default='0', nullable=False),
        sa.Column('parent_category_template_id', sa.Integer(), sa.ForeignKey('guild_template_categories.id', ondelete='SET NULL'), nullable=True),
        sa.Column('discord_channel_id', sa.String(20), nullable=True), # Store actual ID after creation by bot
        sa.Column('metadata_json', sa.JSON(), nullable=True)
    )
    op.create_index('idx_guild_template_channels_template_id', 'guild_template_channels', ['guild_template_id'])
    op.create_index('idx_guild_template_channels_parent_cat', 'guild_template_channels', ['parent_category_template_id'])

    op.create_table(
        'guild_template_category_permissions',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('category_template_id', sa.Integer(), sa.ForeignKey('guild_template_categories.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role_name', sa.String(length=100), nullable=False), # Using name instead of ID
        sa.Column('allow_permissions_bitfield', sa.BigInteger(), nullable=True),
        sa.Column('deny_permissions_bitfield', sa.BigInteger(), nullable=True)
    )
    op.create_index('idx_guild_template_cat_perms_cat_id', 'guild_template_category_permissions', ['category_template_id'])

    op.create_table(
        'guild_template_channel_permissions',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('channel_template_id', sa.Integer(), sa.ForeignKey('guild_template_channels.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role_name', sa.String(length=100), nullable=False), # Using name instead of ID
        sa.Column('allow_permissions_bitfield', sa.BigInteger(), nullable=True),
        sa.Column('deny_permissions_bitfield', sa.BigInteger(), nullable=True)
    )
    op.create_index('idx_guild_template_chan_perms_chan_id', 'guild_template_channel_permissions', ['channel_template_id'])

    # ==========================================================================
    # DASHBOARD Definition Tables (Global/Shared Definitions)
    # ==========================================================================
    op.create_table(
        'dashboard_component_definitions',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('dashboard_type', sa.String(length=100), nullable=False), # e.g., 'common', 'gamehub'
        sa.Column('component_type', sa.String(length=50), nullable=False), # e.g., 'button', 'embed'
        sa.Column('component_key', sa.String(length=100), nullable=False), # e.g., 'minecraft_server', 'system_status'
        sa.Column('definition', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('dashboard_type', 'component_type', 'component_key', name='uq_component_definition')
    )
    op.create_index('idx_component_definition_lookup', 'dashboard_component_definitions', ['dashboard_type', 'component_type', 'component_key'])

    # ==========================================================================
    # DASHBOARD Instance Tables (Guild-Specific)
    # ==========================================================================
    op.create_table(
        'dashboard_instances',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('guild_id', sa.String(20), sa.ForeignKey('discord_guilds.guild_id', ondelete='CASCADE'), nullable=False),
        sa.Column('guild_template_channel_id', sa.Integer(), sa.ForeignKey('guild_template_channels.id', ondelete='SET NULL'), nullable=True),
        sa.Column('dashboard_type', sa.String(length=255), nullable=False), # e.g., 'monitoring', 'gamehub'
        sa.Column('name', sa.String(length=255), nullable=False), # Instance specific name/label if needed
        sa.Column('discord_message_id', sa.String(length=255), nullable=True), # Actual message ID after posting
        sa.Column('config', sa.JSON(), nullable=True), # Instance-specific overrides/config
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False)
    )
    op.create_index('idx_dashboard_instances_guild_id', 'dashboard_instances', ['guild_id'])
    op.create_index('idx_dashboard_instances_channel_template_id', 'dashboard_instances', ['guild_template_channel_id'])

    # ==========================================================================
    # PROJECT Management Tables (Keep as they seem independent)
    # ==========================================================================
    op.create_table(
        'dashboard_project_projects',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True), # Added primary key
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('guild_id', sa.String(20), nullable=False),
        sa.Column('owner_id', sa.String(20), nullable=False),
        sa.Column('status', sa.String(50), server_default='active', nullable=False),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('project_data', sa.JSON(), nullable=True),
        # sa.PrimaryKeyConstraint('id'), # Defined above
        sa.Index('idx_projects_guild_id', 'guild_id')
    )

    op.create_table(
        'dashboard_project_tasks',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True), # Added primary key
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('dashboard_project_projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), server_default='todo', nullable=False),
        sa.Column('priority', sa.String(20), nullable=True),
        sa.Column('assigned_to', sa.String(20), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('task_data', sa.JSON(), nullable=True),
        # sa.PrimaryKeyConstraint('id') # Defined above
    )

    op.create_table(
        'dashboard_project_members',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True), # Added primary key
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('dashboard_project_projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('app_users.id'), nullable=False),
        sa.Column('joined_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        # sa.PrimaryKeyConstraint('id'), # Defined above
        sa.UniqueConstraint('project_id', 'user_id', name='uq_project_member')
    )

    # ==========================================================================
    # WebInterface Tables (Existing one, plus the new one)
    # ==========================================================================
    op.create_table(
        'webinterface_widget_layouts',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('app_users.id'), nullable=False),
        sa.Column('guild_id', sa.String(20), nullable=True),
        sa.Column('page_id', sa.String(50), nullable=False),
        sa.Column('layout_data', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'),
                  onupdate=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('user_id', 'guild_id', 'page_id', name='uq_widget_layout')
    )

    # --- ADDED: ui_layouts table ---
    op.create_table('ui_layouts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('page_identifier', sa.String(), nullable=False), # Use String() without length for text-like behavior if needed, or specify a length
        sa.Column('layout_data', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['app_users.id'], name='fk_ui_layouts_user_id'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'page_identifier', name='_user_page_layout_uc')
    )
    op.create_index(op.f('ix_ui_layouts_id'), 'ui_layouts', ['id'], unique=False)
    op.create_index(op.f('ix_ui_layouts_page_identifier'), 'ui_layouts', ['page_identifier'], unique=False)
    op.create_index(op.f('ix_ui_layouts_user_id'), 'ui_layouts', ['user_id'], unique=False)
    # --- END ADDED ---

    # --- ADDED: shared_ui_layout_templates table ---
    op.create_table('shared_ui_layout_templates',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False, unique=True), # Unique name for the shared template
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('layout_data', sa.JSON(), nullable=False), # The actual Gridstack layout
        sa.Column('creator_user_id', sa.Integer(), sa.ForeignKey('app_users.id', name='fk_shared_ui_layouts_user_id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.Column('source_layout_id', sa.Integer(), nullable=True), # Optional: Track original layout
        # Consider adding guild_id if sharing should be per-guild
        # sa.Column('guild_id', sa.String(20), nullable=True),
        # sa.ForeignKeyConstraint(['guild_id'], ['discord_guilds.guild_id'], name='fk_shared_ui_layouts_guild_id'),
    )
    op.create_index(op.f('ix_shared_ui_layout_templates_name'), 'shared_ui_layout_templates', ['name'], unique=True)
    op.create_index(op.f('ix_shared_ui_layout_templates_created_by'), 'shared_ui_layout_templates', ['creator_user_id'], unique=False)
    # --- END ADDED ---

    # ==========================================================================
    # Remaining DISCORD Tables (If needed, e.g., for general role definitions)
    # ==========================================================================
    op.create_table(
        'discord_server_roles',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True), # Added primary key
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        # sa.PrimaryKeyConstraint('id'), # Defined above
        sa.UniqueConstraint('name')
    )

    op.create_table(
        'discord_guild_users',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True), # Added primary key
        sa.Column('guild_id', sa.String(20), nullable=False), # Should reference discord_guilds.guild_id
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('app_users.id'), nullable=False),
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('app_roles.id'), nullable=False), # Should reference app_roles? Or discord_server_roles? Check FK target.
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        # sa.PrimaryKeyConstraint('id'), # Defined above
        sa.UniqueConstraint('guild_id', 'user_id', name='uq_guild_user')
        # sa.ForeignKeyConstraint(['user_id'], ['app_users.id']), # Defined above
        # sa.ForeignKeyConstraint(['role_id'], ['app_roles.id']) # Defined above
        # Add FK for guild_id to discord_guilds if missing
        # op.create_foreign_key('fk_discord_guild_users_guild', 'discord_guild_users', 'discord_guilds', ['guild_id'], ['guild_id'])
    )


def downgrade() -> None:
    """Drop created tables in reverse order of creation."""

    # Drop tables kept in upgrade
    op.drop_table('discord_guild_users')
    op.drop_table('discord_server_roles')

    # --- ADDED: Drop shared_ui_layout_templates table ---
    op.drop_index(op.f('ix_shared_ui_layout_templates_created_by'), table_name='shared_ui_layout_templates')
    op.drop_index(op.f('ix_shared_ui_layout_templates_name'), table_name='shared_ui_layout_templates')
    op.drop_table('shared_ui_layout_templates')
    # --- END ADDED ---

    # WebInterface Tables
    # --- ADDED: Drop ui_layouts table ---
    op.drop_index(op.f('ix_ui_layouts_user_id'), table_name='ui_layouts')
    op.drop_index(op.f('ix_ui_layouts_page_identifier'), table_name='ui_layouts')
    op.drop_index(op.f('ix_ui_layouts_id'), table_name='ui_layouts')
    op.drop_table('ui_layouts')
    # --- END ADDED ---
    op.drop_table('webinterface_widget_layouts')

    # PROJECT Tables
    op.drop_table('dashboard_project_members')
    op.drop_table('dashboard_project_tasks')
    op.drop_table('dashboard_project_projects')

    # DASHBOARD Instance Tables
    op.drop_index('idx_dashboard_instances_channel_template_id', table_name='dashboard_instances')
    op.drop_index('idx_dashboard_instances_guild_id', table_name='dashboard_instances')
    op.drop_table('dashboard_instances')

    # DASHBOARD Definition Tables
    op.drop_index('idx_component_definition_lookup', table_name='dashboard_component_definitions')
    op.drop_table('dashboard_component_definitions')

    # GUILD TEMPLATE Tables (Reverse order of creation/dependencies)
    op.drop_index('idx_guild_template_chan_perms_chan_id', table_name='guild_template_channel_permissions')
    op.drop_table('guild_template_channel_permissions')
    op.drop_index('idx_guild_template_cat_perms_cat_id', table_name='guild_template_category_permissions')
    op.drop_table('guild_template_category_permissions')
    op.drop_index('idx_guild_template_channels_parent_cat', table_name='guild_template_channels')
    op.drop_index('idx_guild_template_channels_template_id', table_name='guild_template_channels')
    op.drop_table('guild_template_channels')
    op.drop_index('idx_guild_template_categories_template_id', table_name='guild_template_categories')
    op.drop_table('guild_template_categories')
    op.drop_index('idx_guild_templates_guild_id', table_name='guild_templates')
    op.drop_table('guild_templates')

    # Session Table
    op.drop_index('idx_sessions_user_id', table_name='sessions')
    op.drop_index('idx_sessions_token', table_name='sessions')
    op.drop_table('sessions')

    # AUTH Tables
    op.drop_table('app_users')
    op.drop_table('app_roles')

    # Discord Guild Configuration Table
    op.drop_table('guild_configs')

    # DISCORD Guild Table
    op.drop_table('discord_guilds')

    # CORE Tables
    op.drop_table('security_keys')

    # Note: No need to drop tables that were removed from the upgrade function
    # op.drop_table('dashboard_components')
    # op.drop_table('discord_server_permissions')
    # op.drop_table('discord_category_permissions')
    # op.drop_table('discord_channel_permissions')
    # op.drop_table('channel_mappings')
    # op.drop_table('discord_channels')
    # op.drop_table('category_mappings')
    # op.drop_table('discord_categories')
