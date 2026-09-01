import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, expect, test, vi } from "vitest";

import { App } from "./App";
import type { Employee, EmployeePage } from "./api/employees";

const asha: Employee = {
  employee_code: "EMP00001",
  name: "Asha Patel",
  email: "asha@example.com",
  country: "IN",
  department: "Engineering",
  job_title: "Senior Engineer",
  salary_amount: "75000.25",
  currency: "INR",
  is_active: true,
};

afterEach(() => {
  vi.unstubAllGlobals();
});

function response(page: Partial<EmployeePage> = {}): Response {
  return {
    ok: true,
    json: async () => ({
      items: [asha],
      page: 1,
      page_size: 25,
      total: 50,
      total_pages: 2,
      ...page,
    }),
  } as Response;
}

test("shows a loading state and disables request controls", () => {
  vi.stubGlobal("fetch", vi.fn(() => new Promise(() => undefined)));

  render(<App initialView="employees" />);

  expect(screen.getByRole("status")).toHaveTextContent("Loading employees");
  expect(screen.getByLabelText("Search employees")).toBeDisabled();
  expect(screen.getByLabelText("Country")).toBeDisabled();
  expect(screen.getByLabelText("Department")).toBeDisabled();
  expect(screen.getByLabelText("Status")).toBeDisabled();
});

test("renders employee data and keeps salary precision in the display", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response()));

  render(<App initialView="employees" />);

  expect(await screen.findByText("Asha Patel")).toBeInTheDocument();
  expect(screen.getByText("asha@example.com")).toBeInTheDocument();
  expect(screen.getByText("INR 75,000.25")).toBeInTheDocument();
  expect(screen.getByText("1-25")).toBeInTheDocument();
  expect(screen.getByText("50", { selector: ".record-count span" })).toBeInTheDocument();
  expect(screen.getByRole("columnheader", { name: "Code" })).toHaveAttribute(
    "aria-sort",
    "ascending",
  );
  expect(screen.getByRole("columnheader", { name: "Salary" })).not.toHaveAttribute("aria-sort");
});

