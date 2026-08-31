from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    employee_code: str
    name: str
    email: str
    country: str
    department: str
    job_title: str
    salary_amount: Decimal
    currency: str
    is_active: bool


class EmployeePageResponse(BaseModel):
    items: list[EmployeeResponse]
    page: int
    page_size: int
    total: int
    total_pages: int
