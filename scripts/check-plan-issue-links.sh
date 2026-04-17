#!/usr/bin/env sh
set -eu

ACTIVE_DIR="docs/exec-plans/active"
COMPLETED_DIR="docs/exec-plans/completed"

tmp_file="$(mktemp)"
trap 'rm -f "$tmp_file"' EXIT INT TERM

scan_dir() {
  dir="$1"
  if [ ! -d "$dir" ]; then
    return
  fi

  for file in "$dir"/*.md; do
    [ -f "$file" ] || continue
    [ "$(basename "$file")" = "README.md" ] && continue

    issue_lines_count="$(grep -c '^Issue:' "$file" || true)"
    if [ "$issue_lines_count" -gt 1 ]; then
      echo "Plan has multiple Issue lines: $file" >&2
      exit 1
    fi

    if [ "$issue_lines_count" -eq 1 ]; then
      issue_url="$(grep '^Issue:' "$file" | sed -E 's/^Issue:[[:space:]]*//')"
      if ! printf '%s\n' "$issue_url" | grep -Eq '^https://github\.com/.+/issues/[0-9]+/?$'; then
        echo "Plan has malformed Issue URL in $file: $issue_url" >&2
        exit 1
      fi
      printf '%s|%s\n' "$issue_url" "$file" >>"$tmp_file"
    fi
  done
}

scan_dir "$ACTIVE_DIR"
scan_dir "$COMPLETED_DIR"

if [ ! -s "$tmp_file" ]; then
  echo "Plan issue link checks passed (no linked issues found)."
  exit 0
fi

duplicates="$(awk -F'|' '{count[$1]++; files[$1]=files[$1] "\n  - " $2} END {for (u in count) if (count[u] > 1) print u files[u]}' "$tmp_file")"

if [ -n "$duplicates" ]; then
  echo "Duplicate issue links found across plan files:" >&2
  echo "$duplicates" >&2
  exit 1
fi

echo "Plan issue link checks passed."
