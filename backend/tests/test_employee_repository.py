from conftest import employee
from sqlalchemy.orm import Session

from salary_management.persistence.employee_repository import EmployeeQuery, EmployeeRepository


def test_lists_a_stable_page_and_total(session: Session) -> None:
    session.add_all(employee(number) for number in range(1, 6))
    session.commit()

    items, total = EmployeeRepository(session).list(EmployeeQuery(page=2, page_size=2))

    assert [item.employee_code for item in items] == ["EMP00003", "EMP00004"]
    assert total == 5


def test_searches_code_name_and_email_case_insensitively(session: Session) -> None:
    session.add_all(
        [
            employee(1, name="Asha Patel"),
            employee(2, name="Morgan Lee"),
            employee(3, name="Taylor Jones"),
        ]
    )
    session.commit()
    repository = EmployeeRepository(session)

    by_code, _ = repository.list(EmployeeQuery(page=1, page_size=10, search="emp00001"))
    by_name, _ = repository.list(EmployeeQuery(page=1, page_size=10, search="MORGAN"))
    by_email, _ = repository.list(EmployeeQuery(page=1, page_size=10, search="employee3@"))
    by_wildcard, _ = repository.list(EmployeeQuery(page=1, page_size=10, search="%"))
    by_single_wildcard, _ = repository.list(EmployeeQuery(page=1, page_size=10, search="_"))

    assert [item.employee_code for item in by_code] == ["EMP00001"]
    assert [item.employee_code for item in by_name] == ["EMP00002"]
    assert [item.employee_code for item in by_email] == ["EMP00003"]
    assert by_wildcard == []
    assert by_single_wildcard == []


def test_page_beyond_final_page_is_empty_but_preserves_total(session: Session) -> None:
    session.add_all(employee(number) for number in range(1, 4))
    session.commit()

    items, total = EmployeeRepository(session).list(EmployeeQuery(page=3, page_size=2))

    assert items == []
    assert total == 3


def test_combines_country_and_department_filters(session: Session) -> None:
    session.add_all(
        [
            employee(1, country="IN", department="Engineering"),
            employee(2, country="IN", department="Finance"),
            employee(3, country="US", department="Engineering"),
        ]
    )
    session.commit()

    items, total = EmployeeRepository(session).list(
        EmployeeQuery(page=1, page_size=10, country="IN", department="Engineering")
    )

    assert [item.employee_code for item in items] == ["EMP00001"]
    assert total == 1


def test_sorts_ascending_and_descending(session: Session) -> None:
    session.add_all(
        [
            employee(1, name="Morgan", country="US"),
            employee(2, name="Asha", country="IN"),
            employee(3, name="Zara", country="GB"),
        ]
    )
    session.commit()
    repository = EmployeeRepository(session)

    ascending, _ = repository.list(
        EmployeeQuery(page=1, page_size=10, sort_by="name", sort_direction="asc")
    )
    descending, _ = repository.list(
        EmployeeQuery(page=1, page_size=10, sort_by="name", sort_direction="desc")
    )

    assert [item.employee_code for item in ascending] == ["EMP00002", "EMP00001", "EMP00003"]
    assert [item.employee_code for item in descending] == ["EMP00003", "EMP00001", "EMP00002"]


def test_non_code_sort_has_stable_employee_code_tie_breaker(session: Session) -> None:
    session.add_all(employee(number, name="Same Name") for number in range(1, 7))
    session.commit()
    repository = EmployeeRepository(session)

    first_page, _ = repository.list(
        EmployeeQuery(page=1, page_size=3, sort_by="name", sort_direction="desc")
    )
    second_page, _ = repository.list(
        EmployeeQuery(page=2, page_size=3, sort_by="name", sort_direction="desc")
    )

    assert [item.employee_code for item in first_page] == [
        "EMP00001",
        "EMP00002",
        "EMP00003",
    ]
    assert [item.employee_code for item in second_page] == [
        "EMP00004",
        "EMP00005",
        "EMP00006",
    ]


def test_filters_active_inactive_and_all_employees(session: Session) -> None:
    session.add_all(
        [
            employee(1),
            employee(2, is_active=False),
            employee(3),
        ]
    )
    session.commit()
    repository = EmployeeRepository(session)

    active, active_total = repository.list(EmployeeQuery(page=1, page_size=10))
    inactive, inactive_total = repository.list(
        EmployeeQuery(page=1, page_size=10, status="inactive")
    )
    all_items, all_total = repository.list(EmployeeQuery(page=1, page_size=10, status="all"))

    assert [item.employee_code for item in active] == ["EMP00001", "EMP00003"]
    assert active_total == 2
    assert [item.employee_code for item in inactive] == ["EMP00002"]
    assert inactive_total == 1
    assert [item.employee_code for item in all_items] == [
        "EMP00001",
        "EMP00002",
        "EMP00003",
    ]
    assert all_total == 3
