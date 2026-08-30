import pytest
from conftest import employee
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from salary_management.persistence.models import Employee
from salary_management.seed import EMPLOYEE_COUNT, SeedDataConflict, seed_employees


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

    first.employee_code = "EMP0000A"
    session.commit()
    with pytest.raises(SeedDataConflict):
        seed_employees(session)


def test_refuses_to_mix_seed_data_with_existing_employees(session: Session) -> None:
    session.add(employee(99_999))
    session.commit()

    try:
        seed_employees(session)
    except SeedDataConflict as error:
        assert "does not match" in str(error)
    else:
        raise AssertionError("Expected partial employee data to block deterministic seeding")
