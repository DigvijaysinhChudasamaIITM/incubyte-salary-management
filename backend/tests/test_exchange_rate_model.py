from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from salary_management.persistence.models import ExchangeRate


def test_exchange_rate_round_trips_with_declared_decimal_precision(session: Session) -> None:
    rate = ExchangeRate(
        currency_code="INR",
        rate_to_usd=Decimal("0.0123456789"),
        effective_date=date(2026, 8, 31),
    )
    session.add(rate)
    session.commit()
    session.refresh(rate)

    assert rate.rate_to_usd == Decimal("0.0123456789")
    assert isinstance(rate.rate_to_usd, Decimal)


@pytest.mark.parametrize(
    ("currency_code", "rate_to_usd"),
    [("US", Decimal("1.0")), ("USDD", Decimal("1.0")), ("USD", Decimal("0"))],
)
def test_exchange_rate_constraints(
    session: Session, currency_code: str, rate_to_usd: Decimal
) -> None:
    session.add(
        ExchangeRate(
            currency_code=currency_code,
            rate_to_usd=rate_to_usd,
            effective_date=date(2026, 8, 31),
        )
    )

    with pytest.raises(IntegrityError):
        session.commit()
