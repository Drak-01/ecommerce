"""ajout colonne created_at à order

Revision ID: 00b2d915d989
Revises: 
Create Date: 2025-06-04 16:25:27.784938

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '00b2d915d989'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))

    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.alter_column('stock',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
        batch_op.alter_column('image',
               existing_type=mysql.VARCHAR(length=100),
               type_=sa.String(length=200),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.alter_column('image',
               existing_type=sa.String(length=200),
               type_=mysql.VARCHAR(length=100),
               existing_nullable=True)
        batch_op.alter_column('stock',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)

    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.drop_column('created_at')

    # ### end Alembic commands ###
