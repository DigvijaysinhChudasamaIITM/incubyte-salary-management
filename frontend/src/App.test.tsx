import { fireEvent, render, screen, waitFor } from "@testing-library/react";
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

  render(<App />);

  expect(screen.getByRole("status")).toHaveTextContent("Loading employees");
  expect(screen.getByLabelText("Search employees")).toBeDisabled();
  expect(screen.getByLabelText("Country")).toBeDisabled();
  expect(screen.getByLabelText("Department")).toBeDisabled();
  expect(screen.getByLabelText("Status")).toBeDisabled();
});

test("renders employee data and keeps salary precision in the display", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response()));

  render(<App />);

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

test("sorting uses server query parameters, toggles direction, and resets pagination", async () => {
  const fetchMock = vi.fn((input: string | URL | Request) => {
    const url = new URL(String(input), "http://localhost");
    return Promise.resolve(response({ page: Number(url.searchParams.get("page")) }));
  });
  vi.stubGlobal("fetch", fetchMock);
  render(<App />);
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
  render(<App />);
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
  render(<App />);
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
  render(<App />);
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

  render(<App />);

  expect(await screen.findByText("No employees found")).toBeInTheDocument();
});

test("shows a retryable error when the backend request fails", async () => {
  const fetchMock = vi
    .fn()
    .mockRejectedValueOnce(new TypeError("Network error"))
    .mockResolvedValueOnce(response());
  vi.stubGlobal("fetch", fetchMock);
  render(<App />);

  expect(await screen.findByRole("alert")).toHaveTextContent("Employee data is unavailable");
  fireEvent.click(screen.getByRole("button", { name: "Retry" }));

  expect(await screen.findByText("Asha Patel")).toBeInTheDocument();
  expect(fetchMock).toHaveBeenCalledTimes(2);
});

function lastQuery(fetchMock: ReturnType<typeof vi.fn>): URLSearchParams {
  return new URL(String(fetchMock.mock.lastCall?.[0]), "http://localhost").searchParams;
}
