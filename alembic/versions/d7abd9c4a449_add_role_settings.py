"""Add role settings

Revision ID: d7abd9c4a449
Revises: b8a5fd8b0cdb
Create Date: 2021-03-13 02:24:11.520736+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d7abd9c4a449"
down_revision = "b8a5fd8b0cdb"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "key",
            sa.Enum(
                "ManagementRole",
                "PanelAccessRole",
                "MentionRole",
                name="settingskey",
            ),
            nullable=False,
        ),
        sa.Column("value", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_settings_id"), "settings", ["id"], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_settings_id"), table_name="settings")
    op.drop_table("settings")
    # ### end Alembic commands ###
