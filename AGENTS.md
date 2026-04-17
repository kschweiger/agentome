# AGENTS.md

## Purpose
This repository is agent-first and harness-oriented.
`AGENTS.md` is intentionally short and acts as a map plus enforceable rules.

## Start Here (Progressive Disclosure)
1. Read `ARCHITECTURE.md` first.
2. Open the indexes:
   - `docs/design-docs/index.md`
   - `docs/product-specs/index.md`
   - `docs/references/index.md`
3. Only then open detailed documents.

## Navigation Map
- Architecture and boundaries: `ARCHITECTURE.md`
- Design beliefs and autonomy model: `docs/design-docs/index.md`
- Product behavior and acceptance criteria: `docs/product-specs/index.md`
- Planning workflow: `docs/PLANS.md`
- Reliability and security policy: `docs/RELIABILITY.md`, `docs/SECURITY.md`
- Curated external references: `docs/references/index.md`
- End-to-end operating skill: `SKILL.md`

## Agent-First Rules
- Use progressive disclosure: index first, details second.
- Source of truth is repository-local, versioned artifacts.
- Prefer authoritative sources (official docs, standards bodies, primary project documentation).
- If behavior changes, update docs and enforcement in the same change set.

## Housekeeping Rules
- Any changed document must update the corresponding index in the same change set.
- Any changed rule must update mechanical checks in `scripts/` or CI in `.github/workflows/`.
- Internal Markdown links must pass `make check-markdown-links`.
- Required harness docs must pass `make check-harness-docs`.
- Stale or contradictory docs are defects and must be corrected.
- Final implementation handoff must include a diff distribution report with:
  - source code changes,
  - test code changes,
  - documentation changes.

## Bounded Validate Loop Policy
- Define one concrete success check before making edits.
- Implement the smallest coherent patch that can pass that check in one loop.
- Re-run checks on every loop iteration.
- If checks fail, revise using failure output and rerun.
- If checks pass, behavior-preserving refactors are allowed with check reruns.
- In interactive mode, run fast local checks per loop.
- In delivery mode, run full impacted validation before handoff.

## Review Loop Policy (Ralph Wiggum Loop)
- The implementing agent must self-review locally.
- The implementing agent should request at least one additional agent review for non-trivial changes.
- Review comments become either:
  - code changes,
  - doc updates,
  - or new mechanical checks.
- Iterate until all required checks and review feedback are resolved.

## Escalation Policy
Escalate to a human only when one of these is true:
- irreversible/destructive production action is required,
- security/billing posture changes,
- secrets or external credentials are required,
- policy intent cannot be inferred from repository context.

## Architecture and Style Invariants
- Keep boundary parsing explicit at system edges.
- Keep logs structured and machine-queryable.
- Prefer deterministic outputs for machine interfaces.
- Keep modules and files small enough for agent legibility.
- Avoid hidden side effects in commands and scripts.

## Python Test and Typing Policy
- Use `pytest` style tests only; do not introduce `unittest`-based tests.
- Add explicit type annotations for all Python function parameters and return values, including tests and fixtures.
- Prefer simple, readable type annotations by default; use complex typing only when it materially improves correctness or maintainability.
- Treat `typing.Any` as an exception path: the implementing agent must ask for human approval before introducing it.
- Public-facing APIs must not use `Any` in type annotations.

## Language and Commit Standards
- Use English for all programming artifacts and documentation.
- Commits intended for `main` should use Conventional Commits.
