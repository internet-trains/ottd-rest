"""Adding company details

Revision ID: 209cda7e6ae5
Revises: bd0d42ac183c
Create Date: 2020-06-06 17:12:01.168066

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "209cda7e6ae5"
down_revision = "bd0d42ac183c"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "company", sa.Column("bankruptcy_counter", sa.Integer(), nullable=True)
    )
    op.add_column("company", sa.Column("color", sa.Integer(), nullable=True))
    op.add_column("company", sa.Column("is_ai", sa.Boolean(), nullable=True))
    op.add_column("company", sa.Column("manager", sa.String(length=64), nullable=True))
    op.add_column("company", sa.Column("passworded", sa.Boolean(), nullable=True))
    op.add_column("company", sa.Column("start_year", sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("company", "start_year")
    op.drop_column("company", "passworded")
    op.drop_column("company", "manager")
    op.drop_column("company", "is_ai")
    op.drop_column("company", "color")
    op.drop_column("company", "bankruptcy_counter")
    # ### end Alembic commands ###
