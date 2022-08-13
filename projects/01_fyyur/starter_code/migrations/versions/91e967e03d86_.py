"""empty message

Revision ID: 91e967e03d86
Revises: f18ad3014da6
Create Date: 2022-08-12 19:24:35.864132

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '91e967e03d86'
down_revision = 'f18ad3014da6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shows', sa.Column('starting_time', sa.DateTime(timezone=True), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('shows', 'starting_time')
    # ### end Alembic commands ###