test("opens on Overview and keeps employee workflows one click away", async () => {
  const analyticsResponse = jsonResponse({
    reporting_currency: "USD",
    employee_count: 0,
    total_payroll: "0.00",
    filters: { country: null, department: null, job_title: null, include_inactive: false },
    department_breakdown: [],
    country_breakdown: [],
    highest_payroll_departments: [],
    lowest_payroll_departments: [],
    highest_payroll_countries: [],
    lowest_payroll_countries: [],
    highest_median_departments: [],
    lowest_median_departments: [],
    highest_median_countries: [],
    lowest_median_countries: [],
  });
  const fetchMock = vi.fn((input: string | URL | Request) => Promise.resolve(
    String(input).includes("/api/analytics/payroll") ? analyticsResponse : response(),
  ));
  vi.stubGlobal("fetch", fetchMock);
  render(<App />);

  expect(await screen.findByRole("heading", { name: "Overview" })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Overview" })).toHaveAttribute("aria-current", "page");
  fireEvent.click(screen.getByRole("button", { name: "Employees" }));

  expect(await screen.findByText("Asha Patel")).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Add employee" })).toBeInTheDocument();
  expect(screen.getByRole("button", { name: "Employees" })).toHaveAttribute("aria-current", "page");
});

test("sorting uses server query parameters, toggles direction, and resets pagination", async () => {
  const fetchMock = vi.fn((input: string | URL | Request) => {
    const url = new URL(String(input), "http://localhost");
    return Promise.resolve(response({ page: Number(url.searchParams.get("page")) }));
  });
  vi.stubGlobal("fetch", fetchMock);
  render(<App initialView="employees" />);
  await screen.findByText("Asha Patel");

  fireEvent.click(screen.getByRole("button", { name: "Next page" }));
  await waitFor(() => expect(lastQuery(fetchMock).get("page")).toBe("2"));

  fireEvent.click(screen.getByRole("button", { name: "Employee" }));
  await waitFor(() => expect(lastQuery(fetchMock).get("sort_by")).toBe("name"));
  expect(lastQuery(fetchMock).get("sort_direction")).toBe("asc");
  expect(lastQuery(fetchMock).get("page")).toBe("1");
  expect(screen.getByRole("columnheader", { name: "Employee" })).toHaveAttribute(
    "aria-sort",
    "ascending",
  );

  fireEvent.click(screen.getByRole("button", { name: "Employee" }));
  await waitFor(() => expect(lastQuery(fetchMock).get("sort_direction")).toBe("desc"));
  expect(screen.getByRole("columnheader", { name: "Employee" })).toHaveAttribute(
    "aria-sort",
    "descending",
  );
});

test("status resets pagination and pagination preserves status and sorting", async () => {
  const fetchMock = vi.fn((input: string | URL | Request) => {
    const url = new URL(String(input), "http://localhost");
    return Promise.resolve(response({ page: Number(url.searchParams.get("page")) }));
  });
  vi.stubGlobal("fetch", fetchMock);
  render(<App initialView="employees" />);
  await screen.findByText("Asha Patel");

  fireEvent.click(screen.getByRole("button", { name: "Next page" }));
  await waitFor(() => expect(lastQuery(fetchMock).get("page")).toBe("2"));
  fireEvent.change(screen.getByLabelText("Status"), { target: { value: "all" } });
  await waitFor(() => expect(lastQuery(fetchMock).get("status")).toBe("all"));
  expect(lastQuery(fetchMock).get("page")).toBe("1");

  fireEvent.click(screen.getByRole("button", { name: "Job title" }));
  await waitFor(() => expect(lastQuery(fetchMock).get("sort_by")).toBe("job_title"));
  fireEvent.click(screen.getByRole("button", { name: "Next page" }));
  await waitFor(() => expect(lastQuery(fetchMock).get("page")).toBe("2"));
  expect(lastQuery(fetchMock).get("status")).toBe("all");
  expect(lastQuery(fetchMock).get("sort_by")).toBe("job_title");
  expect(lastQuery(fetchMock).get("sort_direction")).toBe("asc");

  fireEvent.click(screen.getByRole("button", { name: "Previous page" }));
  await waitFor(() => expect(lastQuery(fetchMock).get("page")).toBe("1"));
  expect(lastQuery(fetchMock).get("status")).toBe("all");
  expect(lastQuery(fetchMock).get("sort_by")).toBe("job_title");
});

test("sorting composes with search, country, department, and status", async () => {
  const fetchMock = vi.fn((input: string | URL | Request) => {
    const url = new URL(String(input), "http://localhost");
    const page = Number(url.searchParams.get("page"));
    return Promise.resolve(response({ page }));
  });
  vi.stubGlobal("fetch", fetchMock);
  render(<App initialView="employees" />);
  await screen.findByText("Asha Patel");

  fireEvent.change(screen.getByLabelText("Country"), { target: { value: "IN" } });
  await waitFor(() => expect(String(fetchMock.mock.lastCall?.[0])).toContain("country=IN"));

  fireEvent.change(screen.getByLabelText("Department"), {
    target: { value: "Engineering" },
  });
  await waitFor(() => expect(String(fetchMock.mock.lastCall?.[0])).toContain("department=Engineering"));

  fireEvent.change(screen.getByLabelText("Search employees"), { target: { value: "  asha  " } });
  fireEvent.submit(screen.getByLabelText("Search employees").closest("form")!);
  await waitFor(() => expect(String(fetchMock.mock.lastCall?.[0])).toContain("search=asha"));

  fireEvent.change(screen.getByLabelText("Status"), { target: { value: "all" } });
  await waitFor(() => expect(lastQuery(fetchMock).get("status")).toBe("all"));
  fireEvent.click(screen.getByRole("button", { name: "Country" }));
  await waitFor(() => expect(lastQuery(fetchMock).get("sort_by")).toBe("country"));

  const finalQuery = lastQuery(fetchMock);
  expect(finalQuery.get("page")).toBe("1");
  expect(finalQuery.get("page_size")).toBe("25");
  expect(finalQuery.get("search")).toBe("asha");
  expect(finalQuery.get("country")).toBe("IN");
  expect(finalQuery.get("department")).toBe("Engineering");
  expect(finalQuery.get("status")).toBe("all");
  expect(finalQuery.get("sort_by")).toBe("country");
  expect(finalQuery.get("sort_direction")).toBe("asc");
});

test("shows the empty state when no inactive employees match", async () => {
  const fetchMock = vi.fn((input: string | URL | Request) => {
    const url = new URL(String(input), "http://localhost");
    return Promise.resolve(
      url.searchParams.get("status") === "inactive"
        ? response({ items: [], total: 0, total_pages: 0 })
        : response(),
    );
  });
  vi.stubGlobal("fetch", fetchMock);
  render(<App initialView="employees" />);
  await screen.findByText("Asha Patel");

  fireEvent.change(screen.getByLabelText("Status"), { target: { value: "inactive" } });

  expect(await screen.findByText("No employees found")).toBeInTheDocument();
  expect(lastQuery(fetchMock).get("status")).toBe("inactive");
  expect(screen.getAllByRole("button", { name: "Clear filters" })).toHaveLength(2);
});

test("shows an empty state for a successful query without matches", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue(response({ items: [], total: 0, total_pages: 0 })),
  );

  render(<App initialView="employees" />);

  expect(await screen.findByText("No employees found")).toBeInTheDocument();
});

