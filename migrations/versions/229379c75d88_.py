"""empty message

Revision ID: 229379c75d88
Revises: 1d2f49b27d2a
Create Date: 2025-02-20 11:19:13.025514

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '229379c75d88'
down_revision = '1d2f49b27d2a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('categories', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_url', sa.String(length=250), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('categories', schema=None) as batch_op:
        batch_op.drop_column('image_url')

    # ### end Alembic commands ###
