# Testing Strategy

The assessment requires fast, deterministic, meaningful tests.

Testing will be implemented incrementally alongside product behaviour rather
than added only at the end.

## Test Layers

- Database constraint tests for financial precision, positive salaries, and uniqueness
- Repository tests for stable pagination, search, and combined filters
- Service tests for input normalization and pagination metadata
- API tests for request validation and response contracts
- Migration tests against a fresh relational database
- Seed tests for exactly 10,000 employees, repeat execution, and conflict safety
- Frontend tests for critical interactions as browsing UI behaviour is introduced
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
