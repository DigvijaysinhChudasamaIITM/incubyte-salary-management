from pathlib import Path

from alembic.config import Config
from sqlalchemy import create_engine, func, inspect, select, text
from sqlalchemy.orm import Session

from alembic import command
from salary_management.persistence.models import Employee, ExchangeRate
from salary_management.seed import seed_all, seed_employees


def test_migrations_create_employee_schema_on_fresh_database(
    tmp_path: Path, monkeypatch
) -> None:
    database_path = tmp_path / "migration.db"
    database_url = f"sqlite:///{database_path.as_posix()}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    config = Config(Path(__file__).parents[1] / "alembic.ini")

    command.upgrade(config, "head")

    inspector = inspect(create_engine(database_url))
    columns = {column["name"]: column for column in inspector.get_columns("employees")}
    indexes = {index["name"] for index in inspector.get_indexes("employees")}
    assert columns["salary_amount"]["type"].precision == 14
    assert columns["salary_amount"]["type"].scale == 2
    assert "ix_employees_employee_code" in indexes
    assert "ix_employees_country_department" in indexes
    assert columns["is_active"]["nullable"] is False
    assert "ix_employees_is_active" in indexes

    rate_columns = {
        column["name"]: column for column in inspector.get_columns("exchange_rates")
    }
    assert rate_columns["currency_code"]["nullable"] is False
    assert rate_columns["rate_to_usd"]["type"].precision == 20
    assert rate_columns["rate_to_usd"]["type"].scale == 10
    assert rate_columns["effective_date"]["nullable"] is False
    assert inspector.get_pk_constraint("exchange_rates")["constrained_columns"] == [
        "currency_code"
    ]


def test_active_status_migration_backfills_existing_employees(
    tmp_path: Path, monkeypatch
) -> None:
    database_path = tmp_path / "existing.db"
    database_url = f"sqlite:///{database_path.as_posix()}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    config = Config(Path(__file__).parents[1] / "alembic.ini")

    command.upgrade(config, "20260830_01")
    engine = create_engine(database_url)
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO employees (
                    employee_code, name, email, country, department, job_title,
                    salary_amount, currency
                ) VALUES (
                    'EMP00001', 'Existing Employee', 'existing@example.com', 'US',
                    'Engineering', 'Engineer', 75000.25, 'USD'
                )
                """
            )
        )

    command.upgrade(config, "head")

    with engine.connect() as connection:
        assert connection.scalar(text("SELECT is_active FROM employees")) == 1
        assert connection.scalar(text("SELECT COUNT(*) FROM employees")) == 1
    engine.dispose()


def test_production_rollout_adds_rates_to_existing_complete_employee_seed(
    tmp_path: Path, monkeypatch
) -> None:
    database_path = tmp_path / "production-rollout.db"
    database_url = f"sqlite:///{database_path.as_posix()}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    config = Config(Path(__file__).parents[1] / "alembic.ini")

    command.upgrade(config, "20260831_02")
    engine = create_engine(database_url)
    with Session(engine) as session:
        assert seed_employees(session) == 10_000
        session.commit()

    command.upgrade(config, "20260831_03")
    with Session(engine) as session:
        assert session.scalar(select(func.count()).select_from(ExchangeRate)) == 0

        assert seed_all(session) == (0, 5)
        session.commit()
        assert session.scalar(select(func.count()).select_from(Employee)) == 10_000
        assert session.scalar(select(func.count()).select_from(ExchangeRate)) == 5

        assert seed_all(session) == (0, 0)

    engine.dispose()
