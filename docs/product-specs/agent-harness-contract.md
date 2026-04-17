# PSPEC-0001 Agent Harness Operating Contract v2

## Objective
Enable human-steered, agent-executed development with deterministic checks, explicit policy boundaries, and repository-local knowledge governance.

## Functional Behavior
1. Repository must expose a short map (`AGENTS.md`) to indexed documentation.
2. Architecture and policy constraints must be codified in `ARCHITECTURE.md` and `docs/`.
3. Every non-trivial change must define at least one concrete success check before edits.
4. Non-trivial changes must run the review loop policy before handoff.
5. Knowledge drift must be tracked through `docs/QUALITY_SCORE.md` and `docs/exec-plans/tech-debt-tracker.md`.
6. Python tests must use `pytest` style only; `unittest`-based tests are out of contract.
7. Python functions must have explicit type annotations for parameters and return values, including tests and fixtures.
8. Prefer simple, readable type annotations by default; use complex typing only when it materially improves correctness or maintainability.
9. `typing.Any` is an exception path that requires explicit human approval before introduction.
10. Public-facing APIs must not use `Any` in type annotations.

## Acceptance Criteria
1. Required docs and indexes exist and are cross-linked.
2. `make check-markdown-links` passes.
3. `make check-harness-docs` passes.
4. CI runs policy checks on pull requests and on `main`.
5. Final handoff includes diff distribution report counts:
   - source code changes,
   - test code changes,
   - documentation changes.
6. Test suite code under `tests/` contains no `unittest` imports or `TestCase` inheritance.
7. Public-facing API code under `src/` uses no `typing.Any` in annotations.
