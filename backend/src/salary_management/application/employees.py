from dataclasses import dataclass
from decimal import Decimal
from math import ceil

from salary_management.persistence.employee_repository import (
    EmployeeQuery,
    EmployeeRepository,
    EmployeeSortField,
    EmployeeStatus,
    NewEmployee,
    SortDirection,
)
from salary_management.persistence.exchange_rate_repository import ExchangeRateRepository
from salary_management.persistence.models import Employee


@dataclass(frozen=True)
class EmployeePage:
    items: list[Employee]
    page: int
    page_size: int
    total: int
    total_pages: int


class EmployeeService:
    def __init__(
        self,
        repository: EmployeeRepository,
        exchange_rates: ExchangeRateRepository | None = None,
    ) -> None:
        self.repository = repository
        self.exchange_rates = exchange_rates

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

    def create(
        self,
        *,
        employee_code: str,
        name: str,
        email: str,
        country: str,
        department: str,
        job_title: str,
        salary_amount: Decimal,
        currency: str,
    ) -> Employee:
        if self.exchange_rates is None:
            raise RuntimeError("Exchange-rate repository is required for employee creation")

        normalized_currency = currency.strip().upper()
        if self.exchange_rates.get_rate_to_usd(normalized_currency) is None:
            raise UnsupportedCurrency(normalized_currency)

        return self.repository.create(
            NewEmployee(
                employee_code=employee_code.strip().upper(),
                name=name.strip(),
                email=email.strip().lower(),
                country=country.strip().upper(),
                department=department.strip(),
                job_title=job_title.strip(),
                salary_amount=salary_amount,
                currency=normalized_currency,
            )
        )

    def update_salary(self, employee_code: str, salary_amount: Decimal) -> Employee:
        normalized_code = employee_code.strip().upper()
        employee = self.repository.find_by_code(normalized_code)
        if employee is None:
            raise EmployeeNotFound(normalized_code)
        if not employee.is_active:
            raise InactiveEmployee(normalized_code)
        return self.repository.update_salary(employee, salary_amount)

    def deactivate(self, employee_code: str) -> Employee:
        normalized_code = employee_code.strip().upper()
        employee = self.repository.find_by_code(normalized_code)
        if employee is None:
            raise EmployeeNotFound(normalized_code)
        return self.repository.deactivate(employee)


class UnsupportedCurrency(ValueError):
    code = "unsupported_currency"

    def __init__(self, currency_code: str) -> None:
        self.currency_code = currency_code
        super().__init__(self.code)


class EmployeeNotFound(LookupError):
    code = "employee_not_found"

    def __init__(self, employee_code: str) -> None:
        self.employee_code = employee_code
        super().__init__(self.code)


class InactiveEmployee(RuntimeError):
    code = "employee_inactive"

    def __init__(self, employee_code: str) -> None:
        self.employee_code = employee_code
        super().__init__(self.code)


def _clean(value: str | None, *, uppercase: bool = False) -> str | None:
    cleaned = value.strip() if value else ""
    if not cleaned:
        return None
    return cleaned.upper() if uppercase else cleaned
