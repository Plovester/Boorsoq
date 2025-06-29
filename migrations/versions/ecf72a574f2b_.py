"""empty message

Revision ID: ecf72a574f2b
Revises: c5597fb2b0dc
Create Date: 2025-06-12 14:46:21.573656

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ecf72a574f2b'
down_revision = 'c5597fb2b0dc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('confirmed_on',
               existing_type=sa.DATETIME(),
               nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('confirmed_on',
               existing_type=sa.DATETIME(),
               nullable=True)

    # ### end Alembic commands ###
