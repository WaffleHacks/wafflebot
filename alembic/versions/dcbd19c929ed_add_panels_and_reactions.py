"""Add panels and reactions

Revision ID: dcbd19c929ed
Revises: 80a9c1f3f0c4
Create Date: 2021-04-04 00:48:58.131603+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "dcbd19c929ed"
down_revision = "80a9c1f3f0c4"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "panels",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("message_id", sa.BigInteger(), nullable=True),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_panels_id"), "panels", ["id"], unique=False)
    op.create_index(
        op.f("ix_panels_message_id"), "panels", ["message_id"], unique=False
    )
    op.create_table(
        "reactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("emoji", sa.String(length=64), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("panel_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
        ),
        sa.ForeignKeyConstraint(
            ["panel_id"],
            ["panels.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_reactions_id"), "reactions", ["id"], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_reactions_id"), table_name="reactions")
    op.drop_table("reactions")
    op.drop_index(op.f("ix_panels_message_id"), table_name="panels")
    op.drop_index(op.f("ix_panels_id"), table_name="panels")
    op.drop_table("panels")
    # ### end Alembic commands ###
