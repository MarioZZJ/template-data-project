#!/usr/bin/env bash
set -euo pipefail

missing=0

check_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing required command: $cmd"
    missing=1
  else
    echo "Found $cmd: $(command -v "$cmd")"
  fi
}

check_cmd latexmk
check_cmd pdflatex
check_cmd bibtex

if command -v kpsewhich >/dev/null 2>&1; then
  if kpsewhich elsarticle.cls >/dev/null 2>&1; then
    echo "Found elsarticle.cls"
  else
    echo "Missing elsarticle.cls"
    missing=1
  fi
else
  echo "Missing required command: kpsewhich"
  missing=1
fi

if [ "$missing" -ne 0 ]; then
  cat <<'MSG'

TeX environment is not ready.

Install a TeX distribution that includes latexmk, pdflatex, bibtex, and elsarticle.

Common options:
- macOS: MacTeX or BasicTeX plus required packages
- Linux: TeX Live packages from the system package manager
- Windows: TeX Live or MiKTeX
- Online fallback: Overleaf with an Elsevier elsarticle template

After installation, run:

  make init-tex
  make manuscript

MSG
  exit 1
fi

echo "TeX environment is ready."
