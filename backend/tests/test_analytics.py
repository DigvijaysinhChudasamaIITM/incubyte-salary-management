from collections.abc import Generator
from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from salary_management.application.analytics import AnalyticsService
from salary_management.application.exchange_rates import ExchangeRateUnavailable
from salary_management.main import create_app
from salary_management.persistence.analytics_repository import AnalyticsRepository
from salary_management.persistence.database import get_session
from salary_management.persistence.models import Employee, ExchangeRate


def add_rate(session: Session, currency: str, rate: str) -> None:
    session.add(
        ExchangeRate(
            currency_code=currency,
            rate_to_usd=Decimal(rate),
            effective_date=date(2026, 1, 1),
        )
    )


def add_employee(
    session: Session,
    number: int,
    *,
    salary: str,
    currency: str = "USD",
    country: str = "US",
    department: str = "Engineering",
    job_title: str = "Engineer",
    active: bool = True,
) -> None:
    session.add(
        Employee(
            employee_code=f"EMP{number:05d}",
            name=f"Employee {number}",
            email=f"employee{number}@example.com",
            country=country,
            department=department,
            job_title=job_title,
            salary_amount=Decimal(salary),
            currency=currency,
            is_active=active,
        )
    )


def client_for(session: Session) -> TestClient:
    app = create_app()

    def override_session() -> Generator[Session, None, None]:
        yield session

    app.dependency_overrides[get_session] = override_session
    return TestClient(app)


def test_payroll_normalizes_currencies_and_builds_breakdowns(session: Session) -> None:
    add_rate(session, "USD", "1")
    add_rate(session, "INR", "0.012")
    add_rate(session, "GBP", "1.25")
    add_employee(session, 1, salary="100.00", department="Engineering")
    add_employee(session, 2, salary="1000.00", currency="INR", country="IN", department="Finance")
    add_employee(session, 3, salary="80.00", currency="GBP", country="GB", department="Engineering")
    session.commit()

    result = AnalyticsService(AnalyticsRepository(session)).payroll()

    assert result.employee_count == 3
    assert result.total_payroll == Decimal("212.00")
    breakdown = [
        (group.name, group.employee_count, group.total_payroll)
        for group in result.department_breakdown
    ]
    assert breakdown == [
        ("Engineering", 2, Decimal("200.00")),
        ("Finance", 1, Decimal("12.00")),
    ]
    assert [group.name for group in result.country_breakdown] == ["GB", "IN", "US"]
    assert [group.name for group in result.highest_payroll_departments] == ["Engineering"]
    assert [group.name for group in result.lowest_payroll_departments] == ["Finance"]


def test_payroll_excludes_inactive_by_default_and_can_include_it(session: Session) -> None:
    add_rate(session, "USD", "1")
    add_employee(session, 1, salary="100.00")
    add_employee(session, 2, salary="50.00", active=False)
    session.commit()

    active = AnalyticsService(AnalyticsRepository(session)).payroll()
    all_employees = AnalyticsService(AnalyticsRepository(session)).payroll(include_inactive=True)

    assert (active.employee_count, active.total_payroll) == (1, Decimal("100.00"))
    assert (all_employees.employee_count, all_employees.total_payroll) == (2, Decimal("150.00"))


def test_payroll_filters_and_returns_zero_statistics_for_no_match(session: Session) -> None:
    add_rate(session, "USD", "1")
    add_employee(session, 1, salary="100.00", country="US", department="Engineering")
    session.commit()

    result = AnalyticsService(AnalyticsRepository(session)).payroll(
        country=" in ", department="Engineering"
    )

    assert result.employee_count == 0
    assert result.total_payroll == Decimal("0.00")
    assert result.department_breakdown == []
    assert result.highest_payroll_departments == []
    assert result.highest_median_departments == []
    assert result.filters.country == "IN"


def test_payroll_filter_normalization_matches_directory_conventions(session: Session) -> None:
    add_rate(session, "USD", "1")
    add_employee(session, 1, salary="100", country="IN", department="Engineering")
    session.commit()

    service = AnalyticsService(AnalyticsRepository(session))

    matching = service.payroll(
        country=" in ", department=" Engineering ", job_title=" engineer "
    )
    assert matching.employee_count == 1
    assert service.payroll(department=" engineering ").employee_count == 0


def test_extrema_preserve_all_ties_in_name_order(session: Session) -> None:
    add_rate(session, "USD", "1")
    add_employee(session, 1, salary="100", country="US", department="A")
    add_employee(session, 2, salary="100", country="IN", department="B")
    add_employee(session, 3, salary="200", country="GB", department="C")
    session.commit()

    result = AnalyticsService(AnalyticsRepository(session)).payroll()

    assert [group.name for group in result.lowest_payroll_departments] == ["A", "B"]
    assert [group.name for group in result.lowest_median_countries] == ["IN", "US"]
    assert [group.name for group in result.highest_median_departments] == ["C"]


