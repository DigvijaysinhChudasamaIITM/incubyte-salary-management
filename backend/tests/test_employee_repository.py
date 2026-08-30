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

    assert [item.employee_code for item in by_code] == ["EMP00001"]
    assert [item.employee_code for item in by_name] == ["EMP00002"]
    assert [item.employee_code for item in by_email] == ["EMP00003"]
    assert by_wildcard == []


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
