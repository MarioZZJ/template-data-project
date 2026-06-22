#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
MANUSCRIPT_DIR="$ROOT_DIR/docs/writing/manuscript"
SUBMISSION_DIR="$MANUSCRIPT_DIR/submission"
MAIN_TEX="$MANUSCRIPT_DIR/main.tex"

rm -rf "$SUBMISSION_DIR"/*
mkdir -p "$SUBMISSION_DIR"

if [ ! -f "$MAIN_TEX" ]; then
  echo "Missing main manuscript file: $MAIN_TEX"
  exit 1
fi

if command -v latexpand >/dev/null 2>&1; then
  echo "Flattening manuscript with latexpand"
  latexpand "$MAIN_TEX" > "$SUBMISSION_DIR/main.tex"
else
  echo "Warning: latexpand not found; copying source files as fallback"
  cp "$MAIN_TEX" "$SUBMISSION_DIR/main.tex"
fi

cp -f "$MANUSCRIPT_DIR/references.bib" "$SUBMISSION_DIR/"
mkdir -p "$SUBMISSION_DIR/figures" "$SUBMISSION_DIR/tables"
cp -R "$MANUSCRIPT_DIR/figures/"* "$SUBMISSION_DIR/figures/" || true
cp -R "$MANUSCRIPT_DIR/tables/"* "$SUBMISSION_DIR/tables/" || true

echo

echo "Submission bundle prepared in docs/writing/manuscript/submission/"
echo "Some submission systems require all source files at the same folder level."
