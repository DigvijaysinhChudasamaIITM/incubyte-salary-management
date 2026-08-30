from dataclasses import dataclass

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from salary_management.persistence.models import Employee


@dataclass(frozen=True)
class EmployeeQuery:
    page: int
    page_size: int
    search: str | None = None
    country: str | None = None
    department: str | None = None


class EmployeeRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list(self, query: EmployeeQuery) -> tuple[list[Employee], int]:
        filters = []
        if query.search:
            search = query.search.lower()
            filters.append(
                or_(
                    func.lower(Employee.employee_code).contains(search, autoescape=True),
                    func.lower(Employee.name).contains(search, autoescape=True),
                    func.lower(Employee.email).contains(search, autoescape=True),
                )
            )
        if query.country:
            filters.append(Employee.country == query.country)
        if query.department:
            filters.append(Employee.department == query.department)

        total = self.session.scalar(select(func.count()).select_from(Employee).where(*filters))
        statement = (
            select(Employee)
            .where(*filters)
            .order_by(Employee.employee_code)
            .offset((query.page - 1) * query.page_size)
            .limit(query.page_size)
        )
        return list(self.session.scalars(statement)), total or 0
