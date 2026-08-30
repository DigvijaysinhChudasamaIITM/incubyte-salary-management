# Testing Strategy

The assessment requires fast, deterministic, meaningful tests.

Testing will be implemented incrementally alongside product behaviour rather
than added only at the end.

## Planned Layers

- Unit tests for salary/domain rules
- Repository/database tests for persistence
- API tests for request/response behaviour
- Frontend tests for critical interactions
- Integration tests for important boundaries
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