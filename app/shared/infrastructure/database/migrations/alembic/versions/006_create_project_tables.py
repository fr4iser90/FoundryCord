"""Create project management tables

Revision ID: 006
Revises: 005
Create Date: 2025-04-26 
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '006'
down_revision = '005' # Depends on app_users (001)
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True), 
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('guild_id', sa.String(20), nullable=False),
        sa.Column('owner_id', sa.String(20), nullable=False),
        sa.Column('status', sa.String(50), server_default='active', nullable=False),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('project_data', sa.JSON(), nullable=True),
        sa.Index('idx_projects_guild_id', 'guild_id')
    )
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True), 
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), server_default='todo', nullable=False),
        sa.Column('priority', sa.String(20), nullable=True),
        sa.Column('assigned_to', sa.String(20), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('task_data', sa.JSON(), nullable=True),
    )
    op.create_table(
        'project_members',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True), 
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('app_users.id'), nullable=False),
        sa.Column('joined_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('project_id', 'user_id', name='uq_project_member')
    )

def downgrade() -> None:
    op.drop_table('project_members')
    op.drop_table('tasks')
    op.drop_table('projects')