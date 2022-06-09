"""create favorites tables

Revision ID: 5c1bf26c4313
Revises: df0aed374824
Create Date: 2022-05-23 12:02:52.679876

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5c1bf26c4313"
down_revision = "df0aed374824"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "song_favorites_association",
        sa.Column(
            "user_id",
            sa.String,
            sa.ForeignKey("users.id", onupdate="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "song_id",
            sa.Integer,
            sa.ForeignKey("songs.id", onupdate="CASCADE"),
            primary_key=True,
        ),
    )
    op.create_table(
        "album_favorites_association",
        sa.Column(
            "user_id",
            sa.String,
            sa.ForeignKey("users.id", onupdate="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "album_id",
            sa.Integer,
            sa.ForeignKey("albums.id", onupdate="CASCADE"),
            primary_key=True,
        ),
    )
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


def downgrade():
    op.drop_table("playlist_favorites_association")
    op.drop_table("album_favorites_association")
    op.drop_table("song_favorites_association")
