# RELIABILITY

Reliability expectations for agent-authored changes:
1. Deterministic machine-facing outputs where practical.
2. Stable command behavior and explicit failure modes.
3. Reproducible local validation loops using repository checks.
4. Any reliability regression should add a failing check before the fix.
