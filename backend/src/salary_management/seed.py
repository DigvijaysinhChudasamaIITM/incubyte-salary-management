from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from salary_management.persistence.database import SessionLocal
from salary_management.persistence.models import Employee, ExchangeRate

EMPLOYEE_COUNT = 10_000
EXCHANGE_RATE_DATE = date(2026, 8, 31)
EXCHANGE_RATES = {
    "USD": Decimal("1.0000000000"),
    "INR": Decimal("0.0120000000"),
    "GBP": Decimal("1.2500000000"),
    "EUR": Decimal("1.1000000000"),
    "CAD": Decimal("0.7400000000"),
}

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


def seed_exchange_rates(session: Session) -> int:
    existing = {rate.currency_code: rate for rate in session.scalars(select(ExchangeRate))}
    if existing:
        matches = len(existing) == len(EXCHANGE_RATES) and all(
            code in existing
            and existing[code].rate_to_usd == rate
            and existing[code].effective_date == EXCHANGE_RATE_DATE
            for code, rate in EXCHANGE_RATES.items()
        )
        if matches:
            return 0
        raise SeedDataConflict(
            "Exchange-rate data already exists but does not match the deterministic seed set."
        )

    session.add_all(
        ExchangeRate(
            currency_code=currency_code,
            rate_to_usd=rate_to_usd,
            effective_date=EXCHANGE_RATE_DATE,
        )
        for currency_code, rate_to_usd in EXCHANGE_RATES.items()
    )
    return len(EXCHANGE_RATES)


def seed_employees(session: Session) -> int:
    existing_codes = set(session.scalars(select(Employee.employee_code)))
    expected_codes = {
        f"EMP{number:05d}" for number in range(1, EMPLOYEE_COUNT + 1)
    }
    present_seed_codes = existing_codes & expected_codes

    if present_seed_codes == expected_codes:
        return 0
    if present_seed_codes:
        raise SeedDataConflict(
            "Employee data contains an incomplete deterministic seed set."
        )

    session.add_all(_employee(number) for number in range(1, EMPLOYEE_COUNT + 1))
    return EMPLOYEE_COUNT


def seed_all(session: Session) -> tuple[int, int]:
    rates_inserted = seed_exchange_rates(session)
    employees_inserted = seed_employees(session)
    return employees_inserted, rates_inserted


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
        employees_inserted, rates_inserted = seed_all(session)
    print(
        f"Seed complete: {employees_inserted} employees inserted, "
        f"{EMPLOYEE_COUNT} expected total; {rates_inserted} exchange rates inserted, "
        f"{len(EXCHANGE_RATES)} expected total."
    )


if __name__ == "__main__":
    main()
