"""add album sub_level temporarily

Revision ID: ac32c8def835
Revises: 570cfe8ee431
Create Date: 2022-06-13 16:11:39.001563

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ac32c8def835'
down_revision = '570cfe8ee431'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("albums", sa.Column("sub_level", sa.Integer(), nullable=True))
    op.execute("UPDATE albums SET sub_level = 0")
    op.alter_column("albums", "sub_level", nullable=False)


def downgrade():
    op.drop_column("albums", "sub_level")
