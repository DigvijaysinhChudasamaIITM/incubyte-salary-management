import {
  ChevronLeft,
  ChevronRight,
  RefreshCw,
  Search,
  SlidersHorizontal,
  X,
} from "lucide-react";
import { FormEvent, useEffect, useState } from "react";

import { Employee, EmployeePage, EmployeeQuery, fetchEmployees } from "./api/employees";

const PAGE_SIZE = 25;
const COUNTRIES = [
  ["CA", "Canada"],
  ["DE", "Germany"],
  ["GB", "United Kingdom"],
  ["IN", "India"],
  ["US", "United States"],
] as const;
const DEPARTMENTS = ["Engineering", "Finance", "Operations", "People", "Sales"];
const initialQuery: EmployeeQuery = {
  page: 1,
  pageSize: PAGE_SIZE,
  search: "",
  country: "",
  department: "",
};

export function App() {
  const [query, setQuery] = useState(initialQuery);
  const [searchDraft, setSearchDraft] = useState("");
  const [data, setData] = useState<EmployeePage | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [reload, setReload] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    fetchEmployees(query, controller.signal)
      .then(setData)
      .catch((requestError: unknown) => {
        if (requestError instanceof DOMException && requestError.name === "AbortError") return;
        setData(null);
        setError(true);
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [query, reload]);

  function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    beginRequest();
    setQuery((current) => ({ ...current, search: searchDraft.trim(), page: 1 }));
  }

  function setFilter(filter: "country" | "department", value: string) {
    beginRequest();
    setQuery((current) => ({ ...current, [filter]: value, page: 1 }));
  }

  function clearFilters() {
    beginRequest();
    setSearchDraft("");
    setQuery(initialQuery);
  }

  function beginRequest() {
    setLoading(true);
    setError(false);
  }

  function changePage(page: number) {
    beginRequest();
    setQuery((current) => ({ ...current, page }));
  }

  function retry() {
    beginRequest();
    setReload((value) => value + 1);
  }

  const hasFilters = Boolean(query.search || query.country || query.department);

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-mark" aria-hidden="true">SM</div>
        <div>
          <span className="product-name">Salary Management</span>
          <span className="workspace-name">HR workspace</span>
        </div>
      </header>

      <main>
        <div className="page-heading">
          <div>
            <p className="eyebrow">People</p>
            <h1>Employees</h1>
          </div>
          <div className="record-count" aria-live="polite">
            <span>{data?.total.toLocaleString() ?? "--"}</span>
            <small>records</small>
          </div>
        </div>

        <section className="filter-bar" aria-label="Employee filters">
          <form className="search-control" onSubmit={submitSearch}>
            <label htmlFor="employee-search">Search employees</label>
            <div className="search-input-wrap">
              <Search size={18} aria-hidden="true" />
              <input
                id="employee-search"
                type="search"
                value={searchDraft}
                onChange={(event) => setSearchDraft(event.target.value)}
                placeholder="Name, email, or employee code"
                disabled={loading}
              />
              <button className="search-button" type="submit" disabled={loading}>Search</button>
            </div>
          </form>

          <div className="select-control">
            <label htmlFor="country-filter">Country</label>
            <select
              id="country-filter"
              value={query.country}
              onChange={(event) => setFilter("country", event.target.value)}
              disabled={loading}
            >
              <option value="">All countries</option>
              {COUNTRIES.map(([code, name]) => <option key={code} value={code}>{name}</option>)}
            </select>
          </div>

          <div className="select-control">
            <label htmlFor="department-filter">Department</label>
            <select
              id="department-filter"
              value={query.department}
              onChange={(event) => setFilter("department", event.target.value)}
              disabled={loading}
            >
              <option value="">All departments</option>
              {DEPARTMENTS.map((department) => (
                <option key={department} value={department}>{department}</option>
              ))}
            </select>
          </div>

          {hasFilters && (
            <button className="clear-button" type="button" onClick={clearFilters} disabled={loading}>
              <X size={16} aria-hidden="true" />
              Clear filters
            </button>
          )}
        </section>

        <section className="employee-panel" aria-labelledby="employee-table-heading">
          <div className="panel-heading">
            <div>
              <SlidersHorizontal size={18} aria-hidden="true" />
              <h2 id="employee-table-heading">Employee directory</h2>
            </div>
            {loading && data && <span className="updating">Updating...</span>}
          </div>

          {error ? (
            <div className="message-state" role="alert">
              <h3>Employee data is unavailable</h3>
              <p>Check the backend connection and try again.</p>
              <button type="button" onClick={retry}>
                <RefreshCw size={16} aria-hidden="true" />
                Retry
              </button>
            </div>
          ) : loading && !data ? (
            <div className="message-state" role="status">
              <span className="spinner" aria-hidden="true" />
              <p>Loading employees...</p>
            </div>
          ) : data?.items.length === 0 ? (
            <div className="message-state">
              <h3>No employees found</h3>
              <p>Adjust the current search or filters.</p>
              {hasFilters && <button type="button" onClick={clearFilters}>Clear filters</button>}
            </div>
          ) : data ? (
            <EmployeeTable employees={data.items} loading={loading} />
          ) : null}

          {data && data.items.length > 0 && !error && (
            <Pagination
              data={data}
              loading={loading}
              onPageChange={changePage}
            />
          )}
        </section>
      </main>
    </div>
  );
}

function EmployeeTable({ employees, loading }: { employees: Employee[]; loading: boolean }) {
  return (
    <div className="table-scroll" aria-busy={loading}>
      <table>
        <thead>
          <tr>
            <th scope="col">Employee</th>
            <th scope="col">Code</th>
            <th scope="col">Country</th>
            <th scope="col">Department</th>
            <th scope="col">Job title</th>
            <th scope="col" className="salary-column">Salary</th>
          </tr>
        </thead>
        <tbody>
          {employees.map((employee) => (
            <tr key={employee.employee_code}>
              <td>
                <strong>{employee.name}</strong>
                <span>{employee.email}</span>
              </td>
              <td className="code-cell">{employee.employee_code}</td>
              <td>{employee.country}</td>
              <td>{employee.department}</td>
              <td>{employee.job_title}</td>
              <td className="salary-column">{formatSalary(employee.salary_amount, employee.currency)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Pagination({ data, loading, onPageChange }: {
  data: EmployeePage;
  loading: boolean;
  onPageChange: (page: number) => void;
}) {
  const firstRecord = (data.page - 1) * data.page_size + 1;
  const lastRecord = Math.min(data.page * data.page_size, data.total);
  return (
    <nav className="pagination" aria-label="Employee pages">
      <p><span>{firstRecord.toLocaleString()}-{lastRecord.toLocaleString()}</span> of {data.total.toLocaleString()}</p>
      <div>
        <button type="button" title="Previous page" aria-label="Previous page" disabled={loading || data.page <= 1} onClick={() => onPageChange(data.page - 1)}>
          <ChevronLeft size={18} aria-hidden="true" />
        </button>
        <span>Page {data.page} of {data.total_pages}</span>
        <button type="button" title="Next page" aria-label="Next page" disabled={loading || data.page >= data.total_pages} onClick={() => onPageChange(data.page + 1)}>
          <ChevronRight size={18} aria-hidden="true" />
        </button>
      </div>
    </nav>
  );
}

function formatSalary(amount: string, currency: string): string {
  const [whole, fraction] = amount.split(".");
  const groupedWhole = whole.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  return `${currency} ${groupedWhole}${fraction ? `.${fraction}` : ""}`;
}
