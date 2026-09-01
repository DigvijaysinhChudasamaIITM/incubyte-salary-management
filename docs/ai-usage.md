# AI-Assisted Development Log

Incubyte explicitly encourages the use of AI tools during this assessment.

AI is being used as an engineering accelerator and review partner rather than as an unquestioned code generator.

Every AI-assisted decision or implementation remains subject to human review, automated testing, and manual verification.

## Entry 001 — Requirement Analysis

**Purpose**

Review the assessment from the perspectives of product ambiguity, engineering risk, testability, and maintainability.

**AI Assistance**

AI was used to:

* extract explicit requirements;
* distinguish requirements from assumptions;
* identify ambiguous product behaviour;
* identify potential financial-domain edge cases;
* generate candidate clarification questions;
* challenge unnecessary architecture.

**Human Decision**

Only four clarification questions were sent to Incubyte.

Questions about framework choice, database technology, UI libraries, test-coverage percentages, deployment provider, and other normal engineering decisions were deliberately not sent because those decisions should be owned by the candidate.

---

## Entry 002 — Scope Challenge

**AI Suggestion Reviewed**

Potential features considered included authentication, salary history, advanced analytics, bulk import/export, and natural-language salary querying.

**Human Decision**

Only functionality justified by the problem statement will be included in the mandatory scope.

Features that depended on unanswered product requirements were deferred at this stage. Incubyte's
later response is recorded in Entry 013 and now defines the finalized MVP.

In particular, no LLM-based product capability will be implemented simply to demonstrate AI experience.

---

## Entry 003 — Financial Data Review

**AI Assistance**

AI highlighted risks associated with:

* floating-point salary values;
* aggregating compensation across currencies;
* validation of negative or malformed salary values;
* duplicate updates;
* database constraints.

**Human Decision**

Salary values will use decimal-safe representations.

Cross-currency aggregation was deferred at this stage rather than silently applying an arbitrary
conversion policy. Incubyte later required deterministic normalization; USD was then selected as
an explicit engineering decision, not attributed to Incubyte.

---

## Verification Principle

AI-generated suggestions are not considered correct merely because they were generated.

For implementation work:

1. behaviour is defined;
2. tests are written where appropriate;
3. code is implemented;
4. tests and quality checks are executed;
5. results are manually reviewed;
6. only verified behaviour is treated as complete.

---

## Entry 004 - Quality Baseline

**Problem**

Establish reproducible backend and frontend quality gates without making product
assumptions while Incubyte's clarifications were pending.

**AI Assistance**

AI inspected the assessment, repository history, environment, and existing artifacts;
then proposed minimal FastAPI and React smoke slices with lint, test, and build tooling.

**Human Decision**

The tooling baseline and health checks were accepted. Employee and salary behavior was
deferred because it belongs in a later vertical slice. Python 3.10 was selected as the
minimum supported local runtime after inspection showed that Python 3.11 was unavailable.

**Verification**

Ruff and pytest were run for the backend. ESLint, Vitest, and a TypeScript/Vite production
build were run for the frontend. Dependency installation reported no known vulnerabilities.

---

## Entry 005 - Employee Browsing Foundation

**Problem**

Add relational employee data, deterministic assessment data, and scalable browsing without
prematurely deciding compensation-history, currency-conversion, authentication, or AI behavior.

**AI Assistance**

AI proposed the database constraints, SQL-backed pagination/search/filter flow, migration,
seed generation strategy, and behavior-focused repository/service/API test cases.

**Human Decision**

The model was kept deliberately small. Salary uses `Decimal`/`NUMERIC(14,2)`. Seed reruns
no-op only for a complete deterministic dataset and reject partial data. Broader compensation
features were deferred until Incubyte answered the product questions.

**Verification**

The slice is verified through repository, database-constraint, migration, seed, and API tests,
plus fresh-database migration and two-run 10,000-employee seed checks.

---

## Entry 006 - Employee Browsing Interface

**Problem**

Expose the server-paginated employee dataset through an accessible, responsive HR workspace
without pulling all employee records into the browser or adding deferred product features.

**AI Assistance**

AI proposed the request-state model, relative API client, responsive table layout, string-based
salary formatting, and tests for loading, querying, pagination, empty, and error behavior.

**Human Decision**

Search is explicitly submitted, country and department filters request page one immediately,
and all controls are disabled while a replacement page is loading. Salary strings are formatted
without converting them to JavaScript numbers. Decorative dashboard or analytics content was
rejected as outside the current slice.

**Verification**

The interface was verified with Vitest interaction tests, ESLint, TypeScript compilation, a Vite
production build, and a manual smoke test through the development proxy against the seeded API.

---

## Entry 007 - Continuous Integration

**Problem**

