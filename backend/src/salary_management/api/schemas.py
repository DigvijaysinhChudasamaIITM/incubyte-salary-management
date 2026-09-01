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


class EmployeeSalaryUpdateRequest(BaseModel):
    salary_amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)


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


class AnalyticsFiltersResponse(BaseModel):
    country: str | None
    department: str | None
    job_title: str | None
    include_inactive: bool


class PayrollGroupResponse(BaseModel):
    name: str
    employee_count: int
    total_payroll: Decimal
    average_salary: Decimal
    median_salary: Decimal


class PayrollAnalyticsResponse(BaseModel):
    reporting_currency: str
    employee_count: int
    total_payroll: Decimal
    filters: AnalyticsFiltersResponse
    department_breakdown: list[PayrollGroupResponse]
    country_breakdown: list[PayrollGroupResponse]
    highest_payroll_departments: list[PayrollGroupResponse]
    lowest_payroll_departments: list[PayrollGroupResponse]
    highest_payroll_countries: list[PayrollGroupResponse]
    lowest_payroll_countries: list[PayrollGroupResponse]
    highest_median_departments: list[PayrollGroupResponse]
    lowest_median_departments: list[PayrollGroupResponse]
    highest_median_countries: list[PayrollGroupResponse]
    lowest_median_countries: list[PayrollGroupResponse]


class RoleCountryStatisticsResponse(BaseModel):
    country: str
    employee_count: int
    average_salary: Decimal
    median_salary: Decimal


class RoleAnalyticsResponse(BaseModel):
    reporting_currency: str
    job_title: str
    employee_count: int
    include_inactive: bool
    countries: list[RoleCountryStatisticsResponse]
