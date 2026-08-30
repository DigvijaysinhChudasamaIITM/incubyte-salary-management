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

Features that materially depend on unanswered product requirements remain deferred until clarification is received.

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

Cross-currency aggregation remains pending clarification rather than silently applying an arbitrary conversion policy.

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
assumptions while Incubyte's clarifications remain pending.

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
deciding any compensation-history, currency-conversion, authentication, or AI behavior.

**AI Assistance**

AI proposed the database constraints, SQL-backed pagination/search/filter flow, migration,
seed generation strategy, and behavior-focused repository/service/API test cases.

**Human Decision**

The model was kept deliberately small. Salary uses `Decimal`/`NUMERIC(14,2)`. Seed reruns
no-op only for a complete deterministic dataset and reject partial data. Broader compensation
features remain deferred pending Incubyte's answers.

**Verification**

The slice is verified through repository, database-constraint, migration, seed, and API tests,
plus fresh-database migration and two-run 10,000-employee seed checks.
