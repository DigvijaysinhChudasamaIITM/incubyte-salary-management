from decimal import Decimal

import pytest
from conftest import employee
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from salary_management.persistence.models import Employee, ExchangeRate
from salary_management.seed import (
    EMPLOYEE_COUNT,
    EXCHANGE_RATE_DATE,
    EXCHANGE_RATES,
    SeedDataConflict,
    seed_employees,
    seed_exchange_rates,
)


def test_seeds_exactly_ten_thousand_employees_and_is_repeatable(session: Session) -> None:
    inserted = seed_employees(session)
    session.commit()

    inserted_on_repeat = seed_employees(session)
    total = session.scalar(select(func.count()).select_from(Employee))

    assert inserted == EMPLOYEE_COUNT
    assert inserted_on_repeat == 0
    assert total == EMPLOYEE_COUNT
    first = session.scalar(select(Employee).where(Employee.employee_code == "EMP00001"))
    last = session.scalar(select(Employee).where(Employee.employee_code == "EMP10000"))
    assert first is not None and first.email == "employee00001@example.com"
    assert last is not None and last.email == "employee10000@example.com"
    assert first.is_active is True
    assert last.is_active is True

    first.employee_code = "EMP0000A"
    session.commit()
    with pytest.raises(SeedDataConflict):
        seed_employees(session)


def test_refuses_incomplete_deterministic_employee_seed(session: Session) -> None:
    session.add(employee(1))
    session.commit()

    try:
        seed_employees(session)
    except SeedDataConflict as error:
        assert "incomplete" in str(error)
    else:
        raise AssertionError("Expected partial employee data to block deterministic seeding")


def test_repeat_seed_does_not_reactivate_an_employee(session: Session) -> None:
    seed_employees(session)
    session.commit()
    first = session.scalar(select(Employee).where(Employee.employee_code == "EMP00001"))
    assert first is not None
    first.is_active = False
    session.commit()

    assert seed_employees(session) == 0
    assert first.is_active is False


def test_seeds_all_deterministic_exchange_rates_and_is_repeatable(session: Session) -> None:
    assert seed_exchange_rates(session) == len(EXCHANGE_RATES)
    session.commit()

    assert seed_exchange_rates(session) == 0
    rates = {rate.currency_code: rate for rate in session.scalars(select(ExchangeRate))}

    assert set(rates) == set(EXCHANGE_RATES)
    assert all(rates[code].rate_to_usd == value for code, value in EXCHANGE_RATES.items())
    assert all(rate.effective_date == EXCHANGE_RATE_DATE for rate in rates.values())


def test_every_seeded_employee_currency_has_an_exchange_rate(session: Session) -> None:
    seed_exchange_rates(session)
    seed_employees(session)
    session.commit()

    employee_currencies = set(session.scalars(select(Employee.currency).distinct()))
    rate_currencies = set(session.scalars(select(ExchangeRate.currency_code)))

    assert employee_currencies == set(EXCHANGE_RATES)
    assert employee_currencies <= rate_currencies


def test_refuses_conflicting_exchange_rate_data(session: Session) -> None:
    session.add(
        ExchangeRate(
            currency_code="USD",
            rate_to_usd=Decimal("0.9900000000"),
            effective_date=EXCHANGE_RATE_DATE,
        )
    )
    session.commit()

    with pytest.raises(SeedDataConflict, match="Exchange-rate data"):
        seed_exchange_rates(session)
