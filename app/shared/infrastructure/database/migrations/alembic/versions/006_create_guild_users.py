"""Create guild_users table for multi-guild user roles

Revision ID: 006
Revises: 005
Create Date: 2024-03-25 10:00:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Erstelle guild_users Tabelle
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
        sa.ForeignKeyConstraint(['role_id'], ['roles.id']),
        sa.UniqueConstraint('guild_id', 'user_id')
    )
    
    # Index für schnellere Abfragen
    op.create_index('idx_guild_users_guild_user', 'guild_users', ['guild_id', 'user_id'])

def downgrade() -> None:
    op.drop_table('guild_users')