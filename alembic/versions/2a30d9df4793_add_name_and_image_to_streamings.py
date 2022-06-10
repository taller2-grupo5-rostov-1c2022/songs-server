"""add name and image to streamings

Revision ID: 2a30d9df4793
Revises: f92d1310b2b6
Create Date: 2022-06-07 22:32:56.237776

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2a30d9df4793"
down_revision = "f92d1310b2b6"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column("users", "streaming_listener_token")
    op.create_table(
        "streamings",
        sa.Column("listener_token", sa.String, primary_key=True),
        sa.Column(
            "artist_id",
            sa.String,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            unique=True,
        ),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("img_url", sa.String, nullable=True),
    )


def downgrade():
    op.drop_table("streamings")
    op.add_column("users", sa.Column("streaming_listener_token", sa.String))