Run the established backend and frontend quality gates consistently for every push and pull
request, and confirm that repository setup works without relying on an existing workstation.

**AI Assistance**

AI reviewed the current commands, checked maintained GitHub Action major versions, proposed two
parallel jobs, and audited the README as a literal fresh-checkout procedure.

**Human Decision**

CI uses Python 3.11 and Node 22 without Docker or dependency caching. Backend and frontend checks
remain separate for clear failures. The README now creates a virtual environment and performs
migration and seeding before service startup.

**Verification**

The workflow commands were run locally, and the README procedure was repeated from an isolated
checkout through dependency installation, migration, seeding, tests, lint, and frontend build.

---

## Entry 008 - Deployment Readiness and Production Configuration

**Problem**

Prepare the existing application for a future hosting provider without selecting paid
infrastructure or deciding any unresolved compensation behavior.

**AI Assistance**

AI reviewed the runtime, migration, frontend build, and seed paths; proposed PostgreSQL URL
normalization, explicit origin configuration, database-backed readiness, and two portable
deployment topologies; and identified the configuration and failure paths requiring tests.

**Human Decision**

Same-origin routing remains the preferred simple topology, with split-origin CORS enabled only
through an exact allowlist. Migrations and optional seed data remain deliberate one-off commands,
not web-process startup side effects. No provider manifest, Docker setup, or infrastructure service
was introduced.

**Verification**

Backend configuration and probe tests, the full backend/frontend quality suites, a frontend build
with an explicit API origin, fresh environment-driven migration, diff validation, and secret scans
verify the deployment surface before approval.

---

## Entry 009 - Vercel and Neon Deployment Adaptation

**Problem**

Adapt the existing nested React and FastAPI application to one Vercel domain with Neon persistence
without moving domain code, exposing secrets, or running schema/data changes during startup.

**AI Assistance**

AI reviewed current Vercel FastAPI, Python runtime, Vite, routing, and Neon connection guidance;
compared multi-project, private-beta Services, and standard Python-function layouts; and proposed
the smallest generally available same-origin adapter.

**Human Decision**

Use a root `api/index.py` that imports the existing application, a root dependency reference to
the backend project, and two probe rewrites. Keep the frontend API base and CORS unset. Use pooled
Neon connectivity at runtime and a direct secret connection for manual migration and optional
one-time seeding.

**Verification**

The adapter is verified through backend and frontend suites, entrypoint and connection-pool tests,
production frontend build, Vercel configuration validation where locally available, diff checks,
and secret scanning. Hosted routing and real Neon migration remain deployment-time checks.

---

## Entry 010 - Vercel uv Package Identity Fix

**Problem**

Vercel's uv resolver inferred the name `backend` from a bare root path requirement, then rejected
the backend project's authoritative metadata name, `salary-management-api`.

**AI Assistance**

AI identified the path-name inference conflict and implemented the smallest explicit uv source
mapping while preserving the backend package boundary and Python 3.12 selection.

**Human Decision**

Use a non-package root deployment project that depends on `salary-management-api`, mapped to
`./backend` through `[tool.uv.sources]`. Do not copy backend dependency versions to the root.

**Verification**

The change is checked with uv dependency resolution when available, the full backend and frontend
quality suites, the production and Vercel build commands, diff validation, and secret scanning.

---

## Entry 011 - Vercel Services Deployment Split

**Problem**

The mixed FastAPI/Vite deployment built the nested frontend but exposed the project primarily as a
FastAPI application, leaving the generated `frontend/dist/index.html` unavailable at runtime.

**AI Assistance**

AI reviewed current Vercel Services, service routing, Vite, and FastAPI documentation and mapped
the existing application boundaries into separate framework-owned builds without moving code.

**Human Decision**

Use one Vercel Services project with `frontend/` as the root Vite service and the existing root
FastAPI adapter as the backend service. Keep public API and probe routing same-origin, retain uv
package mapping and Neon configuration, and leave migrations and seeding explicit.

**Verification**

The service schema and route ownership are checked alongside both application quality suites, a
Vite production build, diff validation, and secret scanning. The dashboard preset and hosted
service deployment remain production checks.

---

## Entry 012 - Production Deployment Diagnosis and Verification

**Problem**

Several independent deployment faults appeared successively: uv rejected a path whose inferred
name disagreed with backend metadata; a malformed Vercel `DATABASE_URL` caused an import-time
failure; mixed FastAPI/Vite detection did not publish the nested frontend output; and the initial
Services catch-all matched nested frontend paths but not `/`.

**AI Assistance**

AI correlated Vercel build/runtime evidence and direct production route probes with the committed
configuration. Fixes were intentionally narrow: explicit uv package mapping, corrected environment
configuration, separate Vite and FastAPI services, and the documented `/(.*)` root matcher.

**Human Decision**

