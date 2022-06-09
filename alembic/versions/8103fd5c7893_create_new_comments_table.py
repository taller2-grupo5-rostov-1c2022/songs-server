"""create new comments table

Revision ID: 8103fd5c7893
Revises: e265a1960086
Create Date: 2022-06-05 03:15:13.715144

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8103fd5c7893'
down_revision = 'e265a1960086'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'comments',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('commenter_id', sa.String, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('text', sa.String, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('parent_id', sa.ForeignKey('comments.id'), nullable=True),
        sa.Column('album_id', sa.Integer, sa.ForeignKey('albums.id'), nullable=True),
    )


def downgrade():
    op.drop_table('comments')

