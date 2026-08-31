from pathlib import Path

from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from alembic import command


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
