# Issue 2: Add S3 artifact store support

Issue: https://github.com/kschweiger/agentome/issues/2
Issue Number: 2
Issue State: OPEN
Issue Updated: 2026-03-31T07:19:48Z
Last Synced: 2026-04-17T08:16:38+00:00

## Objective
No issue body provided.

## Acceptance Checks
- [x] Define at least one concrete success check before edits.
- [x] `pytest tests/test_utils.py tests/test_server_tools.py` passes with local artifact store default behavior unchanged.
- [x] `pytest tests/test_config.py tests/test_s3_store.py` passes with S3 support enabled.
- [x] `pytest tests/test_s3_integration.py` passes against running S3-compatible endpoint with `AGENTOME_RUN_S3_INTEGRATION=1`.
- [ ] `make check-markdown-links` passes.
- [ ] `make check-harness-docs` passes.

## Implementation Steps
- [x] Decompose work into the smallest coherent patch.
- [x] Run checks and capture validation evidence.
- [x] Implement in bounded slices (config -> store abstraction -> S3 store -> CLI wiring -> bootstrap -> tests -> docs).

## Risks and Unknowns
- Real S3 integration tests depend on external running endpoint and credentials.

## Validation Evidence
- `uv run pytest tests/test_utils.py tests/test_server_tools.py`
- `uv run pytest tests/test_config.py tests/test_s3_store.py tests/test_utils.py tests/test_server_tools.py`
- `uv run pytest tests/test_s3_integration.py -q` (with `.env` credentials and `AGENTOME_RUN_S3_INTEGRATION=1`)

## Decision Log
- Initial plan scaffold created from GitHub issue sync.
- 2026-04-20: Agreed backend config precedence `CLI > env > default`.
- 2026-04-20: Agreed idempotent `bootstrap-bucket` behavior (create-if-missing, non-destructive).
- 2026-04-20: Agreed S3 support ships as optional dependency extra using `boto3`.
- 2026-04-20: Agreed project-scoped env vars with `AGENTOME_S3_*` naming.
- 2026-04-20: Agreed local development uses existing external S3-compatible store; CI bootstrap follows in later change.
