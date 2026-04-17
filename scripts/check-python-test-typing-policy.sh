#!/usr/bin/env sh
set -eu

if rg -n --glob 'tests/**/*.py' '^[[:space:]]*import[[:space:]]+unittest\b|^[[:space:]]*from[[:space:]]+unittest\b|\bTestCase\b' tests >/dev/null; then
  echo "tests must use pytest style only; unittest usage detected" >&2
  rg -n --glob 'tests/**/*.py' '^[[:space:]]*import[[:space:]]+unittest\b|^[[:space:]]*from[[:space:]]+unittest\b|\bTestCase\b' tests >&2
  exit 1
fi

if rg -n --glob 'src/**/*.py' ':[[:space:]]*Any\b|->[[:space:]]*Any\b' src >/dev/null; then
  echo "public-facing APIs must not use typing.Any annotations" >&2
  rg -n --glob 'src/**/*.py' ':[[:space:]]*Any\b|->[[:space:]]*Any\b' src >&2
  exit 1
fi

if rg -n --glob 'tests/**/*.py' ':[[:space:]]*Any\b|->[[:space:]]*Any\b' tests >/dev/null; then
  approved_matches="$(rg -n --glob 'tests/**/*.py' ':[[:space:]]*Any\b|->[[:space:]]*Any\b' tests | rg -v 'agent-approved-any:' || true)"
  if [ -n "$approved_matches" ]; then
    echo "Any in tests requires explicit human approval marker 'agent-approved-any:' on the same line" >&2
    printf '%s\n' "$approved_matches" >&2
    exit 1
  fi
fi

echo "Python test and typing policy checks passed."
