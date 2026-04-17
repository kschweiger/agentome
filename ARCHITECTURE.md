# ARCHITECTURE.md

## Target State
`agentome` is an agentic harness for serving versioned API artifacts to coding agents with deterministic, enforceable operating loops.

The repository is designed for:
- explicit workflow boundaries,
- progressive disclosure of knowledge,
- reproducible validation,
- mechanically enforced governance.

## Harness Topology
The harness architecture is language-agnostic and runtime-centered.

1. Intent Intake
   - Human supplies task intent and acceptance criteria.
   - Intent is translated into repository-local artifacts and checks.
2. Plan and Decomposition
   - Work is captured in executable plans and bounded loops.
   - Every non-trivial change defines one concrete success check first.
3. Execution Runtime
   - Agents run tooling directly (shell, scripts, CI, repository skills).
   - Actions are constrained by explicit mutating vs read-only boundaries.
4. Validation and Observation
   - Deterministic checks verify behavior and policy conformance.
   - Failures feed back into subsequent loop iterations.
5. Review and Merge Loop
   - Self-review plus additional agent review for non-trivial work.
   - Feedback is encoded into docs, checks, or code.
6. Governance and Garbage Collection
   - Recurring cleanup tasks enforce golden principles.
   - Drift is corrected continuously through small, targeted changes.

## Boundary Contracts
Required boundary rules:
1. Repository-local docs are authoritative for agent behavior.
2. `AGENTS.md` is a map; detailed policy belongs under `docs/`.
3. All rules that matter must be mechanically checkable in scripts or CI.
4. External context (chat, docs outside repo, tacit decisions) is non-authoritative until encoded in the repository.

Disallowed patterns:
- Monolithic instruction files that are not index-first.
- Policy-only guidance with no corresponding enforcement.
- Architecture or behavior changes without synchronized doc updates.

## Quality Gates
All changes must satisfy:
1. `make check-markdown-links`
2. `make check-harness-docs`

Recommended before handoff:
- `make lint`
- `make test`

## Documentation Governance
- `AGENTS.md` remains short and stable.
- Index files are first-class and must stay current.
- Plans, quality scores, and debt tracking are versioned repository artifacts.