def test_payroll_spend_and_median_pay_extrema_have_distinct_semantics(
    session: Session,
) -> None:
    add_rate(session, "USD", "1")
    add_employee(session, 1, salary="60", country="US", department="Large")
    add_employee(session, 2, salary="60", country="US", department="Large")
    add_employee(session, 3, salary="60", country="US", department="Large")
    add_employee(session, 4, salary="100", country="GB", department="Specialist")
    session.commit()

    result = AnalyticsService(AnalyticsRepository(session)).payroll()

    groups = {group.name: group for group in result.department_breakdown}
    assert groups["Large"].total_payroll == Decimal("180.00")
    assert groups["Large"].average_salary == Decimal("60.00")
    assert groups["Large"].median_salary == Decimal("60.00")
    assert groups["Specialist"].median_salary == Decimal("100.00")
    assert [group.name for group in result.highest_payroll_departments] == ["Large"]
    assert [group.name for group in result.highest_median_departments] == ["Specialist"]

    countries = {group.name: group for group in result.country_breakdown}
    assert countries["US"].average_salary == Decimal("60.00")
    assert countries["US"].median_salary == Decimal("60.00")
    assert countries["GB"].average_salary == Decimal("100.00")
    assert [group.name for group in result.highest_payroll_countries] == ["US"]
    assert [group.name for group in result.highest_median_countries] == ["GB"]


def test_role_statistics_use_case_insensitive_exact_match_and_decimal_medians(
    session: Session,
) -> None:
    add_rate(session, "USD", "1")
    for number, salary, country in [
        (1, "10", "US"),
        (2, "20", "US"),
        (3, "30", "US"),
        (4, "10", "IN"),
        (5, "20", "IN"),
        (6, "999", "GB"),
    ]:
        add_employee(
            session,
            number,
            salary=salary,
            country=country,
            job_title="Engineer" if country != "GB" else "Senior Engineer",
        )
    session.commit()

    result = AnalyticsService(AnalyticsRepository(session)).role(" engineer ")

    assert result.employee_count == 5
    statistics = [
        (item.country, item.average_salary, item.median_salary) for item in result.countries
    ]
    assert statistics == [
        ("IN", Decimal("15.00"), Decimal("15.00")),
        ("US", Decimal("20.00"), Decimal("20.00")),
    ]


def test_role_rounds_only_final_average_and_median(session: Session) -> None:
    add_rate(session, "CAD", "0.3333333333")
    add_employee(session, 1, salary="1.01", currency="CAD", country="CA")
    add_employee(session, 2, salary="1.02", currency="CAD", country="CA")
    session.commit()

    result = AnalyticsService(AnalyticsRepository(session)).role("Engineer")

    assert result.countries[0].average_salary == Decimal("0.34")
    assert result.countries[0].median_salary == Decimal("0.34")


def test_role_excludes_inactive_by_default_and_can_include_it(session: Session) -> None:
    add_rate(session, "USD", "1")
    add_employee(session, 1, salary="100", job_title="Manager")
    add_employee(session, 2, salary="200", job_title="Manager", active=False)
    session.commit()

    service = AnalyticsService(AnalyticsRepository(session))

    assert service.role("manager").employee_count == 1
    included = service.role("manager", include_inactive=True)
    assert included.employee_count == 2
    assert included.countries[0].average_salary == Decimal("150.00")


def test_missing_fx_fails_whole_calculation(session: Session) -> None:
    add_rate(session, "USD", "1")
    add_employee(session, 1, salary="100", currency="USD")
    add_employee(session, 2, salary="100", currency="JPY")
    session.commit()

    with pytest.raises(ExchangeRateUnavailable) as error:
        AnalyticsService(AnalyticsRepository(session)).payroll()

    assert error.value.currency_code == "JPY"


def test_payroll_api_contract_and_decimal_serialization(session: Session) -> None:
    add_rate(session, "USD", "1.0001")
    add_employee(session, 1, salary="100.12", department="Engineering")
    session.commit()

    response = client_for(session).get("/api/analytics/payroll?job_title=engineer")

    assert response.status_code == 200
    payload = response.json()
    assert payload["reporting_currency"] == "USD"
    assert payload["employee_count"] == 1
    assert payload["total_payroll"] == "100.13"
    assert payload["filters"] == {
        "country": None,
        "department": None,
        "job_title": "engineer",
        "include_inactive": False,
    }
    assert payload["department_breakdown"][0]["total_payroll"] == "100.13"
    assert payload["department_breakdown"][0]["average_salary"] == "100.13"
    assert payload["department_breakdown"][0]["median_salary"] == "100.13"


def test_role_api_empty_contract_and_include_inactive(session: Session) -> None:
    response = client_for(session).get("/api/analytics/roles/Engineer?include_inactive=true")

    assert response.status_code == 200
    assert response.json() == {
        "reporting_currency": "USD",
        "job_title": "Engineer",
        "employee_count": 0,
        "include_inactive": True,
        "countries": [],
    }


@pytest.mark.parametrize("path", ["/api/analytics/payroll", "/api/analytics/roles/Engineer"])
def test_analytics_api_maps_missing_fx_to_structured_503(session: Session, path: str) -> None:
    add_employee(session, 1, salary="100", currency="JPY")
    session.commit()

    response = client_for(session).get(path)

    assert response.status_code == 503
    assert response.json() == {
        "detail": {"code": "exchange_rate_unavailable", "currency": "JPY"}
    }
