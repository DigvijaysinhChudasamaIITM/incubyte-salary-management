import { BarChart3, RefreshCw, Search } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";

import {
  PayrollAnalytics,
  PayrollGroup,
  PayrollQuery,
  RoleAnalytics,
  fetchPayrollAnalytics,
  fetchRoleAnalytics,
} from "./api/analytics";

const COUNTRIES = ["CA", "DE", "GB", "IN", "US"];
const DEPARTMENTS = ["Engineering", "Finance", "Operations", "People", "Sales"];
const INITIAL_QUERY: PayrollQuery = {
  country: "",
  department: "",
  jobTitle: "",
  includeInactive: false,
};

export function AnalyticsDashboard() {
  const [query, setQuery] = useState(INITIAL_QUERY);
  const [data, setData] = useState<PayrollAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [reload, setReload] = useState(0);
  const [roleDraft, setRoleDraft] = useState("");
  const [role, setRole] = useState<RoleAnalytics | null>(null);
  const [roleLoading, setRoleLoading] = useState(false);
  const [roleError, setRoleError] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    fetchPayrollAnalytics(query, controller.signal)
      .then(setData)
      .catch((requestError: unknown) => {
        if (requestError instanceof DOMException && requestError.name === "AbortError") return;
        setError(true);
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [query, reload]);

  function setFilter(field: keyof PayrollQuery, value: string | boolean) {
    setLoading(true);
    setError(false);
    setQuery((current) => ({ ...current, [field]: value }));
  }

  function retryPayroll() {
    setLoading(true);
    setError(false);
    setReload((value) => value + 1);
  }

  async function submitRole(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const title = roleDraft.trim();
    if (!title) return;
    setRoleLoading(true);
    setRoleError(false);
    try {
      setRole(await fetchRoleAnalytics(title, query.includeInactive));
    } catch {
      setRoleError(true);
    } finally {
      setRoleLoading(false);
    }
  }

  return (
    <main className="analytics-page">
      <div className="page-heading analytics-heading">
        <div>
          <p className="eyebrow">Compensation intelligence</p>
          <h1>Overview</h1>
          <p className="page-intro">
            Current payroll and normalized pay levels across the organization.
          </p>
        </div>
        <div className="reporting-note">
          <strong>Reporting currency: USD</strong>
          <span>Normalized with seeded assessment FX rates—not live market rates.</span>
        </div>
      </div>

      <section className="analytics-filters" aria-label="Analytics filters">
        <FilterSelect label="Country" value={query.country} onChange={(value) => setFilter("country", value)} options={COUNTRIES} allLabel="All countries" />
        <FilterSelect label="Department" value={query.department} onChange={(value) => setFilter("department", value)} options={DEPARTMENTS} allLabel="All departments" />
        <label className="analytics-text-filter">
          <span>Job title</span>
          <input value={query.jobTitle} onChange={(event) => setFilter("jobTitle", event.target.value.trimStart())} placeholder="All job titles" />
        </label>
        <label className="checkbox-control">
          <input type="checkbox" checked={query.includeInactive} onChange={(event) => setFilter("includeInactive", event.target.checked)} />
          Include inactive employees
        </label>
      </section>

      {error ? (
        <section className="analytics-state" role="alert">
          <h2>Analytics are unavailable</h2>
          <p>The payroll service could not be reached.</p>
          <button type="button" onClick={retryPayroll}><RefreshCw size={16} aria-hidden="true" /> Retry</button>
        </section>
      ) : loading && !data ? (
        <section className="analytics-state" role="status"><span className="spinner" aria-hidden="true" /><p>Loading compensation analytics...</p></section>
      ) : data ? (
        <div aria-busy={loading} className={loading ? "analytics-content is-updating" : "analytics-content"}>
          {loading && <p className="analytics-updating" role="status">Updating analytics...</p>}
          {data.employee_count === 0 ? (
            <section className="analytics-state compact"><h2>No payroll data matches</h2><p>Adjust the analytics filters to include employees.</p></section>
          ) : (
            <>
              <KpiGrid data={data} />
              <section className="analytics-section" aria-labelledby="spend-heading">
                <div className="section-heading"><div><p className="eyebrow">Payroll spend</p><h2 id="spend-heading">Where payroll dollars go</h2></div><p>Totals reflect group size and answer spend—not typical pay.</p></div>
                <div className="chart-grid">
                  <MetricChart title="Payroll spend by department" groups={data.department_breakdown} field="total_payroll" />
                  <MetricChart title="Payroll spend by country" groups={data.country_breakdown} field="total_payroll" />
                </div>
              </section>
              <section className="analytics-section" aria-labelledby="pay-heading">
                <div className="section-heading"><div><p className="eyebrow">Pay levels</p><h2 id="pay-heading">Typical normalized salary</h2></div><p>Median/P50 is the primary comparison and is less sensitive to outliers.</p></div>
                <div className="chart-grid">
                  <MetricChart title="Median salary by department" groups={data.department_breakdown} field="median_salary" />
                  <MetricChart title="Median salary by country" groups={data.country_breakdown} field="median_salary" />
                </div>
              </section>
            </>
          )}
        </div>
      ) : null}

      <section className="role-panel" aria-labelledby="role-heading">
        <div className="section-heading"><div><p className="eyebrow">Role comparison</p><h2 id="role-heading">Compare a role across countries</h2></div><p>Average and P50 use normalized USD salaries.</p></div>
        <form onSubmit={submitRole} className="role-search">
          <label htmlFor="role-title">Job title</label>
          <div><input id="role-title" value={roleDraft} onChange={(event) => setRoleDraft(event.target.value)} placeholder="For example, Engineer" required /><button type="submit" disabled={roleLoading}><Search size={16} aria-hidden="true" />{roleLoading ? "Comparing..." : "Compare role"}</button></div>
        </form>
        {roleError && <div className="inline-error" role="alert">Role analytics could not be loaded. Try again.</div>}
        {role && role.employee_count === 0 && <div className="role-empty"><h3>No employees match “{role.job_title}”</h3><p>Try another exact job title or include inactive employees.</p></div>}
        {role && role.employee_count > 0 && <RoleTable data={role} />}
      </section>
    </main>
  );
}

function FilterSelect({ label, value, onChange, options, allLabel }: { label: string; value: string; onChange: (value: string) => void; options: string[]; allLabel: string }) {
  const id = `analytics-${label.toLowerCase()}`;
  return <label className="select-control" htmlFor={id}><span>{label}</span><select id={id} value={value} onChange={(event) => onChange(event.target.value)}><option value="">{allLabel}</option>{options.map((option) => <option key={option}>{option}</option>)}</select></label>;
}

function KpiGrid({ data }: { data: PayrollAnalytics }) {
  return <section className="kpi-grid" aria-label="Payroll highlights">
    <Kpi label={data.filters.include_inactive ? "Employees included" : "Active employees"} value={data.employee_count.toLocaleString()} />
    <Kpi label="Total global payroll" value={formatUsd(data.total_payroll)} />
    <Kpi label="Highest median-pay department" value={groupNames(data.highest_median_departments)} detail={groupValue(data.highest_median_departments)} />
    <Kpi label="Highest median-pay country" value={groupNames(data.highest_median_countries)} detail={groupValue(data.highest_median_countries)} />
  </section>;
}

function Kpi({ label, value, detail }: { label: string; value: string; detail?: string }) {
  return <article className="kpi-card"><span>{label}</span><strong>{value}</strong>{detail && <small>{detail}</small>}</article>;
}

function MetricChart({ title, groups, field }: { title: string; groups: PayrollGroup[]; field: "total_payroll" | "median_salary" }) {
  const maximum = Math.max(...groups.map((group) => Number(group[field])), 0);
  return <figure className="metric-chart"><figcaption><BarChart3 size={18} aria-hidden="true" />{title}</figcaption><ul>{groups.map((group) => {
    const width = maximum ? (Number(group[field]) / maximum) * 100 : 0;
    return <li key={group.name}><div className="metric-label"><strong>{group.name}</strong><span>{formatUsd(group[field])}</span></div><div className="metric-track" aria-hidden="true"><span style={{ width: `${width}%` }} /></div><small>{group.employee_count.toLocaleString()} employees</small></li>;
  })}</ul></figure>;
}

function RoleTable({ data }: { data: RoleAnalytics }) {
  return <div className="role-table-wrap"><p className="role-summary">{data.employee_count.toLocaleString()} employees matched “{data.job_title}”</p><table className="role-table"><thead><tr><th>Country</th><th>Employees</th><th>Average salary</th><th>Median / P50</th></tr></thead><tbody>{data.countries.map((country) => <tr key={country.country}><td>{country.country}</td><td>{country.employee_count.toLocaleString()}</td><td>{formatUsd(country.average_salary)}</td><td>{formatUsd(country.median_salary)}</td></tr>)}</tbody></table></div>;
}

function groupNames(groups: PayrollGroup[]): string {
  return groups.length ? groups.map((group) => group.name).join(" · ") : "—";
}

function groupValue(groups: PayrollGroup[]): string | undefined {
  return groups[0] ? `${formatUsd(groups[0].median_salary)} median` : undefined;
}

function formatUsd(value: string): string {
  const [whole, fraction = "00"] = value.split(".");
  return `USD ${whole.replace(/\B(?=(\d{3})+(?!\d))/g, ",")}.${fraction}`;
}
