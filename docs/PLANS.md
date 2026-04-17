# PLANS

Planning workflow:
1. Capture active plans in `docs/exec-plans/active/`.
2. Define explicit acceptance checks per bounded validate loop.
3. Move completed plans to `docs/exec-plans/completed/`.
4. Track follow-up debt in `docs/exec-plans/tech-debt-tracker.md`.

Issue-driven synchronization:
1. Run `make sync-plans-from-issues` to import and refresh issue-linked plans.
2. `Issue:` in a plan is optional.
3. If `Issue:` is present, it must be unique across all plan files.
4. If a linked issue closes, its plan is moved from `active/` to `completed/`.

Related:
- `docs/exec-plans/active/README.md`
- `docs/exec-plans/completed/README.md`
- `docs/exec-plans/tech-debt-tracker.md`
