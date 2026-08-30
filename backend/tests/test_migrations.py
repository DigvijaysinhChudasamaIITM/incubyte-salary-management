from pathlib import Path

from alembic.config import Config
from sqlalchemy import create_engine, inspect

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
