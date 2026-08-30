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

**Status:** Accepted pending clarification

### Decision

Do not add an LLM, RAG system, vector database, or conversational interface merely because AI-assisted development is required.

### Reason

The assessment explicitly requires intentional use of AI during software development but does not explicitly require the resulting product to contain AI functionality.

If Incubyte confirms that natural-language salary querying is required, this decision will be revisited.

---

## D008 - Deterministic Seed Safety

**Status:** Accepted

### Decision

Generate a fixed set of employee codes `EMP00001` through `EMP10000`. A repeat seed is a
no-op only when all 10,000 deterministic employee codes are present. Any partial or unrelated
employee dataset blocks seeding with an explicit error.

### Reason

This makes normal repeat execution idempotent while preventing the seed command from silently
mixing generated assessment data into an ambiguous existing dataset.

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

## Open Decisions

The following remain intentionally unresolved until clarification is received:

* current salary versus compensation history;
* compensation component model;
* bulk import/export scope;
* multi-currency reporting strategy;
* natural-language querying;
* authentication/authorization scope.
