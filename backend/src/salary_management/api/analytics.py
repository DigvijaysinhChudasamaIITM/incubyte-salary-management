from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from salary_management.api.schemas import PayrollAnalyticsResponse, RoleAnalyticsResponse
from salary_management.application.analytics import AnalyticsService
from salary_management.application.exchange_rates import ExchangeRateUnavailable
from salary_management.persistence.analytics_repository import AnalyticsRepository
from salary_management.persistence.database import get_session

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


def _unavailable(error: ExchangeRateUnavailable) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={"code": error.code, "currency": error.currency_code},
    )


@router.get("/payroll", response_model=PayrollAnalyticsResponse)
def payroll_analytics(
    session: Annotated[Session, Depends(get_session)],
    country: Annotated[str | None, Query(min_length=2, max_length=2)] = None,
    department: Annotated[str | None, Query(max_length=80)] = None,
    job_title: Annotated[str | None, Query(max_length=100)] = None,
    include_inactive: bool = False,
) -> PayrollAnalyticsResponse:
    try:
        result = AnalyticsService(AnalyticsRepository(session)).payroll(
            country=country,
            department=department,
            job_title=job_title,
            include_inactive=include_inactive,
        )
    except ExchangeRateUnavailable as error:
        raise _unavailable(error) from None
    return PayrollAnalyticsResponse.model_validate(result, from_attributes=True)


@router.get("/roles/{job_title}", response_model=RoleAnalyticsResponse)
def role_analytics(
    job_title: Annotated[str, Path(min_length=1, max_length=100)],
    session: Annotated[Session, Depends(get_session)],
    include_inactive: bool = False,
) -> RoleAnalyticsResponse:
    try:
        result = AnalyticsService(AnalyticsRepository(session)).role(
            job_title, include_inactive=include_inactive
        )
    except ExchangeRateUnavailable as error:
        raise _unavailable(error) from None
    return RoleAnalyticsResponse.model_validate(result, from_attributes=True)
