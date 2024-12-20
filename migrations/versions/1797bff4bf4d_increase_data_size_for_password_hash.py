"""Increase data size for password hash

Revision ID: 1797bff4bf4d
Revises: 901f90d44fab
Create Date: 2024-12-09 15:36:14.663143

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1797bff4bf4d'
down_revision = '901f90d44fab'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password_hash',
               existing_type=sa.VARCHAR(length=128),
               type_=sa.String(length=250),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password_hash',
               existing_type=sa.String(length=250),
               type_=sa.VARCHAR(length=128),
               existing_nullable=True)

    # ### end Alembic commands ###
