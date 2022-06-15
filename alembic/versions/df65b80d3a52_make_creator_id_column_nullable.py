"""make creator_id column nullable

Revision ID: df65b80d3a52
Revises: 2a30d9df4793
Create Date: 2022-06-09 23:35:08.448127

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "df65b80d3a52"
down_revision = "2a30d9df4793"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("songs", "creator_id", nullable=True)
    op.alter_column("albums", "creator_id", nullable=True)
    op.alter_column("playlists", "creator_id", nullable=True)


def downgrade():
    op.alter_column("songs", "creator_id", nullable=False)
    op.alter_column("albums", "creator_id", nullable=False)
    op.alter_column("playlists", "creator_id", nullable=False)
