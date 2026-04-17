# DDES-0003 Review Loop and Autonomy Thresholds

## Intent
Define the review loop and escalation boundaries for agent-authored changes.

## Review Loop
1. Agent performs local self-review.
2. Agent requests at least one additional agent review for non-trivial work.
3. Feedback is resolved through code, docs, or new checks.
4. Loop repeats until required checks and review comments are resolved.

## Autonomy Thresholds
Agents can proceed autonomously for reversible local development actions.

Agents must escalate when:
- destructive or irreversible production actions are required,
- security or billing posture changes are proposed,
- secrets or credentials are needed,
- policy intent cannot be inferred from repository artifacts.

## Merge Philosophy
- Favor short-lived pull requests.
- Prefer cheap follow-up fixes over prolonged blocking on non-critical flakes.
- Keep gates strict on correctness and policy boundaries.
