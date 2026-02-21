#!/usr/bin/env bash
# scripts/build.sh — Full build (XeLaTeX + Biber via latexmk)
# Usage: ./scripts/build.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "=== ISI_Paper: Building PDF ==="
echo "    Engine:    xelatex"
echo "    Bib:       biber"
echo "    Output:    output/"
echo ""

latexmk -xelatex main.tex

# Quality gate: check for remaining undefined references
LOG="output/main.log"
if [[ -f "$LOG" ]]; then
  if grep -qiE 'undefined references|Citation .* undefined|Reference .* undefined' "$LOG"; then
    echo ""
    echo "*** QUALITY GATE FAILED ***"
    echo "    Undefined references or citations remain."
    echo "    Check: $LOG"
    exit 1
  fi
fi

echo ""
echo "=== Build complete: output/main.pdf ==="
