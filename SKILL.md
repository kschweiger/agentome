---
name: "agentome-harness"
description: "Operating skill for end-to-end agentic harness execution loops."
---

# agentome Harness Skill

## When to use
- Use when a task requires agent-led implementation with explicit checks.
- Use when repository policies, docs, and CI must remain synchronized.
- Use when changes need bounded validate loops and review-loop closure.

## Scope and non-scope
- In scope:
  - plan creation and update using repository artifacts,
  - implementation with one concrete success check per loop,
  - policy and documentation synchronization,
  - local and CI-facing validation commands,
  - review-loop execution and feedback resolution.
- Out of scope:
  - irreversible production actions,
  - security or billing posture changes without human escalation,
  - workflows requiring external credentials.

## Operational workflow
1. Load context progressively: `AGENTS.md` -> `ARCHITECTURE.md` -> indexes.
2. Define one concrete success check before edits.
3. Implement the smallest coherent patch.
4. Run checks and inspect failures.
5. Revise and re-run until checks pass.
6. Run self-review and at least one additional agent review for non-trivial work.
7. Encode feedback into code, docs, or mechanical checks.
8. Produce handoff with diff distribution report.

## Issue-driven plan sync
- Trigger phrases:
  - `sync plans from github issues`
  - `refresh active plans from issues`
- Primary command:
  - `make sync-plans-from-issues`
- Behavior:
  - Plan `Issue:` reference is optional.
  - If a plan already contains an `Issue:` URL, reuse that plan and do not create a duplicate.
  - If an open issue has no linked plan, create one in `docs/exec-plans/active/`.
  - If a linked issue is closed, move its plan from `docs/exec-plans/active/` to `docs/exec-plans/completed/`.
  - Plans without an `Issue:` reference remain valid and are not forced to backfill.
- Default scope:
  - Prefer issues labeled `planning`.
  - Fallback to all open issues if no labeled issues are found.

## Required checks
- `make check-harness-docs`
- `make check-markdown-links`
- `make check-plan-issue-links`

Recommended checks:
- `make lint`
- `make lint-fix` (local autofix workflow)
- `make format` (local formatting workflow)
- `make test`

## Escalation triggers
Escalate to a human when:
- destructive production action is required,
- security/billing posture changes are needed,
- secrets or external credentials are required,
- policy intent is ambiguous after reading repository artifacts.
