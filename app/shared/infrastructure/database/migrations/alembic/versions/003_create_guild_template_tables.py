"""Create guild template tables

Revision ID: 003
Revises: 002
Create Date: 2025-04-26 
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '003'
down_revision = '002' # Depends on auth_tables (001) and discord_guild_tables (002)
branch_labels = None
depends_on = None

def upgrade() -> None:
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
        sa.Column('channel_type', sa.String(length=50), nullable=False), 
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('topic', sa.Text(), nullable=True),
        sa.Column('is_nsfw', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('slowmode_delay', sa.Integer(), server_default='0', nullable=False),
        sa.Column('parent_category_template_id', sa.Integer(), sa.ForeignKey('guild_template_categories.id', ondelete='SET NULL'), nullable=True),
        sa.Column('discord_channel_id', sa.String(20), nullable=True), 
        sa.Column('metadata_json', sa.JSON(), nullable=True)
    )
    op.create_index('idx_guild_template_channels_template_id', 'guild_template_channels', ['guild_template_id'])
    op.create_index('idx_guild_template_channels_parent_cat', 'guild_template_channels', ['parent_category_template_id'])

    op.create_table(
        'guild_template_category_permissions',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('category_template_id', sa.Integer(), sa.ForeignKey('guild_template_categories.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role_name', sa.String(length=100), nullable=False), 
        sa.Column('allow_permissions_bitfield', sa.BigInteger(), nullable=True),
        sa.Column('deny_permissions_bitfield', sa.BigInteger(), nullable=True)
    )
    op.create_index('idx_guild_template_cat_perms_cat_id', 'guild_template_category_permissions', ['category_template_id'])

    op.create_table(
        'guild_template_channel_permissions',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('channel_template_id', sa.Integer(), sa.ForeignKey('guild_template_channels.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role_name', sa.String(length=100), nullable=False), 
        sa.Column('allow_permissions_bitfield', sa.BigInteger(), nullable=True),
        sa.Column('deny_permissions_bitfield', sa.BigInteger(), nullable=True)
    )
    op.create_index('idx_guild_template_chan_perms_chan_id', 'guild_template_channel_permissions', ['channel_template_id'])

def downgrade() -> None:
    op.drop_index('idx_guild_template_chan_perms_chan_id', table_name='guild_template_channel_permissions')
    op.drop_table('guild_template_channel_permissions')
    op.drop_index('idx_guild_template_cat_perms_cat_id', table_name='guild_template_category_permissions')
    op.drop_table('guild_template_category_permissions')
    op.drop_index('idx_guild_template_channels_parent_cat', table_name='guild_template_channels')
    op.drop_index('idx_guild_template_channels_template_id', table_name='guild_template_channels')
    op.drop_table('guild_template_channels')
    op.drop_index('idx_guild_template_categories_template_id', table_name='guild_template_categories')
    op.drop_table('guild_template_categories')
    op.drop_index('idx_guild_templates_creator_user_id', table_name='guild_templates')
    op.drop_index('idx_guild_templates_guild_id', table_name='guild_templates')
    op.drop_table('guild_templates')