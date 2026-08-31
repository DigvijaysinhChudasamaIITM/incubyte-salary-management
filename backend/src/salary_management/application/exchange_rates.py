from decimal import Decimal

from salary_management.persistence.exchange_rate_repository import ExchangeRateRepository


class ExchangeRateUnavailable(RuntimeError):
    code = "exchange_rate_unavailable"

    def __init__(self, currency_code: str) -> None:
        self.currency_code = currency_code
        super().__init__(self.code)


def supported_currency_codes(repository: ExchangeRateRepository) -> list[str]:
    return repository.list_currency_codes()


def normalize_salary_to_usd(
    native_salary: Decimal,
    currency_code: str,
    repository: ExchangeRateRepository,
) -> Decimal:
    if not isinstance(native_salary, Decimal):
        raise TypeError("native_salary must be a Decimal")

    normalized_currency = currency_code.upper()
    rate_to_usd = repository.get_rate_to_usd(normalized_currency)
    if rate_to_usd is None:
        raise ExchangeRateUnavailable(currency_code.upper())
    return native_salary * rate_to_usd
