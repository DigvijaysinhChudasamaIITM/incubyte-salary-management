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

## Quality baseline

Run the backend checks from `backend`:

```shell
python -m pip install -e ".[dev]"
ruff check .
pytest
```

Run the frontend checks from `frontend`:

```shell
npm install
npm run lint
npm test
npm run build
```

Start the development services with `uvicorn salary_management.main:app --reload`
from `backend` and `npm run dev` from `frontend`. Open `http://localhost:5173` to use
the employee browsing interface. During local development, Vite proxies `/api` requests
to the backend at `http://127.0.0.1:8000`.

## Database and seed data

From `backend`, create or update the local SQLite database and seed the deterministic
10,000-employee dataset:

```shell
alembic upgrade head
python -m salary_management.seed
```

Both commands use `DATABASE_URL` when set and otherwise use
`sqlite:///./salary_management.db`. Repeating the seed is a safe no-op when the complete
seed dataset exists; partial or unrelated employee data causes an explicit error.

Browse employees at `GET /api/employees`. The endpoint accepts `page`, `page_size` (up to
100), `search`, `country`, and `department` query parameters. Search matches employee code,
name, and email.
