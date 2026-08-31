# Incubyte Salary Management

Take-home engineering assessment for a web-based employee salary management
application supporting approximately 10,000 employees.

## Status

Implementation in progress.

**Live demo:** https://incubyte-salary-management-eight.vercel.app

Incubyte-confirmed MVP requirements and separate engineering decisions are documented under
`/docs`. The current live slice includes the verified directory and server-side sorting/status
controls. CRUD, deactivation, and compensation-dashboard work remains planned; the deterministic
exchange-rate foundation is implemented locally but requires an explicit migration and seed before
deployment.

## Prerequisites

- Python 3.10 or newer
- Node.js 22 or newer

## Local setup

Create the backend environment and install dependencies:

```shell
cd backend
python -m venv .venv
```

Activate it with `source .venv/bin/activate` on macOS/Linux or
`.\.venv\Scripts\Activate.ps1` in Windows PowerShell, then run:

```shell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
alembic upgrade head
python -m salary_management.seed
uvicorn salary_management.main:app --reload
```

The migration and seed commands use `DATABASE_URL` when set and otherwise use
`sqlite:///./salary_management.db`. Repeating the seed is a safe no-op when the complete employee
and exchange-rate datasets exist; partial, unrelated, or conflicting deterministic data causes an
explicit error. The USD, INR, GBP, EUR, and CAD rates are fixed assessment fixtures dated
2026-08-31—not current market rates and not suitable for financial settlement.

In a second terminal, install and start the frontend:

```shell
cd frontend
npm ci
npm run dev
```

Open `http://localhost:5173`. During local development, Vite proxies `/api` requests
to the backend at `http://127.0.0.1:8000`.

## Quality checks

Run the backend checks from `backend` with the virtual environment active:

```shell
ruff check .
pytest
```

Run the frontend checks from `frontend`:

```shell
npm test
npm run lint
npm run build
```

Browse employees at `GET /api/employees`. The endpoint accepts `page`, `page_size` (up to
100), `search`, `country`, `department`, `status`, `sort_by`, and `sort_direction` query
parameters. Search matches employee code, name, and email. Status defaults to active employees;
supported values are `active`, `inactive`, and `all`.

## Environment variables

[`.env.example`](.env.example) lists the deployment configuration surface. The application does
not automatically load that file; set values through the shell or deployment provider.

| Variable | Used by | Default | Purpose |
| --- | --- | --- | --- |
| `DATABASE_URL` | Backend and Alembic | `sqlite:///./salary_management.db` | SQLAlchemy connection. Production uses Neon's pooled Postgres URL; common provider URL schemes select Psycopg automatically. |
| `CORS_ALLOWED_ORIGINS` | Backend | Empty | Optional comma-separated frontend origins. Leave empty for the same-origin Vercel deployment. |
| `VITE_API_BASE_URL` | Frontend build | Empty | Optional backend origin. Leave empty on Vercel so the browser uses same-origin `/api` requests. |

`VITE_API_BASE_URL` is embedded by Vite at build time. Changing it requires rebuilding the
frontend. Do not put secrets in any `VITE_` variable because browser bundles are public.

## Vercel and Neon deployment

The selected production topology is one Vercel Services project backed by Neon Postgres. Vercel
builds `frontend/` as the primary Vite service at `/` and the existing `api/index.py` FastAPI
application as the backend service for `/api/*`, `/health`, and `/ready`. The services share one
domain, so do not set `VITE_API_BASE_URL` or `CORS_ALLOWED_ORIGINS`.

Import the Git repository into Vercel with these settings:

- project root directory: repository root (`.`);
- framework preset: Services;
- Node.js version: 22;
- build, output, and install commands: leave at the service defaults;
- production environment variable: `DATABASE_URL` set to the Neon pooled connection string.

The service roots, frameworks, entrypoint, and public routing are committed in `vercel.json`;
dashboard values should not override them. `.python-version` selects Python 3.12. The root
`pyproject.toml` declares `salary-management-api` and maps it to `./backend` for uv; the backend
package remains authoritative for its runtime dependencies.

Create a Neon project and copy both connection strings from its Connect dialog. Use the pooled
connection string (hostname contains `-pooler`) as Vercel's `DATABASE_URL`, preserving
`sslmode=require` and `channel_binding=require`. Keep the direct connection string outside Git for
one-off schema administration.

Before the first production deployment, apply migrations from a trusted workstation using the
direct Neon URL:

```powershell
cd backend
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
$env:DATABASE_URL="<NEON_DIRECT_CONNECTION_STRING>"
alembic upgrade head
alembic current
```

If demonstration data is required, run the seed once in the same configured shell:

```powershell
python -m salary_management.seed
```

The seed is not a Vercel build or startup command. Repeating it against the complete deterministic
dataset is a no-op; partial or unrelated employee data is rejected. Never paste either Neon URL
into `VITE_API_BASE_URL`, committed files, build logs, or browser-visible settings.

- `GET /health` is a process liveness check and does not query the database.
- `GET /ready` checks database connectivity and returns `503` without exposing connection details
  when the database is unavailable.
- Seeding is never part of application startup. Run `python -m salary_management.seed` only as an
  intentional one-off operation when deterministic demonstration data is wanted.

After deployment, verify the frontend, `/api/employees?page=1&page_size=25`, `/health`, and
`/ready` on the same Vercel domain. Vercel manages TLS and Python function execution; Neon manages
Postgres persistence and backups according to the selected free-plan capabilities.

The production deployment has been manually verified end to end: the frontend loads at `/`, the
health and database-readiness probes succeed, and the paginated API reports all 10,000 seeded
employees. Employee-code search, country and department filters (individually and combined), the
no-result state, salary/currency formatting, and server-side pagination across multiple pages in
both directions all work against Neon over the same origin.
