# Engineering Decision Log

This document records meaningful technical and product decisions made during the assessment.

The purpose is not to document every implementation detail. It records decisions where reasonable alternatives existed and explains why a particular approach was chosen.

---

## D001 — Build a Modular Monolith

**Status:** Accepted

### Decision

Build the application as a single backend service with a separate React frontend rather than using microservices.

### Reason

The application serves one primary product domain and approximately 10,000 employees. This scale does not justify distributed-system complexity.

A modular monolith provides clear boundaries while remaining easy to build, test, deploy, and understand.

### Alternatives Considered

* Microservices
* Event-driven architecture

### Why Not Chosen

They introduce operational and architectural complexity without solving a demonstrated requirement.

---

## D002 — Python Backend

**Status:** Accepted

### Decision

Use Python with FastAPI for the backend.

### Reason

Python aligns directly with the target role, while FastAPI provides strong request validation, typing support, clear API contracts, good testing ergonomics, and lightweight implementation.

---

## D003 — React with TypeScript

**Status:** Accepted

### Decision

Use React with TypeScript for the user interface.

### Reason

React satisfies the assessment requirement. TypeScript improves API-contract clarity, refactoring safety, and maintainability.

---

## D004 — Relational Persistence

**Status:** Accepted

### Decision

Use a relational database for employee and compensation data.

### Reason

Employee and compensation information is naturally structured and benefits from schema constraints, indexes, transactional updates, and deterministic querying.

SQLite is used for local development and automated tests, with the connection URL supplied
through `DATABASE_URL`. SQLAlchemy and Alembic keep the persistence layer portable to a
PostgreSQL-compatible deployment database without adding local infrastructure.

---

## D005 — Financial Values Must Not Use Floating Point

**Status:** Accepted

### Decision

Salary values will use decimal/numeric financial representations.

### Reason

Binary floating-point arithmetic can introduce representation and rounding errors and is inappropriate for compensation data.

The initial database also requires salary amount to be greater than zero. This is a pragmatic
data-integrity assumption rather than an Incubyte-specified business rule. It will be revisited
only if later requirements make zero-value compensation a material valid case; it does not by
itself justify an additional clarification request.

---

## D006 — Server-Side Pagination

**Status:** Accepted

### Decision

Employee listings will be paginated by the backend.

### Reason

The product explicitly targets 10,000 employees. Loading every employee into the browser would be unnecessary and would make filtering, sorting, and application performance less predictable.

---

## D007 — No Product AI Feature Without Requirement

**Status:** Accepted

### Decision

Do not add an LLM, RAG system, vector database, or conversational interface merely because AI-assisted development is required.

### Reason

Incubyte confirmed that structured KPI cards, charts, and filters are the expected interface and
that natural-language/AI querying is optional stretch scope. Product AI is therefore not required
for the MVP.

---

## D008 - Deterministic Seed Safety

**Status:** Accepted

### Decision

Generate a fixed set of employee codes `EMP00001` through `EMP10000`. A repeat seed is a no-op when
all 10,000 deterministic codes are present and tolerates additional application-created employees.
Any partial deterministic code set blocks seeding with an explicit error. Existing seeded records
are never overwritten, so later salary or active-state changes remain intact.

### Reason

This makes normal repeat execution idempotent without making legitimate creates incompatible with
operations. Detecting partial deterministic data still prevents silently accepting an interrupted
seed, while non-destructive recognition avoids undoing application behavior.

---

## D009 - Provider-Neutral, Explicit Deployment Operations

**Status:** Accepted

### Decision

Keep runtime configuration in environment variables, prefer a same-origin frontend/API topology,
and run schema migration and optional demonstration seeding as explicit deployment operations.
Support a split-origin topology through an exact CORS allowlist and a build-time frontend API
origin, without selecting a hosting vendor or adding container infrastructure.

### Reason

Environment-driven database and origin configuration works with local SQLite and common managed
PostgreSQL providers. Same-origin routing is operationally simple and avoids unnecessary CORS,
while opt-in split-origin support prevents the architecture from depending on one provider.
Keeping migration and seed commands outside web startup prevents concurrent processes and routine
restarts from applying uncontrolled data changes.

### Alternatives Considered

* Hard-code one deployment provider and its manifest
* Enable wildcard CORS for every environment
* Apply migrations and seed data whenever the API starts

### Why Not Chosen

These options add premature provider coupling, expose a broader browser access surface, or make
production startup mutate schema and data implicitly.

---

## D010 - Vercel and Neon Deployment Target

**Status:** Accepted

### Decision

Deploy the React build and FastAPI function as one Vercel project and use Neon Postgres for
persistent production data. Keep browser API requests same-origin. Use Neon's pooled connection
for runtime traffic and its direct connection for explicit migration and seed operations.

### Reason

A single domain preserves the existing relative API client, avoids production CORS, and keeps the
take-home deployment small. A thin Vercel entrypoint adapts the existing backend without moving
domain code. Neon supplies managed Postgres without changing SQLAlchemy or Alembic boundaries.

### Trade-offs

Vercel's Python runtime is serverless and currently Beta, so cold starts, function limits, and
database connection behavior differ from a persistent web process. The adapter enables connection
pre-ping, while migrations and seeding stay outside request handling and deployment builds.

---

## D011 - Explicit uv Source for the Backend Package

