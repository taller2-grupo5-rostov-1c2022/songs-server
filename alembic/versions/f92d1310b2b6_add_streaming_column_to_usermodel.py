"""add streaming column to UserModel

Revision ID: f92d1310b2b6
Revises: 1379f298dcf4
Create Date: 2022-06-07 02:19:47.622258

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f92d1310b2b6"
down_revision = "8103fd5c7893"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users", sa.Column("streaming_listener_token", sa.String(), nullable=True)
    )


def downgrade():
    op.drop_column("users", "streaming_listener_token")
