export interface Employee {
  employee_code: string;
  name: string;
  email: string;
  country: string;
  department: string;
  job_title: string;
  salary_amount: string;
  currency: string;
  is_active: boolean;
}

export interface EmployeePage {
  items: Employee[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export type EmployeeSortField =
  | "employee_code"
  | "name"
  | "country"
  | "department"
  | "job_title";
export type SortDirection = "asc" | "desc";
export type EmployeeStatus = "active" | "inactive" | "all";

export interface EmployeeQuery {
  page: number;
  pageSize: number;
  search: string;
  country: string;
  department: string;
  sortBy: EmployeeSortField;
  sortDirection: SortDirection;
  status: EmployeeStatus;
}

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/+$/, "");

export function employeeApiUrl(parameters: URLSearchParams, baseUrl = apiBaseUrl): string {
  return `${baseUrl.replace(/\/+$/, "")}/api/employees?${parameters}`;
}

export async function fetchEmployees(
  query: EmployeeQuery,
  signal?: AbortSignal,
): Promise<EmployeePage> {
  const parameters = new URLSearchParams({
    page: String(query.page),
    page_size: String(query.pageSize),
    sort_by: query.sortBy,
    sort_direction: query.sortDirection,
    status: query.status,
  });
  if (query.search) parameters.set("search", query.search);
  if (query.country) parameters.set("country", query.country);
  if (query.department) parameters.set("department", query.department);

  const response = await fetch(employeeApiUrl(parameters), { signal });
  if (!response.ok) {
    throw new Error(`Employee request failed with status ${response.status}`);
  }
  return response.json() as Promise<EmployeePage>;
}
