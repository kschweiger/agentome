# DDES-0002 Agentic Harness Architecture and Boundary Contracts

## Intent
Define an enforceable harness architecture that supports high-throughput autonomous delivery without architectural drift.

## Architecture
The harness uses fixed workflow layers:
1. Intent Intake
2. Plan and Decomposition
3. Execution Runtime
4. Validation and Observation
5. Review and Merge Loop
6. Governance and Garbage Collection

Each layer has one primary responsibility and explicit handoff artifacts.

## Boundary Rules
- Knowledge must be encoded in versioned repository artifacts.
- Rule changes require synchronized updates to enforcement checks.
- Agent guidance should be map-first (`AGENTS.md`) and index-driven.
- Cross-cutting policy enters via documented constraints, not ad-hoc prompts.

## Enforcement Direction
- Validate structure and presence of required docs in CI.
- Validate internal links and map integrity.
- Track quality drift in scorecards and debt artifacts.
