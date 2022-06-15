"""fix favorite playlists table

Revision ID: 80ca5cf7ccc3
Revises: 5c1bf26c4313
Create Date: 2022-05-23 16:18:58.064207

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "80ca5cf7ccc3"
down_revision = "5c1bf26c4313"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("playlist_favorites_association")
    op.create_table(
        "playlist_favorite_association",
        sa.Column(
            "user_id",
            sa.String,
            sa.ForeignKey("users.id", onupdate="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "playlist_id",
            sa.Integer,
            sa.ForeignKey("playlists.id", onupdate="CASCADE"),
            primary_key=True,
        ),
    )


def downgrade():
    op.drop_table("playlist_favorite_association")
    op.create_table(
        "playlist_favorites_association",
        sa.Column(
            "user_id",
            sa.String,
            sa.ForeignKey("users.id", onupdate="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "playlist_id",
            sa.Integer,
            sa.ForeignKey("playlists.id", onupdate="CASCADE"),
            primary_key=True,
        ),
    )
