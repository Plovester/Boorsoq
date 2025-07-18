"""empty message

Revision ID: e7f5905b5e15
Revises: 993700eb81e4
Create Date: 2025-04-23 17:14:14.262467

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = 'e7f5905b5e15'
down_revision = '993700eb81e4'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_context().connection
    table_columns = op.get_context().dialect.get_columns(conn, 'users')
    registered_on_col = next((column for column in table_columns if column['name'] == "registered_on"), None)
    confirmed_col = next((column for column in table_columns if column['name'] == "confirmed"), None)
    confirmed_on_col = next((column for column in table_columns if column['name'] == "confirmed_on"), None)

    if not registered_on_col:
        with op.batch_alter_table('users', schema=None) as batch_op:
            batch_op.add_column(sa.Column('registered_on', sa.DateTime(), nullable=True))

    if not confirmed_col:
        with op.batch_alter_table('users', schema=None) as batch_op:
            batch_op.add_column(sa.Column('confirmed', sa.Boolean(), nullable=True))

    if not confirmed_on_col:
        with op.batch_alter_table('users', schema=None) as batch_op:
            batch_op.add_column(sa.Column('confirmed_on', sa.DateTime(), nullable=True))

    statement_registered_at = text(
        """UPDATE users SET registered_on = datetime('now') WHERE registered_on IS NULL""")
    statement_confirmed = text(
        """UPDATE users SET confirmed = 1 WHERE confirmed IS NULL""")
    statement_confirmed_at = text(
        """UPDATE users SET confirmed_on = datetime('now') WHERE confirmed_on IS NULL""")

    conn.execute(statement_registered_at)
    conn.execute(statement_confirmed)
    conn.execute(statement_confirmed_at)


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('confirmed_on')
        batch_op.drop_column('confirmed')
        batch_op.drop_column('registered_on')

    # ### end Alembic commands ###
