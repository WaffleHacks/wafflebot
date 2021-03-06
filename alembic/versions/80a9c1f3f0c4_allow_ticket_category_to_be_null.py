"""Allow ticket category to be null

Revision ID: 80a9c1f3f0c4
Revises: 20389e2d036b
Create Date: 2021-04-03 20:17:11.479962+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "80a9c1f3f0c4"
down_revision = "20389e2d036b"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "tickets", "category_id", existing_type=sa.INTEGER(), nullable=True
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "tickets", "category_id", existing_type=sa.INTEGER(), nullable=False
    )
    # ### end Alembic commands ###
