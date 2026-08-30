from unittest.mock import Mock

from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from salary_management.main import app, create_app
from salary_management.persistence.database import get_session


def test_health_reports_api_is_available() -> None:
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_reports_database_is_available() -> None:
    response = TestClient(app).get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_readiness_returns_service_unavailable_without_leaking_database_error() -> None:
    application = create_app()
    unavailable_session = Mock()
    unavailable_session.execute.side_effect = OperationalError(
        "SELECT 1", {}, Exception("database credentials appeared here")
    )
    application.dependency_overrides[get_session] = lambda: unavailable_session

    response = TestClient(application).get("/ready")

    assert response.status_code == 503
    assert response.json() == {"detail": "Database is unavailable"}
    assert "credentials" not in response.text


def test_configured_frontend_origin_is_allowed(monkeypatch) -> None:
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "https://hr.example.com")
    application = create_app()

    response = TestClient(application).options(
        "/api/employees",
        headers={
            "Origin": "https://hr.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://hr.example.com"
