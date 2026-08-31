from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from salary_management.application.exchange_rates import (
    ExchangeRateUnavailable,
    normalize_salary_to_usd,
)
from salary_management.persistence.exchange_rate_repository import ExchangeRateRepository
from salary_management.seed import EXCHANGE_RATES, seed_exchange_rates


@pytest.mark.parametrize(
    ("currency", "native_salary", "expected_usd"),
    [
        ("USD", Decimal("1234.56"), Decimal("1234.560000000000")),
        ("INR", Decimal("100000.00"), Decimal("1200.000000000000")),
        ("GBP", Decimal("80000.00"), Decimal("100000.000000000000")),
        ("EUR", Decimal("90000.00"), Decimal("99000.000000000000")),
        ("CAD", Decimal("75000.00"), Decimal("55500.000000000000")),
    ],
)
def test_normalizes_representative_native_salaries_with_decimal_accuracy(
    session: Session,
    currency: str,
    native_salary: Decimal,
    expected_usd: Decimal,
) -> None:
    seed_exchange_rates(session)
    session.flush()

    result = normalize_salary_to_usd(
        native_salary, currency, ExchangeRateRepository(session)
    )

    assert result == expected_usd
    assert isinstance(result, Decimal)
    assert result == native_salary * EXCHANGE_RATES[currency]


def test_preserves_precision_without_rounding(session: Session) -> None:
    seed_exchange_rates(session)
    session.flush()

    assert normalize_salary_to_usd(
        Decimal("123.45"), "INR", ExchangeRateRepository(session)
    ) == Decimal("1.481400000000")


def test_missing_rate_has_explicit_application_failure(session: Session) -> None:
    with pytest.raises(ExchangeRateUnavailable) as error:
        normalize_salary_to_usd(
            Decimal("100.00"), "JPY", ExchangeRateRepository(session)
        )

    assert error.value.code == "exchange_rate_unavailable"
    assert error.value.currency_code == "JPY"
    assert str(error.value) == "exchange_rate_unavailable"


def test_rejects_float_input(session: Session) -> None:
    with pytest.raises(TypeError, match="must be a Decimal"):
        normalize_salary_to_usd(  # type: ignore[arg-type]
            100.0, "USD", ExchangeRateRepository(session)
        )
