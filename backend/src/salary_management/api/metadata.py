from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from salary_management.api.schemas import SupportedCurrenciesResponse
from salary_management.application.exchange_rates import supported_currency_codes
from salary_management.persistence.database import get_session
from salary_management.persistence.exchange_rate_repository import ExchangeRateRepository

router = APIRouter(prefix="/api/metadata", tags=["metadata"])


@router.get("/currencies", response_model=SupportedCurrenciesResponse)
def list_supported_currencies(
    session: Annotated[Session, Depends(get_session)],
) -> SupportedCurrenciesResponse:
    currencies = supported_currency_codes(ExchangeRateRepository(session))
    return SupportedCurrenciesResponse(currencies=currencies)
