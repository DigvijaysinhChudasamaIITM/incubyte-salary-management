import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

import { AnalyticsDashboard } from "./AnalyticsDashboard";

const engineering = {
  name: "Engineering",
  employee_count: 6,
  total_payroll: "600000.00",
  average_salary: "100000.00",
  median_salary: "95000.00",
};
const finance = {
  name: "Finance",
  employee_count: 4,
  total_payroll: "360000.00",
  average_salary: "90000.00",
  median_salary: "88000.00",
};
const us = { ...engineering, name: "US" };
const india = { ...finance, name: "IN" };

const payroll = {
  reporting_currency: "USD",
  employee_count: 10,
  total_payroll: "960000.00",
  filters: { country: null, department: null, job_title: null, include_inactive: false },
  department_breakdown: [engineering, finance],
  country_breakdown: [india, us],
  highest_payroll_departments: [engineering],
  lowest_payroll_departments: [finance],
  highest_payroll_countries: [us],
  lowest_payroll_countries: [india],
  highest_median_departments: [engineering],
  lowest_median_departments: [finance],
  highest_median_countries: [us],
  lowest_median_countries: [india],
};

afterEach(() => vi.unstubAllGlobals());

test("renders payroll KPIs, static FX context, spend, and median-pay views", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse(payroll)));
  render(<AnalyticsDashboard />);

  expect(await screen.findByText("USD 960,000.00")).toBeInTheDocument();
  expect(screen.getByText("Active employees").nextElementSibling).toHaveTextContent("10");
  expect(screen.getByText("Reporting currency: USD")).toBeInTheDocument();
  expect(screen.getByText(/seeded assessment FX rates—not live market rates/i)).toBeInTheDocument();
  expect(screen.getByText("Payroll spend by department")).toBeInTheDocument();
  expect(screen.getByText("Payroll spend by country")).toBeInTheDocument();
  expect(screen.getByText("Median salary by department")).toBeInTheDocument();
  expect(screen.getByText("Median salary by country")).toBeInTheDocument();
  expect(screen.getAllByText("USD 95,000.00").length).toBeGreaterThan(0);
  expect(screen.getByText("Highest median-pay department").nextElementSibling).toHaveTextContent(
    "Engineering",
  );
});

test("shows initial and refetch loading states", async () => {
  let resolve!: (response: Response) => void;
  const pending = new Promise<Response>((value) => { resolve = value; });
  vi.stubGlobal("fetch", vi.fn().mockReturnValue(pending));
  render(<AnalyticsDashboard />);

  expect(screen.getByRole("status")).toHaveTextContent("Loading compensation analytics");
  resolve(jsonResponse(payroll));
  expect(await screen.findByText("USD 960,000.00")).toBeInTheDocument();

  let resolveRefetch!: (response: Response) => void;
  const refetch = new Promise<Response>((value) => { resolveRefetch = value; });
  vi.mocked(fetch).mockReturnValueOnce(refetch);
  fireEvent.change(screen.getByLabelText("Country"), { target: { value: "IN" } });
  expect(await screen.findByText("Updating analytics...")).toBeInTheDocument();
  resolveRefetch(jsonResponse(payroll));
  await waitFor(() => expect(screen.queryByText("Updating analytics...")).not.toBeInTheDocument());
});

test("composes payroll filters in server requests", async () => {
  const fetchMock = vi.fn().mockResolvedValue(jsonResponse(payroll));
  vi.stubGlobal("fetch", fetchMock);
  render(<AnalyticsDashboard />);
  await screen.findByText("USD 960,000.00");

  fireEvent.change(screen.getByLabelText("Country"), { target: { value: "IN" } });
  fireEvent.change(screen.getByLabelText("Department"), { target: { value: "Engineering" } });
  fireEvent.change(screen.getAllByLabelText("Job title")[0], { target: { value: "Engineer" } });
  fireEvent.click(screen.getByLabelText("Include inactive employees"));

  await waitFor(() => {
    const query = new URL(String(fetchMock.mock.lastCall?.[0]), "http://localhost").searchParams;
    expect(query.get("country")).toBe("IN");
    expect(query.get("department")).toBe("Engineering");
    expect(query.get("job_title")).toBe("Engineer");
    expect(query.get("include_inactive")).toBe("true");
  });
});

test("shows a retryable payroll error", async () => {
  const fetchMock = vi.fn().mockRejectedValueOnce(new Error("offline")).mockResolvedValueOnce(jsonResponse(payroll));
  vi.stubGlobal("fetch", fetchMock);
  render(<AnalyticsDashboard />);

  expect(await screen.findByRole("alert")).toHaveTextContent("Analytics are unavailable");
  fireEvent.click(screen.getByRole("button", { name: /Retry/ }));
  expect(await screen.findByText("USD 960,000.00")).toBeInTheDocument();
});

test("shows an empty payroll state", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse({
    ...payroll,
    employee_count: 0,
    total_payroll: "0.00",
    department_breakdown: [],
    country_breakdown: [],
  })));
  render(<AnalyticsDashboard />);

  expect(await screen.findByText("No payroll data matches")).toBeInTheDocument();
});

test("requests role analytics and renders country statistics", async () => {
  const fetchMock = vi.fn((input: string | URL | Request) => Promise.resolve(
    String(input).includes("/roles/")
      ? jsonResponse({ reporting_currency: "USD", job_title: "Engineer", employee_count: 2, include_inactive: false, countries: [{ country: "IN", employee_count: 2, average_salary: "1500.01", median_salary: "1490.00" }] })
      : jsonResponse(payroll),
  ));
  vi.stubGlobal("fetch", fetchMock);
  render(<AnalyticsDashboard />);
  await screen.findByText("USD 960,000.00");

  const rolePanel = screen.getByRole("heading", { name: "Compare a role across countries" }).closest("section")!;
  fireEvent.change(within(rolePanel).getByLabelText("Job title"), { target: { value: " Engineer " } });
  fireEvent.click(within(rolePanel).getByRole("button", { name: "Compare role" }));

  expect(await within(rolePanel).findByText("USD 1,500.01")).toBeInTheDocument();
  expect(within(rolePanel).getByText("USD 1,490.00")).toBeInTheDocument();
  expect(String(fetchMock.mock.lastCall?.[0])).toContain("/api/analytics/roles/Engineer");
});

test("shows a clear zero-match role state", async () => {
  vi.stubGlobal("fetch", vi.fn((input: string | URL | Request) => Promise.resolve(
    String(input).includes("/roles/")
      ? jsonResponse({ reporting_currency: "USD", job_title: "Astronaut", employee_count: 0, include_inactive: false, countries: [] })
      : jsonResponse(payroll),
  )));
  render(<AnalyticsDashboard />);
  await screen.findByText("USD 960,000.00");
  const rolePanel = screen.getByRole("heading", { name: "Compare a role across countries" }).closest("section")!;
  fireEvent.change(within(rolePanel).getByLabelText("Job title"), { target: { value: "Astronaut" } });
  fireEvent.submit(within(rolePanel).getByLabelText("Job title").closest("form")!);

  expect(await within(rolePanel).findByText("No employees match “Astronaut”")).toBeInTheDocument();
});

function jsonResponse(body: unknown, status = 200): Response {
  return { ok: status >= 200 && status < 300, status, json: async () => body } as Response;
}
