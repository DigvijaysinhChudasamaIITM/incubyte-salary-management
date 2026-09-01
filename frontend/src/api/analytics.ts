export interface AnalyticsFilters {
  country: string | null;
  department: string | null;
  job_title: string | null;
  include_inactive: boolean;
}

export interface PayrollGroup {
  name: string;
  employee_count: number;
  total_payroll: string;
  average_salary: string;
  median_salary: string;
}

export interface PayrollAnalytics {
  reporting_currency: string;
  employee_count: number;
  total_payroll: string;
  filters: AnalyticsFilters;
  department_breakdown: PayrollGroup[];
  country_breakdown: PayrollGroup[];
  highest_payroll_departments: PayrollGroup[];
  lowest_payroll_departments: PayrollGroup[];
  highest_payroll_countries: PayrollGroup[];
  lowest_payroll_countries: PayrollGroup[];
  highest_median_departments: PayrollGroup[];
  lowest_median_departments: PayrollGroup[];
  highest_median_countries: PayrollGroup[];
  lowest_median_countries: PayrollGroup[];
}

export interface RoleCountryStatistics {
  country: string;
  employee_count: number;
  average_salary: string;
  median_salary: string;
}

export interface RoleAnalytics {
  reporting_currency: string;
  job_title: string;
  employee_count: number;
  include_inactive: boolean;
  countries: RoleCountryStatistics[];
}

export interface PayrollQuery {
  country: string;
  department: string;
  jobTitle: string;
  includeInactive: boolean;
}

const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/+$/, "");

async function analyticsRequest<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, { signal });
  if (!response.ok) throw new Error(`Analytics request failed with status ${response.status}`);
  return response.json() as Promise<T>;
}

export function fetchPayrollAnalytics(
  query: PayrollQuery,
  signal?: AbortSignal,
): Promise<PayrollAnalytics> {
  const parameters = new URLSearchParams();
  if (query.country) parameters.set("country", query.country);
  if (query.department) parameters.set("department", query.department);
  if (query.jobTitle) parameters.set("job_title", query.jobTitle);
  if (query.includeInactive) parameters.set("include_inactive", "true");
  const suffix = parameters.size ? `?${parameters}` : "";
  return analyticsRequest(`/api/analytics/payroll${suffix}`, signal);
}

export function fetchRoleAnalytics(
  jobTitle: string,
  includeInactive: boolean,
  signal?: AbortSignal,
): Promise<RoleAnalytics> {
  const suffix = includeInactive ? "?include_inactive=true" : "";
  return analyticsRequest(
    `/api/analytics/roles/${encodeURIComponent(jobTitle.trim())}${suffix}`,
    signal,
  );
}
