#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
MANUSCRIPT_DIR="$ROOT_DIR/docs/writing/manuscript"
OUTPUTS_DIR="$ROOT_DIR/outputs"
SUBMISSION_DIR="$MANUSCRIPT_DIR/submission"
MAIN_TEX="$MANUSCRIPT_DIR/main.tex"

if [ ! -f "$MAIN_TEX" ]; then
  echo "Missing main manuscript file: $MAIN_TEX" >&2
  exit 1
fi

rm -rf "$SUBMISSION_DIR"
mkdir -p "$SUBMISSION_DIR/figures" "$SUBMISSION_DIR/tables"

if command -v latexpand >/dev/null 2>&1; then
  echo "Flattening manuscript with latexpand"
  (
    cd "$MANUSCRIPT_DIR"
    latexpand main.tex
  ) > "$SUBMISSION_DIR/main.tex"
else
  echo "Warning: latexpand not found; copying main.tex without flattening" >&2
  cp "$MAIN_TEX" "$SUBMISSION_DIR/main.tex"
fi

sed \
  -e 's#../../../outputs/figures/#figures/#g' \
  -e 's#../../../outputs/tables/#tables/#g' \
  "$SUBMISSION_DIR/main.tex" > "$SUBMISSION_DIR/main.tex.tmp"
mv "$SUBMISSION_DIR/main.tex.tmp" "$SUBMISSION_DIR/main.tex"

if [ -f "$MANUSCRIPT_DIR/references.bib" ]; then
  cp "$MANUSCRIPT_DIR/references.bib" "$SUBMISSION_DIR/"
fi

if [ -d "$OUTPUTS_DIR/figures" ]; then
  cp -R "$OUTPUTS_DIR/figures/." "$SUBMISSION_DIR/figures/"
fi

if [ -d "$OUTPUTS_DIR/tables" ]; then
  cp -R "$OUTPUTS_DIR/tables/." "$SUBMISSION_DIR/tables/"
fi

find "$SUBMISSION_DIR" -name .gitkeep -delete

echo "Submission bundle prepared in docs/writing/manuscript/submission/"
echo "Review the bundle against the target journal requirements before submission."
