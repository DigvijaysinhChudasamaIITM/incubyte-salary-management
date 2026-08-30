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
from `backend` and `npm run dev` from `frontend`.
