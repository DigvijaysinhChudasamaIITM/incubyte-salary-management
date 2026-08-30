"""Create employees table.

Revision ID: 20260830_01
Revises:
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260830_01"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "employees",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("employee_code", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("country", sa.String(length=2), nullable=False),
        sa.Column("department", sa.String(length=80), nullable=False),
        sa.Column("job_title", sa.String(length=100), nullable=False),
        sa.Column("salary_amount", sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.CheckConstraint("length(currency) = 3", name="ck_employees_currency_length"),
        sa.CheckConstraint("salary_amount > 0", name="ck_employees_salary_positive"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_employees_country", "employees", ["country"])
    op.create_index(
        "ix_employees_country_department", "employees", ["country", "department"]
    )
    op.create_index("ix_employees_department", "employees", ["department"])
    op.create_index("ix_employees_email", "employees", ["email"], unique=True)
    op.create_index("ix_employees_employee_code", "employees", ["employee_code"], unique=True)
    op.create_index("ix_employees_name", "employees", ["name"])


def downgrade() -> None:
    op.drop_index("ix_employees_name", table_name="employees")
    op.drop_index("ix_employees_employee_code", table_name="employees")
    op.drop_index("ix_employees_email", table_name="employees")
    op.drop_index("ix_employees_department", table_name="employees")
    op.drop_index("ix_employees_country_department", table_name="employees")
    op.drop_index("ix_employees_country", table_name="employees")
    op.drop_table("employees")
