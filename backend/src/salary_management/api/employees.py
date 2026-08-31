from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from salary_management.api.schemas import (
    EmployeeCreateRequest,
    EmployeePageResponse,
    EmployeeResponse,
)
from salary_management.application.employees import EmployeeService, UnsupportedCurrency
from salary_management.persistence.database import get_session
from salary_management.persistence.employee_repository import (
    EmployeeConflict,
    EmployeeRepository,
    EmployeeSortField,
    EmployeeStatus,
    SortDirection,
)
from salary_management.persistence.exchange_rate_repository import ExchangeRateRepository

router = APIRouter(prefix="/api/employees", tags=["employees"])


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(
    request: EmployeeCreateRequest,
    session: Annotated[Session, Depends(get_session)],
) -> EmployeeResponse:
    try:
        employee = EmployeeService(
            EmployeeRepository(session), ExchangeRateRepository(session)
        ).create(**request.model_dump())
    except EmployeeConflict as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": "employee_conflict", "fields": error.fields},
        ) from None
    except UnsupportedCurrency as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={"code": error.code, "currency": error.currency_code},
        ) from None
    return EmployeeResponse.model_validate(employee, from_attributes=True)


@router.get("", response_model=EmployeePageResponse)
def list_employees(
    session: Annotated[Session, Depends(get_session)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 25,
    search: Annotated[str | None, Query(max_length=120)] = None,
    country: Annotated[str | None, Query(min_length=2, max_length=2)] = None,
    department: Annotated[str | None, Query(max_length=80)] = None,
    sort_by: EmployeeSortField = "employee_code",
    sort_direction: SortDirection = "asc",
    status: EmployeeStatus = "active",
) -> EmployeePageResponse:
    result = EmployeeService(EmployeeRepository(session)).browse(
        page=page,
        page_size=page_size,
        search=search,
        country=country,
        department=department,
        sort_by=sort_by,
        sort_direction=sort_direction,
        status=status,
    )
    return EmployeePageResponse.model_validate(result, from_attributes=True)
