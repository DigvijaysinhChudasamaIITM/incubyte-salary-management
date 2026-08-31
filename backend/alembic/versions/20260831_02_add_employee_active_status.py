"""Add employee active status.

Revision ID: 20260831_02
Revises: 20260830_01
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260831_02"
down_revision: str | None = "20260830_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "employees",
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
    )
    op.create_index("ix_employees_is_active", "employees", ["is_active"])


def downgrade() -> None:
    op.drop_index("ix_employees_is_active", table_name="employees")
    op.drop_column("employees", "is_active")
