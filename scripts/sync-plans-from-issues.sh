#!/usr/bin/env sh
set -eu

if ! command -v gh >/dev/null 2>&1; then
  echo "gh is not installed. Install GitHub CLI first." >&2
  exit 1
fi

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is not installed. Install uv first." >&2
  exit 1
fi

ACTIVE_DIR="docs/exec-plans/active"
COMPLETED_DIR="docs/exec-plans/completed"
ISSUE_LABEL="${AGENTOME_ISSUE_LABEL:-planning}"

mkdir -p "$ACTIVE_DIR" "$COMPLETED_DIR"

open_issues_json="$(mktemp)"
closed_issues_json="$(mktemp)"
trap 'rm -f "$open_issues_json" "$closed_issues_json"' EXIT INT TERM

gh issue list --state open --limit 200 --json number,title,body,url,state,updatedAt,labels --label "$ISSUE_LABEL" >"$open_issues_json"

if [ "$(uv run python -c 'import json,sys; print(len(json.load(open(sys.argv[1]))))' "$open_issues_json")" -eq 0 ]; then
  gh issue list --state open --limit 200 --json number,title,body,url,state,updatedAt,labels >"$open_issues_json"
fi

gh issue list --state closed --limit 200 --json number,title,body,url,state,updatedAt,labels >"$closed_issues_json"

uv run python - "$ACTIVE_DIR" "$COMPLETED_DIR" "$open_issues_json" "$closed_issues_json" <<'PY'
from __future__ import annotations

import datetime as dt
import json
import pathlib
import re
import shutil
import sys

ACTIVE_DIR = pathlib.Path(sys.argv[1])
COMPLETED_DIR = pathlib.Path(sys.argv[2])
OPEN_ISSUES_PATH = pathlib.Path(sys.argv[3])
CLOSED_ISSUES_PATH = pathlib.Path(sys.argv[4])

ISSUE_RE = re.compile(r"^Issue:\s*(https://github\.com/.+/issues/(\d+)/?)\s*$", re.MULTILINE)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "issue"


def find_issue_reference(path: pathlib.Path) -> tuple[str, str] | None:
    text = path.read_text(encoding="utf-8")
    match = ISSUE_RE.search(text)
    if not match:
        return None
    return (match.group(1), match.group(2))


def collect_plan_index() -> tuple[dict[str, pathlib.Path], dict[str, pathlib.Path]]:
    by_url: dict[str, pathlib.Path] = {}
    by_number: dict[str, pathlib.Path] = {}

    for directory in (ACTIVE_DIR, COMPLETED_DIR):
        for path in sorted(directory.glob("*.md")):
            if path.name == "README.md":
                continue
            ref = find_issue_reference(path)
            if ref is None:
                continue
            url, number = ref
            by_url[url] = path
            by_number[number] = path
    return by_url, by_number


def issue_plan_content(issue: dict[str, object]) -> str:
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    body = (issue.get("body") or "").strip()
    body_block = body if body else "No issue body provided."
    return "\n".join(
        [
            f"# Issue {issue['number']}: {issue['title']}",
            "",
            f"Issue: {issue['url']}",
            f"Issue Number: {issue['number']}",
            f"Issue State: {issue['state']}",
            f"Issue Updated: {issue['updatedAt']}",
            f"Last Synced: {now}",
            "",
            "## Objective",
            body_block,
            "",
            "## Acceptance Checks",
            "- [ ] Define at least one concrete success check before edits.",
            "",
            "## Implementation Steps",
            "- [ ] Decompose work into the smallest coherent patch.",
            "- [ ] Run checks and capture validation evidence.",
            "",
            "## Risks and Unknowns",
            "- Pending issue triage.",
            "",
            "## Decision Log",
            "- Initial plan scaffold created from GitHub issue sync.",
            "",
        ]
    )


open_issues = json.loads(OPEN_ISSUES_PATH.read_text(encoding="utf-8"))
closed_issues = json.loads(CLOSED_ISSUES_PATH.read_text(encoding="utf-8"))

closed_numbers = {str(issue["number"]) for issue in closed_issues}

by_url, by_number = collect_plan_index()

for number, path in list(by_number.items()):
    if path.parent == ACTIVE_DIR and number in closed_numbers:
        destination = COMPLETED_DIR / path.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(path, destination)

by_url, by_number = collect_plan_index()

for issue in open_issues:
    number = str(issue["number"])
    url = str(issue["url"])
    existing_path = by_url.get(url) or by_number.get(number)

    if existing_path is None:
        filename = f"issue-{number}-{slugify(str(issue['title']))}.md"
        existing_path = ACTIVE_DIR / filename
    elif existing_path.parent == COMPLETED_DIR:
        existing_path = ACTIVE_DIR / existing_path.name

    existing_path.parent.mkdir(parents=True, exist_ok=True)
    existing_path.write_text(issue_plan_content(issue), encoding="utf-8")

print("Plan sync complete.")
PY
