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

The final database choice will be confirmed during environment/deployment setup.

---

## D005 — Financial Values Must Not Use Floating Point

**Status:** Accepted

### Decision

Salary values will use decimal/numeric financial representations.

### Reason

Binary floating-point arithmetic can introduce representation and rounding errors and is inappropriate for compensation data.

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

## Open Decisions

The following remain intentionally unresolved until clarification is received:

* current salary versus compensation history;
* compensation component model;
* bulk import/export scope;
* multi-currency reporting strategy;
* natural-language querying;
* authentication/authorization scope.
