"""empty message

Revision ID: 2a4484ca0601
Revises: 72b5424128d4
Create Date: 2022-03-17 00:40:26.627008

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2a4484ca0601'
down_revision = '72b5424128d4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('user_id', table_name='cards')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('user_id', 'cards', ['user_id'], unique=False)
    # ### end Alembic commands ###