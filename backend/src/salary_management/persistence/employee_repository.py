from dataclasses import dataclass
from typing import Literal

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.orm import Session

from salary_management.persistence.models import Employee

EmployeeSortField = Literal["employee_code", "name", "country", "department", "job_title"]
SortDirection = Literal["asc", "desc"]
EmployeeStatus = Literal["active", "inactive", "all"]


@dataclass(frozen=True)
class EmployeeQuery:
    page: int
    page_size: int
    search: str | None = None
    country: str | None = None
    department: str | None = None
    sort_by: EmployeeSortField = "employee_code"
    sort_direction: SortDirection = "asc"
    status: EmployeeStatus = "active"


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
        if query.status == "active":
            filters.append(Employee.is_active.is_(True))
        elif query.status == "inactive":
            filters.append(Employee.is_active.is_(False))

        sort_columns = {
            "employee_code": Employee.employee_code,
            "name": Employee.name,
            "country": Employee.country,
            "department": Employee.department,
            "job_title": Employee.job_title,
        }
        direction = asc if query.sort_direction == "asc" else desc
        order_by = [direction(sort_columns[query.sort_by])]
        if query.sort_by != "employee_code":
            order_by.append(Employee.employee_code.asc())

        total = self.session.scalar(select(func.count()).select_from(Employee).where(*filters))
        statement = (
            select(Employee)
            .where(*filters)
            .order_by(*order_by)
            .offset((query.page - 1) * query.page_size)
            .limit(query.page_size)
        )
        return list(self.session.scalars(statement)), total or 0