test("shows a retryable error when the backend request fails", async () => {
  const fetchMock = vi
    .fn()
    .mockRejectedValueOnce(new TypeError("Network error"))
    .mockResolvedValueOnce(response());
  vi.stubGlobal("fetch", fetchMock);
  render(<App initialView="employees" />);

  expect(await screen.findByRole("alert")).toHaveTextContent("Employee data is unavailable");
  fireEvent.click(screen.getByRole("button", { name: "Retry" }));

  expect(await screen.findByText("Asha Patel")).toBeInTheDocument();
  expect(fetchMock).toHaveBeenCalledTimes(2);
});

test("creates an employee from supported currencies and refreshes the directory", async () => {
  const created: Employee = {
    ...asha,
    employee_code: "NEW00001",
    name: "New Employee",
    email: "new.employee@example.com",
  };
  const fetchMock = vi.fn((input: string | URL | Request, init?: RequestInit) => {
    const url = String(input);
    if (url.endsWith("/api/metadata/currencies")) {
      return Promise.resolve(jsonResponse({ currencies: ["CAD", "EUR", "GBP", "INR", "USD"] }));
    }
    if (init?.method === "POST") return Promise.resolve(jsonResponse(created, 201));
    return Promise.resolve(response());
  });
  vi.stubGlobal("fetch", fetchMock);
  render(<App initialView="employees" />);
  await screen.findByText("Asha Patel");

  const addEmployee = screen.getByRole("button", { name: "Add employee" });
  addEmployee.focus();
  fireEvent.click(addEmployee);
  const dialog = await screen.findByRole("dialog", { name: "Add employee" });
  await waitFor(() => expect(within(dialog).getByLabelText("Currency")).toBeEnabled());
  fillCreateForm(dialog);
  fireEvent.click(within(dialog).getByRole("button", { name: "Add employee" }));

  expect(await screen.findByRole("status")).toHaveTextContent(
    "New Employee was added successfully",
  );
  expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  const postCall = fetchMock.mock.calls.find(([, init]) => init?.method === "POST");
  expect(postCall).toBeDefined();
  expect(JSON.parse(String(postCall?.[1]?.body))).toMatchObject({
    employee_code: "NEW00001",
    salary_amount: "12345.67",
    currency: "INR",
  });
  await waitFor(() => {
    const directoryGets = fetchMock.mock.calls.filter(([input, init]) =>
      String(input).includes("/api/employees?") && !init?.method
    );
    expect(directoryGets).toHaveLength(2);
  });
});

test("opens with keyboard focus and closes with Escape", async () => {
  vi.stubGlobal("fetch", createFormFetch(jsonResponse(asha, 201)));
  render(<App initialView="employees" />);
  await screen.findByText("Asha Patel");

  const addEmployee = screen.getByRole("button", { name: "Add employee" });
  addEmployee.focus();
  fireEvent.click(addEmployee);
  const dialog = await screen.findByRole("dialog");

  expect(within(dialog).getByLabelText("Employee code")).toHaveFocus();
  fireEvent.keyDown(dialog, { key: "Escape" });
  expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  expect(addEmployee).toHaveFocus();
});

