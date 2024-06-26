"""empty message

Revision ID: b17cbeb057e6
Revises: aaccde1bc1cd
Create Date: 2024-06-26 14:17:02.051712

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b17cbeb057e6'
down_revision = 'aaccde1bc1cd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=sa.VARCHAR(length=250),
               type_=sa.DateTime(),
               existing_nullable=False)
        batch_op.alter_column('ready_by_date',
               existing_type=sa.VARCHAR(length=250),
               type_=sa.DateTime(),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.alter_column('ready_by_date',
               existing_type=sa.DateTime(),
               type_=sa.VARCHAR(length=250),
               existing_nullable=False)
        batch_op.alter_column('created_at',
               existing_type=sa.DateTime(),
               type_=sa.VARCHAR(length=250),
               existing_nullable=False)

    # ### end Alembic commands ###
