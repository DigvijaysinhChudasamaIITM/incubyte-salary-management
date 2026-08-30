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