test("keeps keyboard focus inside the create dialog", async () => {
  vi.stubGlobal("fetch", createFormFetch(jsonResponse(asha, 201)));
  render(<App initialView="employees" />);
  await screen.findByText("Asha Patel");
  fireEvent.click(screen.getByRole("button", { name: "Add employee" }));
  const dialog = await screen.findByRole("dialog");
  const close = within(dialog).getByRole("button", { name: "Close add employee form" });
  const submit = within(dialog).getByRole("button", { name: "Add employee" });

  submit.focus();
  fireEvent.keyDown(dialog, { key: "Tab" });
  expect(close).toHaveFocus();

  close.focus();
  fireEvent.keyDown(dialog, { key: "Tab", shiftKey: true });
  expect(submit).toHaveFocus();
});

test("prevents double submission while employee creation is pending", async () => {
  let resolveCreate!: (response: Response) => void;
  const pendingCreate = new Promise<Response>((resolve) => { resolveCreate = resolve; });
  const fetchMock = vi.fn((input: string | URL | Request, init?: RequestInit) => {
    if (String(input).endsWith("/api/metadata/currencies")) {
      return Promise.resolve(jsonResponse({ currencies: ["INR"] }));
    }
    if (init?.method === "POST") return pendingCreate;
    return Promise.resolve(response());
  });
  vi.stubGlobal("fetch", fetchMock);
  render(<App initialView="employees" />);
  await screen.findByText("Asha Patel");
  fireEvent.click(screen.getByRole("button", { name: "Add employee" }));
  const dialog = await screen.findByRole("dialog");
  await waitFor(() => expect(within(dialog).getByLabelText("Currency")).toBeEnabled());
  fillCreateForm(dialog);
  const submit = within(dialog).getByRole("button", { name: "Add employee" });

  fireEvent.click(submit);
  fireEvent.click(submit);

  expect(fetchMock.mock.calls.filter(([, init]) => init?.method === "POST")).toHaveLength(1);
  expect(within(dialog).getByRole("button", { name: "Adding employee..." })).toBeDisabled();
  resolveCreate(jsonResponse(asha, 201));
  await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());
});

test("shows duplicate conflicts at the relevant field", async () => {
  const fetchMock = createFormFetch(
    jsonResponse(
      { detail: { code: "employee_conflict", fields: ["email"] } },
      409,
    ),
  );
  vi.stubGlobal("fetch", fetchMock);
  render(<App initialView="employees" />);
  await screen.findByText("Asha Patel");
  fireEvent.click(screen.getByRole("button", { name: "Add employee" }));
  const dialog = await screen.findByRole("dialog");
  await waitFor(() => expect(within(dialog).getByLabelText("Currency")).toBeEnabled());
  fillCreateForm(dialog);
  fireEvent.click(within(dialog).getByRole("button", { name: "Add employee" }));

  expect(await within(dialog).findByText("Email already exists.")).toBeInTheDocument();
  expect(within(dialog).getByLabelText("Email")).toHaveAttribute("aria-invalid", "true");
  expect(within(dialog).getByText("Resolve the duplicate value and try again.")).toBeInTheDocument();
});

test("shows backend validation and general create failures without closing the form", async () => {
  const validationFetch = createFormFetch(
    jsonResponse(
      { detail: [{ loc: ["body", "email"], msg: "value is not a valid email address" }] },
      422,
    ),
  );
  vi.stubGlobal("fetch", validationFetch);
  const { unmount } = render(<App initialView="employees" />);
  await screen.findByText("Asha Patel");
  fireEvent.click(screen.getByRole("button", { name: "Add employee" }));
  let dialog = await screen.findByRole("dialog");
  await waitFor(() => expect(within(dialog).getByLabelText("Currency")).toBeEnabled());
  fillCreateForm(dialog);
  fireEvent.click(within(dialog).getByRole("button", { name: "Add employee" }));
  expect(await within(dialog).findByText("value is not a valid email address")).toBeInTheDocument();
  unmount();

  vi.stubGlobal("fetch", createFormFetch(jsonResponse({ detail: "failure" }, 500)));
  render(<App initialView="employees" />);
  await screen.findByText("Asha Patel");
  fireEvent.click(screen.getByRole("button", { name: "Add employee" }));
  dialog = await screen.findByRole("dialog");
  await waitFor(() => expect(within(dialog).getByLabelText("Currency")).toBeEnabled());
  fillCreateForm(dialog);
  fireEvent.click(within(dialog).getByRole("button", { name: "Add employee" }));
  expect(await within(dialog).findByText("Employee could not be created. Try again.")).toBeInTheDocument();
});

