from decimal import Decimal

from sqlalchemy.orm import Session

from salary_management.persistence.exchange_rate_repository import ExchangeRateRepository
from salary_management.seed import seed_exchange_rates


def test_looks_up_decimal_rate_and_returns_none_when_missing(session: Session) -> None:
    seed_exchange_rates(session)
    session.flush()
    repository = ExchangeRateRepository(session)

    assert repository.get_rate_to_usd("INR") == Decimal("0.0120000000")
    assert repository.get_rate_to_usd("JPY") is None
