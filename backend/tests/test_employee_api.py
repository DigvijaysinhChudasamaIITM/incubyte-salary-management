from collections.abc import Generator

import pytest
from conftest import employee
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from salary_management.main import create_app
from salary_management.persistence.database import get_session
from salary_management.persistence.employee_repository import EmployeeRepository
from salary_management.persistence.models import Employee
from salary_management.seed import seed_exchange_rates


def client_for(session: Session) -> TestClient:
    app = create_app()

    def override_session() -> Generator[Session, None, None]:
        yield session

    app.dependency_overrides[get_session] = override_session
    return TestClient(app)


def create_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "employee_code": "new00001",
        "name": "New Employee",
        "email": "NEW.EMPLOYEE@example.com",
        "country": "in",
        "department": "Engineering",
        "job_title": "Engineer",
        "salary_amount": "12345.67",
        "currency": "inr",
    }
    payload.update(overrides)
    return payload


def test_returns_paginated_employee_salary_data(session: Session) -> None:
    session.add_all(employee(number) for number in range(1, 4))
    session.commit()

    response = client_for(session).get("/api/employees?page=2&page_size=2")

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "employee_code": "EMP00003",
                "name": "Employee 3",
                "email": "employee3@example.com",
                "country": "US",
                "department": "Engineering",
                "job_title": "Engineer",
                "salary_amount": "75000.25",
                "currency": "USD",
                "is_active": True,
            }
        ],
        "page": 2,
        "page_size": 2,
        "total": 3,
        "total_pages": 2,
    }


def test_search_and_filters_are_applied_by_the_api(session: Session) -> None:
    session.add_all(
        [
            employee(1, name="Asha Patel", country="IN", department="Engineering"),
            employee(2, name="Asha Shah", country="IN", department="Finance"),
            employee(3, name="Asha Brown", country="US", department="Engineering"),
        ]
    )
    session.commit()

    response = client_for(session).get(
        "/api/employees?search=asha&country=in&department=Engineering"
    )

    assert response.status_code == 200
    assert [item["employee_code"] for item in response.json()["items"]] == ["EMP00001"]
    assert response.json()["total"] == 1


def test_rejects_invalid_pagination(session: Session) -> None:
    response = client_for(session).get("/api/employees?page=0&page_size=101")

    assert response.status_code == 422


def test_applies_sorting_and_status_query_parameters(session: Session) -> None:
    session.add_all(
        [
            employee(1, name="Morgan", is_active=False),
            employee(2, name="Asha"),
            employee(3, name="Zara"),
        ]
    )
    session.commit()

    response = client_for(session).get(
        "/api/employees?status=all&sort_by=name&sort_direction=desc"
    )

    assert response.status_code == 200
    assert [item["employee_code"] for item in response.json()["items"]] == [
        "EMP00003",
        "EMP00001",
        "EMP00002",
    ]
    assert response.json()["items"][1]["is_active"] is False


def test_rejects_unsupported_sorting_and_status_values(session: Session) -> None:
    client = client_for(session)

    assert client.get("/api/employees?sort_by=email").status_code == 422
    assert client.get("/api/employees?sort_direction=sideways").status_code == 422
    assert client.get("/api/employees?status=deleted").status_code == 422


def test_creates_active_employee_with_exact_decimal_and_normalized_codes(
    session: Session,
) -> None:
    seed_exchange_rates(session)
    session.commit()
    client = client_for(session)

    response = client.post("/api/employees", json=create_payload())

    assert response.status_code == 201
    assert response.json() == {
        "employee_code": "NEW00001",
        "name": "New Employee",
        "email": "new.employee@example.com",
        "country": "IN",
        "department": "Engineering",
        "job_title": "Engineer",
        "salary_amount": "12345.67",
        "currency": "INR",
        "is_active": True,
    }
    created = session.get(Employee, 1)
    assert created is not None
    assert str(created.salary_amount) == "12345.67"

    listing = client.get("/api/employees?search=NEW00001")
    assert listing.status_code == 200
    assert listing.json()["total"] == 1
    assert listing.json()["items"][0]["employee_code"] == "NEW00001"


@pytest.mark.parametrize(
    ("existing_field", "request_value"),
    [("employee_code", "EMP00001"), ("email", "employee1@example.com")],
)
def test_duplicate_employee_code_or_email_returns_structured_conflict(
    session: Session, existing_field: str, request_value: str
) -> None:
    existing = employee(1)
    session.add(existing)
    seed_exchange_rates(session)
    session.commit()
    before = client_for(session).get("/api/employees?status=all").json()["total"]

    response = client_for(session).post(
        "/api/employees", json=create_payload(**{existing_field: request_value})
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": {"code": "employee_conflict", "fields": [existing_field]}
    }
    assert client_for(session).get("/api/employees?status=all").json()["total"] == before


def test_duplicate_against_inactive_employee_still_conflicts(session: Session) -> None:
    session.add(employee(1, is_active=False))
    seed_exchange_rates(session)
    session.commit()

    response = client_for(session).post(
        "/api/employees", json=create_payload(employee_code="EMP00001")
    )

    assert response.status_code == 409
    assert response.json()["detail"] == {
        "code": "employee_conflict",
        "fields": ["employee_code"],
    }


def test_unsupported_currency_returns_structured_validation_error(session: Session) -> None:
    seed_exchange_rates(session)
    session.commit()

    response = client_for(session).post(
        "/api/employees", json=create_payload(currency="jpy")
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": {"code": "unsupported_currency", "currency": "JPY"}
    }


@pytest.mark.parametrize("salary", ["0.00", "-1.00"])
def test_rejects_non_positive_salary(session: Session, salary: str) -> None:
    response = client_for(session).post(
        "/api/employees", json=create_payload(salary_amount=salary)
    )

    assert response.status_code == 422


@pytest.mark.parametrize(
    "overrides",
    [{"email": "not-an-email"}, {"country": "India"}, {"name": "   "}],
)
def test_rejects_malformed_employee_input(
    session: Session, overrides: dict[str, object]
) -> None:
    response = client_for(session).post("/api/employees", json=create_payload(**overrides))

    assert response.status_code == 422


def test_lists_supported_currencies_without_exposing_rates(session: Session) -> None:
    seed_exchange_rates(session)
    session.commit()

    response = client_for(session).get("/api/metadata/currencies")

    assert response.status_code == 200
    assert response.json() == {"currencies": ["CAD", "EUR", "GBP", "INR", "USD"]}


@pytest.mark.parametrize("conflict_field", ["employee_code", "email"])
def test_commit_time_unique_constraint_failure_returns_structured_conflict(
    session: Session, monkeypatch, conflict_field: str
) -> None:
    seed_exchange_rates(session)
    session.commit()
    conflict_checks = iter([[], [conflict_field]])
    monkeypatch.setattr(
        EmployeeRepository,
        "_conflicting_fields",
        lambda self, employee_code, email: next(conflict_checks),
    )

    def raise_unique_constraint() -> None:
        raise IntegrityError("INSERT INTO employees", {}, RuntimeError("unique constraint"))

    monkeypatch.setattr(session, "commit", raise_unique_constraint)

    response = client_for(session).post("/api/employees", json=create_payload())

    assert response.status_code == 409
    assert response.json() == {
        "detail": {"code": "employee_conflict", "fields": [conflict_field]}
    }
