from collections.abc import Generator

from conftest import employee
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from salary_management.main import create_app
from salary_management.persistence.database import get_session


def client_for(session: Session) -> TestClient:
    app = create_app()

    def override_session() -> Generator[Session, None, None]:
        yield session

    app.dependency_overrides[get_session] = override_session
    return TestClient(app)


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
