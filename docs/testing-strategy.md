# Testing Strategy

The assessment requires fast, deterministic, meaningful tests.

Testing will be implemented incrementally alongside product behaviour rather
than added only at the end.

## Test Layers

- Database constraint tests for financial precision, positive salaries, and uniqueness
- Repository tests for stable pagination, search, and combined filters
- Service tests for input normalization and pagination metadata
- API tests for request validation and response contracts
- Configuration and deployment-probe tests for database URL compatibility, explicit CORS, and
  readiness failure behavior
- Migration tests against a fresh relational database
- Seed tests for exactly 10,000 employees, repeat execution, and conflict safety
- Frontend interaction tests for loading, salary display, server query construction,
  pagination, empty results, and retryable failures
- At least one end-to-end HR workflow before submission

## Principles

Tests should verify observable behaviour rather than implementation details.

Important requirements will be mapped to automated or manual verification.

Relevant edge cases include:

- invalid and missing input
- zero and negative salary values
- decimal precision
- nonexistent employees
- pagination boundaries
- filtering combinations
- persistence failures
- UI loading, empty, validation and error states
- repeat seed execution

A feature is not considered complete until its relevant tests and quality
checks pass.

Migration-backed slices must also be applied to a fresh database and checked for
schema drift. Seed changes must prove both the expected record count and safe repeat
behaviour outside the unit-test fixture.

Deployment-configuration changes must additionally prove that a production frontend build embeds
the configured API origin, that the default build retains relative API URLs, and that a fresh
database configured through `DATABASE_URL` can migrate to the current Alembic head.

The Vercel adapter is checked for an exported FastAPI application and deployment probe aliases.
The committed Vercel configuration must parse successfully, define independent Vite and FastAPI
services, route the frontend, API, and probes to their intended owners, retain an unset same-origin
frontend API base, and install the backend through the root uv package mapping.
Live Neon migration and Vercel routing are final deployment checks because credentials and hosted
infrastructure are deliberately unavailable to repository tests.

## Production Verification

The live deployment at https://incubyte-salary-management-eight.vercel.app was manually verified
after automated checks passed. `/` serves Vite; `/api/health` and `/api/ready` return healthy
responses; and the employee endpoint returns 25 records with a total of 10,000. Employee-code
search, country filtering, department filtering, combined filters, the empty state,
salary/currency formatting, and server-side pagination across multiple pages in both directions
were exercised through the UI. The successful readiness response and employee queries confirm
production Neon connectivity without exposing connection details.

## Continuous Integration

GitHub Actions runs backend Ruff and pytest checks plus frontend Vitest, ESLint, and
production-build checks on every push and pull request. The backend and frontend run as
independent jobs so failures remain easy to locate and both stacks can execute in parallel.
