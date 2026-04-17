#!/usr/bin/env sh
set -eu

required_files="
AGENTS.md
ARCHITECTURE.md
SKILL.md
docs/PLANS.md
docs/QUALITY_SCORE.md
docs/RELIABILITY.md
docs/SECURITY.md
docs/PRODUCT_SENSE.md
docs/DESIGN.md
docs/FRONTEND.md
docs/design-docs/index.md
docs/design-docs/core-beliefs.md
docs/design-docs/harness-architecture.md
docs/design-docs/review-loop-and-autonomy.md
docs/product-specs/index.md
docs/product-specs/agent-harness-contract.md
docs/references/index.md
docs/exec-plans/active/README.md
docs/exec-plans/completed/README.md
docs/exec-plans/tech-debt-tracker.md
"

missing=0
for file in $required_files; do
  if [ ! -f "$file" ]; then
    echo "Missing required harness file: $file" >&2
    missing=1
  fi
done

if [ "$missing" -ne 0 ]; then
  exit 1
fi

check_link() {
  src="$1"
  needle="$2"

  if ! grep -q "$needle" "$src"; then
    echo "Required reference '$needle' missing in $src" >&2
    return 1
  fi
  return 0
}

status=0
check_link "AGENTS.md" "docs/design-docs/index.md" || status=1
check_link "AGENTS.md" "docs/product-specs/index.md" || status=1
check_link "AGENTS.md" "docs/references/index.md" || status=1
check_link "AGENTS.md" "ARCHITECTURE.md" || status=1
check_link "AGENTS.md" "Python Test and Typing Policy" || status=1
check_link "AGENTS.md" 'Use `pytest` style tests only' || status=1
check_link "AGENTS.md" 'Prefer simple, readable type annotations by default' || status=1
check_link "AGENTS.md" 'must ask for human approval before introducing it' || status=1
check_link "AGENTS.md" 'Public-facing APIs must not use `Any`' || status=1
check_link "ARCHITECTURE.md" "docs/" || status=1
check_link "docs/PLANS.md" "docs/exec-plans/active/README.md" || status=1
check_link "docs/PLANS.md" "docs/exec-plans/completed/README.md" || status=1
check_link "docs/PLANS.md" "make sync-plans-from-issues" || status=1
check_link "docs/product-specs/agent-harness-contract.md" 'Python tests must use `pytest` style only' || status=1
check_link "docs/product-specs/agent-harness-contract.md" 'Prefer simple, readable type annotations by default' || status=1
check_link "docs/product-specs/agent-harness-contract.md" 'typing.Any` is an exception path that requires explicit human approval' || status=1
check_link "docs/product-specs/agent-harness-contract.md" 'Public-facing APIs must not use `Any`' || status=1

if [ "$status" -ne 0 ]; then
  exit 1
fi

echo "Harness documentation checks passed."
