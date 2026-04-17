#!/usr/bin/env sh
set -eu

if ! command -v lychee >/dev/null 2>&1; then
  echo "lychee is not installed. Install it locally (for example: brew install lychee)." >&2
  exit 1
fi

set --
while IFS= read -r file; do
  set -- "$@" "$file"
done <<EOF_FILES
$(find . -type f -name '*.md' -not -path './.git/*' -not -path './.venv/*' -not -path './.pytest_cache/*' | sort)
EOF_FILES

if [ "$#" -eq 0 ]; then
  echo "No Markdown files found."
  exit 0
fi

lychee --offline --no-progress --include-fragments -- "$@"