**Status:** Accepted

### Decision

Declare `salary-management-api` as the root deployment project's only dependency and map that name
to `./backend` with `[tool.uv.sources]`. Keep package metadata and runtime dependency versions in
`backend/pyproject.toml`.

### Reason

A bare `./backend` requirements entry makes uv infer the package name `backend`, which conflicts
with the published metadata name `salary-management-api`. The explicit name-to-path mapping gives
uv both identities without duplicating the backend dependency list.

### Trade-offs

The root now contains minimal uv-specific project metadata. Other Python package managers do not
interpret `[tool.uv.sources]`, so the deployment install path assumes Vercel's current uv resolver.

---

## D012 - Separate Vite and FastAPI Vercel Services

**Status:** Accepted

### Decision

Deploy `frontend/` and the existing root FastAPI entrypoint as independent services in one Vercel
project. Route `/api/*`, `/health`, and `/ready` to the backend service and use the Vite service as
the `/` catch-all. Keep the project domain, backend package boundary, and Neon configuration.

### Reason

Mixed framework auto-detection treated FastAPI as the primary application and did not publish the
nested Vite output, even though the frontend build succeeded. Services give each application its
own framework build and merge them through an explicit public route table.

### Trade-offs

Vercel Services is a Beta feature and requires the dashboard Framework Preset to be `Services`.
The frontend and backend deploy together, and routing into a selected service is final rather than
falling through to another service.

### Production Outcome

The topology is live at https://incubyte-salary-management-eight.vercel.app. Production evidence
resolved five deployment faults in sequence: an ambiguous uv path dependency, a malformed
`DATABASE_URL`, mixed-framework output ownership, the need for separate Vercel Services, and a
top-level matcher that handled nested frontend paths but omitted bare `/`. Each correction followed
build logs or direct route probes rather than speculative application changes.

---

## D013 - Clarified Employee and Analytics MVP

**Status:** Accepted

### Incubyte-Confirmed Requirements

Deliver server-side employee search, sorting, pagination, view/create/salary-update/deactivation
workflows, and structured compensation analytics. Preserve native salaries, normalize analytics
with deterministic seeded exchange rates, exclude inactive employees from analytics by default,
and physically delete no employee. History, compensation components, bulk Excel import, required
natural-language querying, authentication, SSO, and RBAC are outside the MVP.

### Engineering Decisions

Use USD as the base reporting currency; Incubyte required a common currency but did not select USD.
Represent deactivation with `is_active`, retain identifier uniqueness across inactive rows, use
country as the regional grain, keep sorting server-side, and expose inactive records through an
explicit status filter. The complete directory row satisfies record viewing for P0; a dedicated
detail endpoint/screen is deferred until it supports information or actions not already present.
Salary edits change amount only and preserve native currency; deactivation is idempotent, while
reactivation is excluded because Incubyte did not request it.

### Reason and Trade-offs

These choices satisfy the confirmed workflows with the fewest new concepts and keep current-payroll
analytics accurate. Seeded rates are deterministic but become stale and are unsuitable for live
financial settlement. USD normalization is comparative reporting, not payroll accounting. Omitting
authentication is acceptable only under the confirmed already-authorized internal-user assumption;
SSO/RBAC is required future hardening for broader production access.

---

## D014 - Deterministic Assessment Exchange Rates

**Status:** Accepted

### Decision

Seed rates dated 2026-08-31 with the meaning `1 local unit = rate_to_usd USD`: USD `1.0000000000`,
INR `0.0120000000`, GBP `1.2500000000`, EUR `1.1000000000`, and CAD `0.7400000000`. Store and
calculate with `NUMERIC(20,10)`/Python `Decimal`; preserve multiplication precision and leave
rounding to a later reporting boundary. Reject missing rates as `exchange_rate_unavailable`.

### Reason and Trade-offs

These five currencies exactly cover the deterministic employee dataset. Simple fixed values make
tests and assessment results reproducible. They are static fixtures, not current market prices;
live or historical FX management remains deliberately out of scope and the values must not be used
for financial settlement.

---

## D015 - Portable Analytics and Explicit Extrema Ties

**Status:** Accepted

### Decision

Fetch one filtered employee/FX projection through an analytics repository, then use Python
`Decimal` for normalization, grouping, average, and exact P50. Keep total-payroll extrema explicitly
named as spend measures and use median/P50 for highest/lowest pay-distribution comparisons. Return
all ties as name-sorted arrays and compare full-precision values before rounding responses to cents.

### Reason and Trade-offs

This preserves the repository boundary, behaves consistently on SQLite and PostgreSQL, and is
proportionate for 10,000 employees. Database-side aggregation and percentiles remain an optimization
option if measurement at materially larger scale justifies the added database coupling.

---

## D016 - Use Semantic CSS Data Bars for MVP Analytics

**Status:** Accepted

### Decision

Render the small department/country analytics sets as labelled semantic lists with CSS data bars,
without adding a charting dependency. Convert rounded API strings to numbers only to calculate bar
lengths; display the authoritative strings unchanged and perform no business calculations in React.

### Reason and Trade-offs

Five categories per view do not justify a chart runtime or custom SVG framework. Visible values,
employee counts, headings, and KPI cards remain understandable without color or graphics, while the
layout stays responsive. A chart library can be reconsidered if richer interaction becomes required.
