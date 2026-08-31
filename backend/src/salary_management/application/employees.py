from dataclasses import dataclass
from math import ceil

from salary_management.persistence.employee_repository import (
    EmployeeQuery,
    EmployeeRepository,
    EmployeeSortField,
    EmployeeStatus,
    SortDirection,
)
from salary_management.persistence.models import Employee


@dataclass(frozen=True)
class EmployeePage:
    items: list[Employee]
    page: int
    page_size: int
    total: int
    total_pages: int


class EmployeeService:
    def __init__(self, repository: EmployeeRepository) -> None:
        self.repository = repository

    def browse(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None = None,
        country: str | None = None,
        department: str | None = None,
        sort_by: EmployeeSortField = "employee_code",
        sort_direction: SortDirection = "asc",
        status: EmployeeStatus = "active",
    ) -> EmployeePage:
        query = EmployeeQuery(
            page=page,
            page_size=page_size,
            search=_clean(search),
            country=_clean(country, uppercase=True),
            department=_clean(department),
            sort_by=sort_by,
            sort_direction=sort_direction,
            status=status,
        )
        items, total = self.repository.list(query)
        return EmployeePage(
            items=items,
            page=page,
            page_size=page_size,
            total=total,
            total_pages=ceil(total / page_size),
        )


def _clean(value: str | None, *, uppercase: bool = False) -> str | None:
    cleaned = value.strip() if value else ""
    if not cleaned:
        return None
    return cleaned.upper() if uppercase else cleaned
