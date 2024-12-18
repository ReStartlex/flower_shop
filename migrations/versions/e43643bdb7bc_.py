"""empty message

Revision ID: e43643bdb7bc
Revises: 7cf5b4f9175c
Create Date: 2024-12-01 15:32:03.062367

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e43643bdb7bc'
down_revision = '7cf5b4f9175c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.add_column(sa.Column('role', sa.Enum('ADMIN', 'CLIENT', name='roleenum'), nullable=True))
        batch_op.create_unique_constraint(None, ['phone'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('role')

    # ### end Alembic commands ###
