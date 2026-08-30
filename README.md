# Incubyte Salary Management

Take-home engineering assessment for a web-based employee salary management
application supporting approximately 10,000 employees.

## Status

Implementation in progress.

Product requirements and engineering decisions are documented under `/docs`.

Some product behaviours remain provisional while clarification from Incubyte
is pending.

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
`sqlite:///./salary_management.db`. Repeating the seed is a safe no-op when the complete
seed dataset exists; partial or unrelated employee data causes an explicit error.

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
100), `search`, `country`, and `department` query parameters. Search matches employee code,
name, and email.

## Environment variables

[`.env.example`](.env.example) lists the deployment configuration surface. The application does
not automatically load that file; set values through the shell or deployment provider.

| Variable | Used by | Default | Purpose |
| --- | --- | --- | --- |
| `DATABASE_URL` | Backend and Alembic | `sqlite:///./salary_management.db` | SQLAlchemy database connection. `postgres://` and `postgresql://` provider URLs use the installed Psycopg driver automatically. |
| `CORS_ALLOWED_ORIGINS` | Backend | Empty | Comma-separated explicit frontend origins for a split-origin deployment. Wildcards are rejected. |
| `VITE_API_BASE_URL` | Frontend build | Empty | Backend origin, such as `https://api.example.com`. Empty keeps relative `/api` requests for the local proxy or a same-origin deployment. |

`VITE_API_BASE_URL` is embedded by Vite at build time. Changing it requires rebuilding the
frontend. Do not put secrets in any `VITE_` variable because browser bundles are public.

## Production readiness

A provider-neutral deployment needs a Python web process, a static frontend host, and a
PostgreSQL-compatible database. Install backend dependencies and apply migrations as an explicit
release step before starting the service:

```shell
cd backend
python -m pip install --upgrade pip
python -m pip install .
alembic upgrade head
uvicorn salary_management.main:app --host 0.0.0.0 --port 8000
```

The provider should supply its assigned port to Uvicorn in place of `8000`. Build the frontend
with `npm ci && npm run build` and publish `frontend/dist` as static files.

The simplest topology serves the static frontend and proxies `/api`, `/health`, and `/ready` to
the backend under one public origin. It needs neither frontend API configuration nor CORS. If the
frontend and API use different origins, set `VITE_API_BASE_URL` during the frontend build and set
the exact frontend origin in `CORS_ALLOWED_ORIGINS` for the backend.

- `GET /health` is a process liveness check and does not query the database.
- `GET /ready` checks database connectivity and returns `503` without exposing connection details
  when the database is unavailable.
- Seeding is never part of application startup. Run `python -m salary_management.seed` only as an
  intentional one-off operation when deterministic demonstration data is wanted.

No provider is selected by this phase. TLS termination, managed database backups, secret
injection, process scaling, and deployment rollback behavior remain responsibilities of the
future hosting platform.
