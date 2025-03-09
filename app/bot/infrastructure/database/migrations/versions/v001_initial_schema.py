"""Initial schema

Revision ID: v001
Create Date: 2023-xx-xx

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'v001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create all initial tables here
    # ...
    pass

def downgrade():
    # Drop all tables in reverse order
    # ...
    pass
