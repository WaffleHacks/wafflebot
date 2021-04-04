"""Add archive channel setting key

Revision ID: f90d606fedf5
Revises: dcbd19c929ed
Create Date: 2021-04-04 02:20:54.110410+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f90d606fedf5"
down_revision = "dcbd19c929ed"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("ALTER TYPE settingskey ADD VALUE 'ArchiveChannel'")


def downgrade():
    # Delete any rows referencing the enum state
    op.execute("DELETE FROM settings WHERE key = 'ArchiveChannel'")

    # Rename the old type
    op.execute("ALTER TYPE settingskey RENAME TO settingskey_old")

    # Create a new type with all fields except TicketCategory
    op.execute(
        "CREATE TYPE settingskey AS ENUM('ManagementRole', 'PanelAccessRole', 'MentionRole', 'TicketCategory')"
    )

    # Change the column type
    op.execute(
        "ALTER TABLE settings ALTER COLUMN key TYPE settingskey USING key::text::settingskey"
    )

    # Remove the old type
    op.execute("DROP TYPE settingskey_old")
