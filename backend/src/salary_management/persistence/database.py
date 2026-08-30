import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    pass


def database_url() -> str:
    return os.getenv("DATABASE_URL", "sqlite:///./salary_management.db")


def build_engine(url: str | None = None):
    resolved_url = url or database_url()
    connect_args = {"check_same_thread": False} if resolved_url.startswith("sqlite") else {}
    return create_engine(resolved_url, connect_args=connect_args)


engine = build_engine()
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
