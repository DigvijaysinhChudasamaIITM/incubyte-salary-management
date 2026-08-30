import pytest

from salary_management.config import cors_allowed_origins, database_url, normalize_database_url
from salary_management.persistence.database import build_engine


@pytest.mark.parametrize(
    ("provided", "expected"),
    [
        ("postgres://user:pass@host/database", "postgresql+psycopg://user:pass@host/database"),
        ("postgresql://user:pass@host/database", "postgresql+psycopg://user:pass@host/database"),
        ("postgresql+psycopg://user:pass@host/database", "postgresql+psycopg://user:pass@host/database"),
        ("sqlite:///./local.db", "sqlite:///./local.db"),
    ],
)
def test_normalizes_database_urls_for_installed_drivers(provided: str, expected: str) -> None:
    assert normalize_database_url(provided) == expected


def test_database_url_defaults_to_local_sqlite(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)

    assert database_url() == "sqlite:///./salary_management.db"


def test_engine_uses_installed_psycopg_driver_for_standard_postgresql_url() -> None:
    engine = build_engine("postgresql://user:pass@host/database")

    assert engine.dialect.name == "postgresql"
    assert engine.dialect.driver == "psycopg"
    assert engine.pool._pre_ping is True
    engine.dispose()


def test_parses_explicit_cors_origins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "CORS_ALLOWED_ORIGINS",
        "https://hr.example.com/, https://admin.example.com",
    )

    assert cors_allowed_origins() == [
        "https://hr.example.com",
        "https://admin.example.com",
    ]


def test_rejects_wildcard_cors_origin(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ALLOWED_ORIGINS", "*")

    with pytest.raises(ValueError, match="explicit origins"):
        cors_allowed_origins()
