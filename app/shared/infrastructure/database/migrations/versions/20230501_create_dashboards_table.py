"""Create dashboards table

Revision ID: create_dashboards_table
Revises: previous_migration_id
Create Date: 2023-05-01 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'create_dashboards_table'
down_revision = 'previous_migration_id'  # Replace with actual previous migration ID
branch_labels = None
depends_on = None

def upgrade():
    # Create dashboards table
    op.create_table(
        'dashboards',
        sa.Column('id', sa.String(50), primary_key=True),
        sa.Column('title', sa.String(100), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('dashboard_type', sa.String(50), nullable=False),
        sa.Column('channel_id', sa.Integer, nullable=True),
        sa.Column('guild_id', sa.Integer, nullable=True),
        sa.Column('message_id', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime, default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('config', sa.Text, nullable=True),
    )

def downgrade():
    # Drop dashboards table
    op.drop_table('dashboards') 