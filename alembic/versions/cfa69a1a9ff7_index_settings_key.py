"""Index settings key

Revision ID: cfa69a1a9ff7
Revises: d7abd9c4a449
Create Date: 2021-03-13 05:58:32.044411+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "cfa69a1a9ff7"
down_revision = "d7abd9c4a449"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f("ix_settings_key"), "settings", ["key"], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_settings_key"), table_name="settings")
    # ### end Alembic commands ###
