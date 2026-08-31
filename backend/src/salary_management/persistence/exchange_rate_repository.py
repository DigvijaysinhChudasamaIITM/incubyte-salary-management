from decimal import Decimal

from sqlalchemy.orm import Session

from salary_management.persistence.models import ExchangeRate


class ExchangeRateRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_rate_to_usd(self, currency_code: str) -> Decimal | None:
        rate = self.session.get(ExchangeRate, currency_code)
        return rate.rate_to_usd if rate is not None else None
