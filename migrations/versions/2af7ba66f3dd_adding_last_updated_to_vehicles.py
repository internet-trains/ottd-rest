"""Adding last_updated to vehicles

Revision ID: 2af7ba66f3dd
Revises: a96bcd8e69ef
Create Date: 2020-06-07 13:34:16.157184

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2af7ba66f3dd"
down_revision = "a96bcd8e69ef"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("vehicle", sa.Column("last_updated", sa.Date(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("vehicle", "last_updated")
    # ### end Alembic commands ###
