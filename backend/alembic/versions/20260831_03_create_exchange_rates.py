"""Create exchange rates table.

Revision ID: 20260831_03
Revises: 20260831_02
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260831_03"
down_revision: str | None = "20260831_02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "exchange_rates",
        sa.Column("currency_code", sa.String(length=3), nullable=False),
        sa.Column("rate_to_usd", sa.Numeric(precision=20, scale=10), nullable=False),
        sa.Column("effective_date", sa.Date(), nullable=False),
        sa.CheckConstraint(
            "length(currency_code) = 3", name="ck_exchange_rates_currency_length"
        ),
        sa.CheckConstraint("rate_to_usd > 0", name="ck_exchange_rates_rate_positive"),
        sa.PrimaryKeyConstraint("currency_code"),
    )


def downgrade() -> None:
    op.drop_table("exchange_rates")
