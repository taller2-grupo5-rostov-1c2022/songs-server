"""change comments table to reviews table

Revision ID: e265a1960086
Revises: 80ca5cf7ccc3
Create Date: 2022-06-05 03:10:54.239825

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e265a1960086'
down_revision = '80ca5cf7ccc3'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('comments', 'reviews')
    op.alter_column('reviews', 'commenter_id', new_column_name='reviewer_id')


def downgrade():
    op.rename_table('reviews', 'comments')
    op.alter_column('comments', 'reviewer_id', new_column_name='commenter_id')
