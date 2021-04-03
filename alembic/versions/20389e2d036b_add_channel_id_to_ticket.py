"""Add channel id to ticket

Revision ID: 20389e2d036b
Revises: 7e7d3ab7b310
Create Date: 2021-04-03 08:57:35.018608+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20389e2d036b"
down_revision = "7e7d3ab7b310"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "tickets", sa.Column("channel_id", sa.BigInteger(), nullable=True)
    )
    op.create_index(
        op.f("ix_tickets_channel_id"), "tickets", ["channel_id"], unique=False
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_tickets_channel_id"), table_name="tickets")
    op.drop_column("tickets", "channel_id")
    # ### end Alembic commands ###
