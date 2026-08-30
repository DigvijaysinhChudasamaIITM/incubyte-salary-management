import { expect, test } from "vitest";

import { employeeApiUrl } from "./employees";

test("uses a relative API URL for same-origin and Vite proxy deployments", () => {
  const parameters = new URLSearchParams({ page: "1", page_size: "25" });

  expect(employeeApiUrl(parameters, "")).toBe("/api/employees?page=1&page_size=25");
});

test("uses the configured production API origin without a duplicate slash", () => {
  const parameters = new URLSearchParams({ page: "2", page_size: "50" });

  expect(employeeApiUrl(parameters, "https://api.example.com/")).toBe(
    "https://api.example.com/api/employees?page=2&page_size=50",
  );
});
