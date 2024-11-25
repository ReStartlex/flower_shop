"""Add password field to Client model

Revision ID: 91177f0aa130
Revises: 3162ce4b96d5
Create Date: 2024-11-26 00:01:36.767268

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '91177f0aa130'
down_revision = '3162ce4b96d5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password', sa.String(length=128), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.drop_column('password')

    # ### end Alembic commands ###
