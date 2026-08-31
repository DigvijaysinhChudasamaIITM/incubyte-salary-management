from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from salary_management.persistence.database import SessionLocal
from salary_management.persistence.models import Employee

EMPLOYEE_COUNT = 10_000

COUNTRIES = (
    ("US", "USD"),
    ("IN", "INR"),
    ("GB", "GBP"),
    ("DE", "EUR"),
    ("CA", "CAD"),
)
DEPARTMENTS = ("Engineering", "Finance", "People", "Sales", "Operations")
JOB_TITLES = ("Associate", "Specialist", "Manager", "Senior Manager", "Director")
FIRST_NAMES = ("Aarav", "Emma", "Liam", "Maya", "Noah", "Sofia", "Ethan", "Isha")
LAST_NAMES = ("Patel", "Smith", "Brown", "Shah", "Miller", "Wilson", "Kumar", "Taylor")


class SeedDataConflict(RuntimeError):
    pass


def seed_employees(session: Session) -> int:
    existing_codes = list(
        session.scalars(select(Employee.employee_code).order_by(Employee.employee_code))
    )
    expected_codes = (f"EMP{number:05d}" for number in range(1, EMPLOYEE_COUNT + 1))

    if len(existing_codes) == EMPLOYEE_COUNT and all(
        actual == expected for actual, expected in zip(existing_codes, expected_codes, strict=True)
    ):
        return 0
    if existing_codes:
        raise SeedDataConflict(
            "Employee data already exists but does not match the complete deterministic seed set."
        )

    session.add_all(_employee(number) for number in range(1, EMPLOYEE_COUNT + 1))
    return EMPLOYEE_COUNT


def _employee(number: int) -> Employee:
    country, currency = COUNTRIES[(number - 1) % len(COUNTRIES)]
    department_index = ((number - 1) // len(COUNTRIES)) % len(DEPARTMENTS)
    title_index = ((number - 1) // (len(COUNTRIES) * len(DEPARTMENTS))) % len(JOB_TITLES)
    first_name = FIRST_NAMES[(number - 1) % len(FIRST_NAMES)]
    last_name = LAST_NAMES[((number - 1) // len(FIRST_NAMES)) % len(LAST_NAMES)]
    salary = Decimal("30000.00") + Decimal((number * 137) % 170_000)

    return Employee(
        employee_code=f"EMP{number:05d}",
        name=f"{first_name} {last_name} {number:05d}",
        email=f"employee{number:05d}@example.com",
        country=country,
        department=DEPARTMENTS[department_index],
        job_title=JOB_TITLES[title_index],
        salary_amount=salary,
        currency=currency,
        is_active=True,
    )


def main() -> None:
    with SessionLocal.begin() as session:
        inserted = seed_employees(session)
    print(f"Employee seed complete: {inserted} inserted, {EMPLOYEE_COUNT} expected total.")


if __name__ == "__main__":
    main()
