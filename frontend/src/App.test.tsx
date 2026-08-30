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
});

test("renders employee data and keeps salary precision in the display", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(response()));

  render(<App />);

  expect(await screen.findByText("Asha Patel")).toBeInTheDocument();
  expect(screen.getByText("asha@example.com")).toBeInTheDocument();
  expect(screen.getByText("INR 75,000.25")).toBeInTheDocument();
  expect(screen.getByText("1-25")).toBeInTheDocument();
  expect(screen.getByText("50", { selector: ".record-count span" })).toBeInTheDocument();
});

test("sends search, filter, and pagination changes to the backend", async () => {
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

  fireEvent.click(screen.getByRole("button", { name: "Next page" }));
  await waitFor(() => expect(String(fetchMock.mock.lastCall?.[0])).toContain("page=2"));

  const finalUrl = String(fetchMock.mock.lastCall?.[0]);
  expect(finalUrl).toContain("page_size=25");
  expect(finalUrl).toContain("country=IN");
  expect(finalUrl).toContain("department=Engineering");
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