test("updates native salary and refetches the directory", async () => {
  const updated = { ...asha, salary_amount: "81234.56" };
  const fetchMock = mutationFetch("PATCH", jsonResponse(updated));
  vi.stubGlobal("fetch", fetchMock);
  render(<App initialView="employees" />);
  await screen.findByText("Asha Patel");

  fireEvent.click(screen.getByRole("button", { name: "Edit salary for Asha Patel" }));
  const dialog = await screen.findByRole("dialog", { name: "Update salary" });
  expect(within(dialog).getByText(/Current native salary: INR 75000.25/)).toBeInTheDocument();
  expect(within(dialog).queryByLabelText("Currency")).not.toBeInTheDocument();
  fireEvent.change(within(dialog).getByLabelText("Salary amount (INR)"), {
    target: { value: "81234.56" },
  });
  fireEvent.click(within(dialog).getByRole("button", { name: "Update salary" }));

  expect(await screen.findByRole("status")).toHaveTextContent("salary was updated successfully");
  const patchCall = fetchMock.mock.calls.find(([, init]) => init?.method === "PATCH");
  expect(String(patchCall?.[0])).toContain("/api/employees/EMP00001/salary");
  expect(JSON.parse(String(patchCall?.[1]?.body))).toEqual({ salary_amount: "81234.56" });
  await expectDirectoryRefetch(fetchMock);
});

test("shows salary validation and prevents duplicate salary submissions", async () => {
  let resolveUpdate!: (response: Response) => void;
  const pendingUpdate = new Promise<Response>((resolve) => { resolveUpdate = resolve; });
  const fetchMock = mutationFetch("PATCH", pendingUpdate);
  vi.stubGlobal("fetch", fetchMock);
  render(<App initialView="employees" />);
  await screen.findByText("Asha Patel");
  fireEvent.click(screen.getByRole("button", { name: "Edit salary for Asha Patel" }));
  let dialog = await screen.findByRole("dialog");
  const submit = within(dialog).getByRole("button", { name: "Update salary" });

  fireEvent.click(submit);
  fireEvent.click(submit);

  expect(fetchMock.mock.calls.filter(([, init]) => init?.method === "PATCH")).toHaveLength(1);
  expect(within(dialog).getByRole("button", { name: "Updating salary..." })).toBeDisabled();
  resolveUpdate(jsonResponse(asha));
  await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());

  const validationFetch = mutationFetch(
    "PATCH",
    jsonResponse(
      { detail: [{ loc: ["body", "salary_amount"], msg: "Input should be greater than 0" }] },
      422,
    ),
  );
  vi.stubGlobal("fetch", validationFetch);
  const editSalary = screen.getByRole("button", { name: "Edit salary for Asha Patel" });
  await waitFor(() => expect(editSalary).toBeEnabled());
  fireEvent.click(editSalary);
  dialog = await screen.findByRole("dialog");
  fireEvent.click(within(dialog).getByRole("button", { name: "Update salary" }));
  expect(await within(dialog).findByText("Input should be greater than 0")).toBeInTheDocument();
});

