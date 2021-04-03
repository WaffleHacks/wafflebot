"""Add category setting key

Revision ID: 7e7d3ab7b310
Revises: 0050251979c5
Create Date: 2021-04-03 06:17:05.337113+00:00

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "7e7d3ab7b310"
down_revision = "0050251979c5"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE settingskey ADD VALUE 'TicketCategory'")


def downgrade():
    # Delete any rows referencing the enum state
    op.execute("DELETE FROM settings WHERE key = 'TicketCategory'")

    # Rename the old type
    op.execute("ALTER TYPE settingskey RENAME TO settingskey_old")

    # Create a new type with all fields except TicketCategory
    op.execute(
        "CREATE TYPE settingskey AS ENUM('ManagementRole', 'PanelAccessRole', 'MentionRole')"
    )

    # Change the column type
    op.execute(
        "ALTER TABLE settings ALTER COLUMN key TYPE settingskey USING key::text::settingskey"
    )

    # Remove the old type
    op.execute("DROP TYPE settingskey_old")
