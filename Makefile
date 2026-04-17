SHELL := /bin/zsh

.PHONY: help lint lint-fix format format-check test check-markdown-links check-harness-docs check-plan-issue-links check-python-test-typing-policy sync-plans-from-issues

help:
	@echo "Targets:"
	@echo "  make check-harness-docs   - validate required harness docs and indexes"
	@echo "  make check-markdown-links - validate markdown links with lychee"
	@echo "  make check-plan-issue-links - validate optional Issue links in plans"
	@echo "  make check-python-test-typing-policy - enforce pytest style and typing policy"
	@echo "  make lint                 - run ruff lint checks (optional)"
	@echo "  make lint-fix             - run ruff lint autofix (optional)"
	@echo "  make format               - run ruff formatter (optional)"
	@echo "  make format-check         - run ruff formatter checks (optional)"
	@echo "  make test                 - run pytest (optional)"
	@echo "  make sync-plans-from-issues - sync active/completed plans from GitHub issues"

lint:
	uv run ruff check src scripts tests

lint-fix:
	uv run ruff check src scripts tests --fix

format:
	uv run ruff format src scripts tests

format-check:
	uv run ruff format --check src scripts tests

test:
	uv run pytest -q

check-markdown-links:
	@./scripts/check-markdown-links.sh

check-harness-docs:
	@./scripts/check-harness-docs.sh

check-plan-issue-links:
	@./scripts/check-plan-issue-links.sh

check-python-test-typing-policy:
	@./scripts/check-python-test-typing-policy.sh

sync-plans-from-issues:
	@./scripts/sync-plans-from-issues.sh
