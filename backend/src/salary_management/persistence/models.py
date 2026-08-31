from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, Index, Numeric, String, true
from sqlalchemy.orm import Mapped, mapped_column

from salary_management.persistence.database import Base


class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = (
        CheckConstraint("salary_amount > 0", name="ck_employees_salary_positive"),
        CheckConstraint("length(currency) = 3", name="ck_employees_currency_length"),
        Index("ix_employees_name", "name"),
        Index("ix_employees_country_department", "country", "department"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    country: Mapped[str] = mapped_column(String(2), index=True)
    department: Mapped[str] = mapped_column(String(80), index=True)
    job_title: Mapped[str] = mapped_column(String(100))
    salary_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    currency: Mapped[str] = mapped_column(String(3))
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=true(), index=True
    )
