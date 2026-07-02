#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "usage: $0 OUTPUT_PDF" >&2
  exit 2
fi

: "${BASE_SHA:?BASE_SHA is required}"
: "${HEAD_SHA:?HEAD_SHA is required}"

command -v git-latexdiff >/dev/null
command -v pdfinfo >/dev/null

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

mkdir -p "$(dirname "$1")"
OUT_DIR="$(cd "$(dirname "$1")" && pwd)"
OUT="$OUT_DIR/$(basename "$1")"

if [[ -n "${GITHUB_WORKSPACE:-}" ]]; then
  git config --global --add safe.directory "$GITHUB_WORKSPACE"
fi

BASE_COMMIT="$(git rev-parse "${BASE_SHA}^{commit}")"
HEAD_COMMIT="$(git rev-parse "${HEAD_SHA}^{commit}")"

git-latexdiff \
  --no-view \
  --ignore-makefile \
  --latexmk \
  --build-dir docs/writing/manuscript/build \
  --main docs/writing/manuscript/main.tex \
  --prepare 'cp .latexmkrc docs/writing/manuscript/.latexmkrc' \
  --output "$OUT" \
  "$BASE_COMMIT" "$HEAD_COMMIT" \
  --type=UNDERLINE \
  --graphics-markup=none \
  --disable-citation-markup \
  --math-markup=whole

test -s "$OUT"
pdfinfo "$OUT"
