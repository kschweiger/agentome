# PSPEC-0001 Agent Harness Operating Contract v1

## Objective
Enable human-steered, agent-executed development with deterministic checks, explicit policy boundaries, and repository-local knowledge governance.

## Functional Behavior
1. Repository must expose a short map (`AGENTS.md`) to indexed documentation.
2. Architecture and policy constraints must be codified in `ARCHITECTURE.md` and `docs/`.
3. Every non-trivial change must define at least one concrete success check before edits.
4. Non-trivial changes must run the review loop policy before handoff.
5. Knowledge drift must be tracked through `docs/QUALITY_SCORE.md` and `docs/exec-plans/tech-debt-tracker.md`.

## Acceptance Criteria
1. Required docs and indexes exist and are cross-linked.
2. `make check-markdown-links` passes.
3. `make check-harness-docs` passes.
4. CI runs policy checks on pull requests and on `main`.
5. Final handoff includes diff distribution report counts:
   - source code changes,
   - test code changes,
   - documentation changes.