Accept changes only after the preceding production signal identified a concrete failure boundary.
Keep application behavior, same-origin requests, Neon persistence, and explicit migration/seed
operations unchanged.

**Verification**

The live deployment at https://incubyte-salary-management-eight.vercel.app serves the frontend,
healthy API probes, and 10,000 Neon-backed employee records. Search, individual and combined
filters, empty results, salary/currency presentation, and server-side pagination across multiple
pages in both directions were manually verified. This sequence reinforced that production logs
and observable routes should drive deployment fixes rather than speculative changes across
application layers.

---

## Entry 013 - Incubyte Clarification and Final MVP Plan

**Problem**

Four product boundaries had deliberately remained unresolved: employee-management depth,
compensation questions, cross-currency reporting, and authentication expectations.

**AI Assistance**

AI compared Incubyte's authoritative response with the current production slice, removed obsolete
pending language, identified missing model/API/UI/analytics capabilities, and drafted an acceptance
matrix and implementation sequence. It also challenged whether a dedicated employee detail page,
a region taxonomy, live FX, or database-specific median SQL were necessary for this MVP.

**Incubyte-Confirmed Requirements**

The P0 includes server-side search, sorting and pagination; employee view/create/salary-update and
record-preserving deactivation; structured compensation dashboards; native salary currencies;
seeded exchange rates and common-currency analytics; and active-only analytics by default. History,
compensation components, bulk Excel import, required natural-language querying, authentication,
SSO, and RBAC are excluded.

**Human Engineering Decisions**

USD is the reporting currency, country is the regional grain, `is_active` represents deactivation,
identifiers remain unique across inactive records, sorting stays server-side, and the complete
directory row satisfies P0 viewing without a separate detail endpoint. Exact P50 is computed over
a filtered Decimal projection for consistent local and production behavior. These choices are
explicitly documented as candidate-owned decisions rather than attributed to Incubyte.

**Verification**

Documentation was checked against the current schema, API, repository, and UI so planned work is
not presented as implemented. No product or deployment code was changed during this planning phase.

---

## Entry 014 - Employee Status and Stable Sorting

**Problem**

Implement the first confirmed-MVP slice without pulling later CRUD, FX, analytics, or dashboard
work into scope.

**AI Assistance**

AI traced the model, Alembic, seed, repository, service, API, and frontend contract boundaries;
proposed a backfilled Boolean status, allowlisted query literals, and deterministic secondary
ordering; and added focused migration and behavior tests.

**Human Decision**

Default browsing to active employees, expose explicit active/inactive/all filters, allow sorting by
employee code, name, country, department, and job title, and use employee code ascending as the
tie-breaker for every non-code sort. Repeat seeding recognizes the deterministic employee set
without reactivating a deliberately inactive record.

**Verification**

Fresh migration and a 10,000-row pre-change migration prove the schema and backfill. Repository,
service, and API tests cover both directions, stable page ties, status filters, and rejected query
values. Backend and frontend quality suites verify the expanded response contract.

---

## Entry 015 - Compensation Analytics Backend

**Problem**

Implement the confirmed payroll and role analytics APIs without adding dashboard UI or coupling
application calculations to SQLAlchemy.

**AI Assistance**

AI traced the FX and repository boundaries, implemented a filtered employee/FX projection and exact
Decimal aggregation, and added adversarial fixtures that distinguish payroll spend from pay levels,
plus inactive records, tied extrema, odd/even P50, output rounding, empty results, and missing rates.

**Human Decision**

Keep the MVP implementation portable: calculate aggregates and P50 over one repository projection,
use median/P50 rather than group payroll total to compare pay distributions, return every tied
extreme in deterministic name order, and reserve database-native aggregation for future scale
evidence. USD remains the documented engineering-selected reporting currency.

**Verification**

Focused analytics tests and the full backend suite verify API contracts and calculation behavior.
No schema, frontend, deployment, or production-data changes are part of this slice.

---

## Entry 016 - Compensation Analytics Dashboard

**Problem**

Turn the deployed analytics contracts into a reviewer-facing HR overview without recalculating
money in the browser or disrupting employee-management workflows.

**AI Assistance**

AI mapped the response fields into distinct spend and median-pay sections, added server-backed
filters and role comparison, designed loading/refetch/retry/empty states, and added user-observable
frontend tests for analytics, navigation, and preserved directory access.

**Human Decision**

Open on Overview, keep Employees one click away, and use semantic CSS data bars instead of adding a
chart dependency. Backend monetary strings remain authoritative; numeric conversion is limited to
visual bar proportions. Static seeded FX limitations are prominent in the interface.

**Verification**

Vitest, ESLint, and the TypeScript/Vite production build cover the frontend slice. Backend code,
database schema, deployment configuration, and production data are unchanged.
