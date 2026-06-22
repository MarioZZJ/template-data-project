#!/usr/bin/env bash
set -euo pipefail

if [ -n "${GITHUB_WORKSPACE:-}" ]; then
  git config --global --add safe.directory "$GITHUB_WORKSPACE" >/dev/null 2>&1 || true
fi

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

MAIN_TEX="${MAIN_TEX:-docs/writing/manuscript/main.tex}"
BUILD_DIR="${BUILD_DIR:-docs/writing/manuscript/build}"
OUTPUT_PDF="${OUTPUT_PDF:-$BUILD_DIR/manuscript-diff.pdf}"

if ! command -v git-latexdiff >/dev/null 2>&1; then
  echo "git-latexdiff not found. Install TeX Live tools that provide git-latexdiff."
  exit 127
fi

if [ -z "${BASE_REF:-}" ]; then
  if git rev-parse --abbrev-ref --symbolic-full-name '@{u}' >/dev/null 2>&1; then
    BASE_REF="$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}')"
  elif git rev-parse --verify origin/master >/dev/null 2>&1; then
    BASE_REF="origin/master"
  else
    BASE_REF="HEAD~1"
  fi
fi

HEAD_REF="${HEAD_REF:-HEAD}"

mkdir -p "$BUILD_DIR"

echo "Building manuscript diff:"
echo "  base: $BASE_REF"
echo "  head: $HEAD_REF"
echo "  main: $MAIN_TEX"
echo "  out:  $OUTPUT_PDF"

git-latexdiff \
  --no-view \
  --whole-tree \
  --latexmk \
  --ignore-latex-errors \
  --main "$MAIN_TEX" \
  -o "$OUTPUT_PDF" \
  "$BASE_REF" "$HEAD_REF"
