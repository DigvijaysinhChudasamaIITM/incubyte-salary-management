from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from salary_management.application.exchange_rates import ExchangeRateUnavailable
from salary_management.persistence.analytics_repository import (
    AnalyticsQuery,
    AnalyticsRepository,
    CompensationRecord,
)

REPORTING_CURRENCY = "USD"
DISPLAY_QUANTUM = Decimal("0.01")


@dataclass(frozen=True)
class AnalyticsFilters:
    country: str | None
    department: str | None
    job_title: str | None
    include_inactive: bool


@dataclass(frozen=True)
class PayrollGroup:
    name: str
    employee_count: int
    total_payroll: Decimal
    average_salary: Decimal
    median_salary: Decimal
    calculation_total: Decimal
    calculation_median: Decimal


@dataclass(frozen=True)
class PayrollAnalytics:
    reporting_currency: str
    employee_count: int
    total_payroll: Decimal
    filters: AnalyticsFilters
    department_breakdown: list[PayrollGroup]
    country_breakdown: list[PayrollGroup]
    highest_payroll_departments: list[PayrollGroup]
    lowest_payroll_departments: list[PayrollGroup]
    highest_payroll_countries: list[PayrollGroup]
    lowest_payroll_countries: list[PayrollGroup]
    highest_median_departments: list[PayrollGroup]
    lowest_median_departments: list[PayrollGroup]
    highest_median_countries: list[PayrollGroup]
    lowest_median_countries: list[PayrollGroup]


@dataclass(frozen=True)
class RoleCountryStatistics:
    country: str
    employee_count: int
    average_salary: Decimal
    median_salary: Decimal


@dataclass(frozen=True)
class RoleAnalytics:
    reporting_currency: str
    job_title: str
    employee_count: int
    include_inactive: bool
    countries: list[RoleCountryStatistics]


class AnalyticsService:
    def __init__(self, repository: AnalyticsRepository) -> None:
        self.repository = repository

    def payroll(
        self,
        *,
        country: str | None = None,
        department: str | None = None,
        job_title: str | None = None,
        include_inactive: bool = False,
    ) -> PayrollAnalytics:
        filters = AnalyticsFilters(
            country=_clean(country, uppercase=True),
            department=_clean(department),
            job_title=_clean(job_title),
            include_inactive=include_inactive,
        )
        records = self.repository.list_compensation(AnalyticsQuery(**vars(filters)))
        normalized = _normalize(records)
        departments = _group(normalized, "department")
        countries = _group(normalized, "country")
        return PayrollAnalytics(
            reporting_currency=REPORTING_CURRENCY,
            employee_count=len(records),
            total_payroll=_money(sum((amount for _, amount in normalized), Decimal(0))),
            filters=filters,
            department_breakdown=departments,
            country_breakdown=countries,
            highest_payroll_departments=_extrema(departments, "calculation_total", True),
            lowest_payroll_departments=_extrema(departments, "calculation_total", False),
            highest_payroll_countries=_extrema(countries, "calculation_total", True),
            lowest_payroll_countries=_extrema(countries, "calculation_total", False),
            highest_median_departments=_extrema(departments, "calculation_median", True),
            lowest_median_departments=_extrema(departments, "calculation_median", False),
            highest_median_countries=_extrema(countries, "calculation_median", True),
            lowest_median_countries=_extrema(countries, "calculation_median", False),
        )

    def role(self, job_title: str, *, include_inactive: bool = False) -> RoleAnalytics:
        cleaned_title = _clean(job_title)
        if cleaned_title is None:
            return RoleAnalytics(REPORTING_CURRENCY, "", 0, include_inactive, [])
        records = self.repository.list_compensation(
            AnalyticsQuery(job_title=cleaned_title, include_inactive=include_inactive)
        )
        normalized = _normalize(records)
        by_country: dict[str, list[Decimal]] = {}
        for record, amount in normalized:
            by_country.setdefault(record.country, []).append(amount)
        countries = []
        for country in sorted(by_country):
            values = sorted(by_country[country])
            total = sum(values, Decimal(0))
            countries.append(
                RoleCountryStatistics(
                    country=country,
                    employee_count=len(values),
                    average_salary=_money(total / Decimal(len(values))),
                    median_salary=_money(_median(values)),
                )
            )
        return RoleAnalytics(
            reporting_currency=REPORTING_CURRENCY,
            job_title=cleaned_title or "",
            employee_count=len(records),
            include_inactive=include_inactive,
            countries=countries,
        )


def _normalize(records: list[CompensationRecord]) -> list[tuple[CompensationRecord, Decimal]]:
    result = []
    for record in records:
        if record.rate_to_usd is None:
            raise ExchangeRateUnavailable(record.currency)
        result.append((record, record.salary_amount * record.rate_to_usd))
    return result


def _group(
    normalized: list[tuple[CompensationRecord, Decimal]], attribute: str
) -> list[PayrollGroup]:
    values_by_group: dict[str, list[Decimal]] = {}
    for record, amount in normalized:
        name = getattr(record, attribute)
        values_by_group.setdefault(name, []).append(amount)
    groups = []
    for name, unsorted_values in sorted(values_by_group.items()):
        values = sorted(unsorted_values)
        total = sum(values, Decimal(0))
        median = _median(values)
        groups.append(
            PayrollGroup(
                name=name,
                employee_count=len(values),
                total_payroll=_money(total),
                average_salary=_money(total / Decimal(len(values))),
                median_salary=_money(median),
                calculation_total=total,
                calculation_median=median,
            )
        )
    return groups


def _extrema(
    groups: list[PayrollGroup], attribute: str, highest: bool
) -> list[PayrollGroup]:
    if not groups:
        return []
    target = (max if highest else min)(getattr(group, attribute) for group in groups)
    return [group for group in groups if getattr(group, attribute) == target]


def _median(values: list[Decimal]) -> Decimal:
    midpoint = len(values) // 2
    if len(values) % 2:
        return values[midpoint]
    return (values[midpoint - 1] + values[midpoint]) / Decimal(2)


def _money(value: Decimal) -> Decimal:
    return value.quantize(DISPLAY_QUANTUM, rounding=ROUND_HALF_UP)


def _clean(value: str | None, *, uppercase: bool = False) -> str | None:
    cleaned = value.strip() if value else ""
    if not cleaned:
        return None
    return cleaned.upper() if uppercase else cleaned
