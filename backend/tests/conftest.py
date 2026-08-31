from collections.abc import Generator
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from salary_management.persistence.database import Base
from salary_management.persistence.models import Employee


@pytest.fixture
def session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    with Session(engine) as database_session:
        yield database_session
    engine.dispose()


def employee(
    number: int,
    *,
    name: str | None = None,
    country: str = "US",
    department: str = "Engineering",
    job_title: str = "Engineer",
    is_active: bool = True,
) -> Employee:
    return Employee(
        employee_code=f"EMP{number:05d}",
        name=name or f"Employee {number}",
        email=f"employee{number}@example.com",
        country=country,
        department=department,
        job_title=job_title,
        salary_amount=Decimal("75000.25"),
        currency="USD",
        is_active=is_active,
    )
