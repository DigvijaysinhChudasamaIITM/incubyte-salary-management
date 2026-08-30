from conftest import employee
from sqlalchemy.orm import Session

from salary_management.application.employees import EmployeeService
from salary_management.persistence.employee_repository import EmployeeRepository


def test_service_normalizes_filters_and_calculates_page_count(session: Session) -> None:
    session.add_all(
        [
            employee(1, name="Asha Patel", country="IN", department="Engineering"),
            employee(2, name="Asha Shah", country="IN", department="Engineering"),
            employee(3, name="Morgan Lee", country="US", department="Engineering"),
        ]
    )
    session.commit()

    result = EmployeeService(EmployeeRepository(session)).browse(
        page=1,
        page_size=1,
        search="  asha  ",
        country=" in ",
        department=" Engineering ",
    )

    assert [item.employee_code for item in result.items] == ["EMP00001"]
    assert result.total == 2
    assert result.total_pages == 2
