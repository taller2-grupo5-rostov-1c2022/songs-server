"""add sub_level column to users table and remove it from albums

Revision ID: 570cfe8ee431
Revises: df65b80d3a52
Create Date: 2022-06-10 18:37:28.120277

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "570cfe8ee431"
down_revision = "df65b80d3a52"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("sub_level", sa.Integer(), nullable=True))
    op.execute("UPDATE users SET sub_level = 0")
    op.alter_column("users", "sub_level", nullable=False)

    op.add_column("users", sa.Column("sub_expires", sa.DateTime(), nullable=True))
    op.drop_column("albums", "sub_level")


def downgrade():
    op.add_column("albums", sa.Column("sub_level", sa.Integer(), nullable=True))
    op.execute("UPDATE albums SET sub_level = 0")
    op.alter_column("albums", "sub_level", nullable=False)
    op.drop_column("users", "sub_level")
    op.drop_column("users", "sub_expires")
