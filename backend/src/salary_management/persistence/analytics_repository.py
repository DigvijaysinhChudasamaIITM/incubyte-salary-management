from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from salary_management.persistence.models import Employee, ExchangeRate


@dataclass(frozen=True)
class AnalyticsQuery:
    include_inactive: bool = False
    country: str | None = None
    department: str | None = None
    job_title: str | None = None


@dataclass(frozen=True)
class CompensationRecord:
    employee_code: str
    country: str
    department: str
    job_title: str
    salary_amount: Decimal
    currency: str
    rate_to_usd: Decimal | None


class AnalyticsRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_compensation(self, query: AnalyticsQuery) -> list[CompensationRecord]:
        filters = []
        if not query.include_inactive:
            filters.append(Employee.is_active.is_(True))
        if query.country:
            filters.append(Employee.country == query.country)
        if query.department:
            filters.append(Employee.department == query.department)
        if query.job_title:
            filters.append(func.lower(Employee.job_title) == query.job_title.lower())

        statement = (
            select(
                Employee.employee_code,
                Employee.country,
                Employee.department,
                Employee.job_title,
                Employee.salary_amount,
                Employee.currency,
                ExchangeRate.rate_to_usd,
            )
            .outerjoin(ExchangeRate, ExchangeRate.currency_code == Employee.currency)
            .where(*filters)
            .order_by(Employee.employee_code)
        )
        return [CompensationRecord(*row) for row in self.session.execute(statement)]
