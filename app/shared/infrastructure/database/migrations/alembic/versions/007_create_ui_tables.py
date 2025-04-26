"""Create UI layout tables

Revision ID: 007
Revises: 006
Create Date: 2025-04-26 
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '007'
down_revision = '006' # Depends on app_users (001)
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'webinterface_widget_layouts', # Keeping the old table for now? Or remove? Assuming keep.
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
    # ui_layouts table
    op.create_table('ui_layouts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('page_identifier', sa.String(), nullable=False), 
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
    
    # shared_ui_layout_templates table
    op.create_table('shared_ui_layout_templates',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(length=100), nullable=False, unique=True), 
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('layout_data', sa.JSON(), nullable=False), 
        sa.Column('creator_user_id', sa.Integer(), sa.ForeignKey('app_users.id', name='fk_shared_ui_layouts_user_id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.Column('source_layout_id', sa.Integer(), nullable=True), 
    )
    op.create_index(op.f('ix_shared_ui_layout_templates_name'), 'shared_ui_layout_templates', ['name'], unique=True)
    op.create_index(op.f('ix_shared_ui_layout_templates_created_by'), 'shared_ui_layout_templates', ['creator_user_id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_shared_ui_layout_templates_created_by'), table_name='shared_ui_layout_templates')
    op.drop_index(op.f('ix_shared_ui_layout_templates_name'), table_name='shared_ui_layout_templates')
    op.drop_table('shared_ui_layout_templates')
    op.drop_index(op.f('ix_ui_layouts_user_id'), table_name='ui_layouts')
    op.drop_index(op.f('ix_ui_layouts_page_identifier'), table_name='ui_layouts')
    op.drop_index(op.f('ix_ui_layouts_id'), table_name='ui_layouts')
    op.drop_table('ui_layouts')
    op.drop_table('webinterface_widget_layouts')