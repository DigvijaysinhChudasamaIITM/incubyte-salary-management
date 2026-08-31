# Salary Management - Finalized MVP Requirements

**Version:** 1.0
**Status:** Confirmed from Incubyte clarification

## Goal and User

Provide one already-authorized internal HR Manager with a reliable employee directory and
structured compensation insights for approximately 10,000 multi-country employees.

## Incubyte-Confirmed P0 Scope

- Search employees; sort, filter, and paginate on the server.
- View and create employee records, update salary, and deactivate employees without physical
  deletion.
- Retain salary in each employee's native currency.
- Seed 10,000 synthetic employees and deterministic exchange rates; no live FX integration.
- Provide KPI/dashboard analytics for normalized global payroll, department/country breakdowns,
  average and median (P50) salary for a role across regions, and highest/lowest-paying departments
  or countries, with useful interactive filters.
- Exclude inactive employees from analytics by default, with explicit inclusion where useful.
- Use decimal-safe financial values, persistent relational storage, and meaningful automated tests.

## Engineering/Product Decisions (Not Incubyte Requirements)

- **Reporting currency:** USD, selected as a neutral global comparison basis. One unit of local
  currency multiplied by a seeded `rate_to_usd` produces its USD value.
- **Deactivation:** add `is_active`; never delete an employee row. Employee code and email remain
  unique across active and inactive records.
- **Directory defaults:** show active employees, with an explicit status filter for inactive/all.
- **Sorting:** execute against an allowlist on the server with employee code as a stable tie-breaker.
- **Regional grain:** use country as the MVP region grouping; no separate region taxonomy is needed.
- **View workflow:** the directory row satisfies P0 viewing because it exposes the complete MVP
  record. Use focused create, salary-edit, and deactivate dialogs; defer a dedicated detail page
  until a detail-only workflow exists.
- **Write invariants:** codes/emails stay unique across inactive records; salaries stay positive;
  new currencies require a seeded rate; salary update changes amount only; deactivation is
  idempotent. Reactivation and salary history are not part of P0.

## Explicit Exclusions

Salary revision history; employee reactivation; bonuses, taxes, allowances, and other compensation
components; bulk Excel import; payroll execution; live FX APIs; required natural-language/AI
querying; authentication, SSO, and RBAC. The MVP assumes one authorized HR Manager; production
identity and access controls remain future work.

## Acceptance Summary

A reviewer can seed 10,000 records; browse, search, filter, and sort stable server-side pages;
create an employee; update salary; deactivate without data loss; include inactive records
explicitly; and use a structured dashboard to answer every confirmed compensation question in USD.
All operations validate on the backend, preserve decimal precision, and pass automated tests.
