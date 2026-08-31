from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.exc import IntegrityError
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


@dataclass(frozen=True)
class NewEmployee:
    employee_code: str
    name: str
    email: str
    country: str
    department: str
    job_title: str
    salary_amount: Decimal
    currency: str


class EmployeeConflict(RuntimeError):
    def __init__(self, fields: list[str]) -> None:
        self.fields = fields
        super().__init__("employee_conflict")


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

    def create(self, new_employee: NewEmployee) -> Employee:
        conflicts = self._conflicting_fields(new_employee.employee_code, new_employee.email)
        if conflicts:
            raise EmployeeConflict(conflicts)

        employee = Employee(**vars(new_employee), is_active=True)
        self.session.add(employee)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            conflicts = self._conflicting_fields(new_employee.employee_code, new_employee.email)
            raise EmployeeConflict(conflicts or ["employee_code", "email"]) from None
        self.session.refresh(employee)
        return employee

    def find_by_code(self, employee_code: str) -> Employee | None:
        statement = select(Employee).where(Employee.employee_code == employee_code)
        return self.session.scalar(statement)

    def update_salary(self, employee: Employee, salary_amount: Decimal) -> Employee:
        employee.salary_amount = salary_amount
        self.session.commit()
        self.session.refresh(employee)
        return employee

    def deactivate(self, employee: Employee) -> Employee:
        if employee.is_active:
            employee.is_active = False
            self.session.commit()
            self.session.refresh(employee)
        return employee

    def _conflicting_fields(self, employee_code: str, email: str) -> list[str]:
        statement = select(Employee.employee_code, Employee.email).where(
            or_(Employee.employee_code == employee_code, Employee.email == email)
        )
        existing = self.session.execute(statement).all()
        conflicts: list[str] = []
        if any(code == employee_code for code, _ in existing):
            conflicts.append("employee_code")
        if any(existing_email == email for _, existing_email in existing):
            conflicts.append("email")
        return conflicts
