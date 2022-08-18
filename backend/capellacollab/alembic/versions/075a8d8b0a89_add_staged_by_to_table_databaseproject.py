"""Add staged_by to table DatabaseProject

Revision ID: 075a8d8b0a89
Revises: d64fc5a97252
Create Date: 2022-08-16 16:04:06.036545

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "075a8d8b0a89"
down_revision = "d64fc5a97252"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("projects", sa.Column("staged_by", sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    op.drop_column("projects", "staged_by")
    # ### end Alembic commands #####
