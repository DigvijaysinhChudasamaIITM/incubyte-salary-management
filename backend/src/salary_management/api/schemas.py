from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class EmployeeCreateRequest(BaseModel):
    employee_code: str = Field(min_length=1, max_length=20)
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    country: str = Field(min_length=2, max_length=2, pattern=r"^[A-Za-z]{2}$")
    department: str = Field(min_length=1, max_length=80)
    job_title: str = Field(min_length=1, max_length=100)
    salary_amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    currency: str = Field(min_length=3, max_length=3, pattern=r"^[A-Za-z]{3}$")

    @field_validator("employee_code", "name", "department", "job_title")
    @classmethod
    def reject_whitespace_only(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value


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


class SupportedCurrenciesResponse(BaseModel):
    currencies: list[str]
