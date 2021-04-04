"""Migrate settings to Redis

Revision ID: 485d2a94f8f4
Revises: 61fead81e7a2
Create Date: 2021-04-04 22:16:38.872930+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "485d2a94f8f4"
down_revision = "61fead81e7a2"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index(op.f("ix_settings_id"), table_name="settings")
    op.drop_index(op.f("ix_settings_key"), table_name="settings")
    op.drop_table("settings")
    op.execute("DROP TYPE settingskey")


def downgrade():
    op.create_table(
        "settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "key",
            sa.Enum(
                "ManagementRole",
                "PanelAccessRole",
                "MentionRole",
                "TicketCategory",
                "ArchiveChannel",
                name="settingskey",
            ),
        ),
        sa.Column("value", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_settings_id"), "settings", ["id"], unique=False)
    op.create_index(op.f("ix_settings_key"), "settings", ["key"], unique=False)
