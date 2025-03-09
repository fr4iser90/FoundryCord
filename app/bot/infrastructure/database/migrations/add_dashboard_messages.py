# app/bot/infrastructure/database/migrations/add_dashboard_messages.py
"""Add dashboard_messages table"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'add_dashboard_messages'
down_revision = 'previous_migration'  # replace with your actual previous migration

def upgrade():
    op.create_table(
        'dashboard_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dashboard_type', sa.String(), nullable=False),
        sa.Column('message_id', sa.BigInteger(), nullable=False),
        sa.Column('channel_id', sa.BigInteger(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dashboard_messages_dashboard_type'), 'dashboard_messages', ['dashboard_type'], unique=True)

def downgrade():
    op.drop_index(op.f('ix_dashboard_messages_dashboard_type'), table_name='dashboard_messages')
    op.drop_table('dashboard_messages')