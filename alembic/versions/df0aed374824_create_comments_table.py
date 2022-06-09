"""create comments table

Revision ID: df0aed374824
Revises: 
Create Date: 2022-05-23 11:47:33.424174

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "df0aed374824"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("album_id", sa.Integer, sa.ForeignKey("albums.id"), nullable=True),
        sa.Column("commenter_id", sa.String, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("score", sa.Integer, nullable=True),
        sa.Column("text", sa.String, nullable=True),
    )


def downgrade():
    op.drop_table("comments")