test("confirms deactivation, prevents duplicate submission, and refetches", async () => {
  let resolveDeactivate!: (response: Response) => void;
  const pendingDeactivate = new Promise<Response>((resolve) => { resolveDeactivate = resolve; });
  const fetchMock = mutationFetch("POST", pendingDeactivate);
  vi.stubGlobal("fetch", fetchMock);
  render(<App initialView="employees" />);
  await screen.findByText("Asha Patel");
  fireEvent.click(screen.getByRole("button", { name: "Deactivate Asha Patel" }));
  const dialog = await screen.findByRole("dialog", { name: "Deactivate employee" });
  expect(within(dialog).getByText(/record will be retained/)).toBeInTheDocument();
  expect(within(dialog).getByText(/excluded from current payroll/)).toBeInTheDocument();
  const confirm = within(dialog).getByRole("button", { name: "Deactivate employee" });

  fireEvent.click(confirm);
  fireEvent.click(confirm);

  expect(fetchMock.mock.calls.filter(([, init]) => init?.method === "POST")).toHaveLength(1);
  expect(within(dialog).getByRole("button", { name: "Deactivating employee..." })).toBeDisabled();
  resolveDeactivate(jsonResponse({ ...asha, is_active: false }));
  expect(await screen.findByRole("status")).toHaveTextContent("was deactivated successfully");
  await expectDirectoryRefetch(fetchMock);
});

test("keeps deactivation errors visible without closing the dialog", async () => {
  vi.stubGlobal("fetch", mutationFetch("POST", jsonResponse({ detail: "failure" }, 500)));
  render(<App initialView="employees" />);
  await screen.findByText("Asha Patel");
  fireEvent.click(screen.getByRole("button", { name: "Deactivate Asha Patel" }));
  const dialog = await screen.findByRole("dialog");
  fireEvent.click(within(dialog).getByRole("button", { name: "Deactivate employee" }));

  expect(
    await within(dialog).findByText("The employee action could not be completed. Try again."),
  ).toBeInTheDocument();
  expect(within(dialog).getByRole("button", { name: "Deactivate employee" })).toBeEnabled();
});

test("does not expose mutation actions for an inactive employee", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response({ items: [{ ...asha, is_active: false }] })));
  render(<App initialView="employees" />);

  expect(await screen.findByText("Inactive")).toBeInTheDocument();
  expect(screen.queryByRole("button", { name: /Edit salary for/ })).not.toBeInTheDocument();
  expect(screen.queryByRole("button", { name: /Deactivate Asha/ })).not.toBeInTheDocument();
});

function lastQuery(fetchMock: ReturnType<typeof vi.fn>): URLSearchParams {
  return new URL(String(fetchMock.mock.lastCall?.[0]), "http://localhost").searchParams;
}

function jsonResponse(body: unknown, status = 200): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  } as Response;
}

function createFormFetch(createResponse: Response) {
  return vi.fn((input: string | URL | Request, init?: RequestInit) => {
    if (String(input).endsWith("/api/metadata/currencies")) {
      return Promise.resolve(jsonResponse({ currencies: ["INR", "USD"] }));
    }
    if (init?.method === "POST") return Promise.resolve(createResponse);
    return Promise.resolve(response());
  });
}

function mutationFetch(method: "PATCH" | "POST", mutationResponse: Response | Promise<Response>) {
  return vi.fn((input: string | URL | Request, init?: RequestInit) => {
    if (init?.method === method) return Promise.resolve(mutationResponse);
    return Promise.resolve(response());
  });
}

async function expectDirectoryRefetch(fetchMock: ReturnType<typeof vi.fn>) {
  await waitFor(() => {
    const directoryGets = fetchMock.mock.calls.filter(([input, init]) =>
      String(input).includes("/api/employees?") && !init?.method
    );
    expect(directoryGets).toHaveLength(2);
  });
}

function fillCreateForm(dialog: HTMLElement) {
  fireEvent.change(within(dialog).getByLabelText("Employee code"), { target: { value: "NEW00001" } });
  fireEvent.change(within(dialog).getByLabelText("Name"), { target: { value: "New Employee" } });
  fireEvent.change(within(dialog).getByLabelText("Email"), { target: { value: "new.employee@example.com" } });
  fireEvent.change(within(dialog).getByLabelText("Country"), { target: { value: "IN" } });
  fireEvent.change(within(dialog).getByLabelText("Department"), { target: { value: "Engineering" } });
  fireEvent.change(within(dialog).getByLabelText("Job title"), { target: { value: "Engineer" } });
  fireEvent.change(within(dialog).getByLabelText("Salary amount"), { target: { value: "12345.67" } });
  fireEvent.change(within(dialog).getByLabelText("Currency"), { target: { value: "INR" } });
}
