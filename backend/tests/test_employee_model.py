from decimal import Decimal

import pytest
from conftest import employee
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


@pytest.mark.parametrize("salary", [Decimal("0.00"), Decimal("-1.00")])
def test_database_rejects_non_positive_salary(session: Session, salary: Decimal) -> None:
    record = employee(1)
    record.salary_amount = salary
    session.add(record)

    with pytest.raises(IntegrityError):
        session.commit()


def test_database_rejects_duplicate_employee_codes(session: Session) -> None:
    first = employee(1)
    duplicate = employee(2)
    duplicate.employee_code = first.employee_code
    session.add_all([first, duplicate])

    with pytest.raises(IntegrityError):
        session.commit()


def test_salary_round_trips_as_decimal(session: Session) -> None:
    record = employee(1)
    session.add(record)
    session.commit()
    session.refresh(record)

    assert record.salary_amount == Decimal("75000.25")
    assert isinstance(record.salary_amount, Decimal)
