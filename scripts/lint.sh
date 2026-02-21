#!/usr/bin/env bash
# scripts/lint.sh — Run chktex linter on all .tex files (advisory only)
# Usage: ./scripts/lint.sh
# Exit code: always 0 (lint is advisory, never blocks)
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "=== ISI_Paper: Running chktex lint ==="

if ! command -v chktex &>/dev/null; then
  echo "    chktex not found. Install via TeX Live (ships with it) or:"
  echo "      brew install chktex"
  echo "    Skipping lint."
  exit 0
fi

# Suppressed warnings (common false positives with modern LaTeX):
#   1  — Command terminated with space
#   3  — Enclose previous parenthesis with {}
#   6  — No italic correction (\/) found
#   8  — Wrong length of dash
#  24  — Delete this space to maintain correct pagereferences
#  36  — Vertical rules in tables
SUPPRESS="-n1 -n3 -n6 -n8 -n24 -n36"

echo ""
ISSUES=0

for f in main.tex preamble/*.tex sections/*.tex; do
  if [[ -f "$f" ]]; then
    OUTPUT=$(chktex -q $SUPPRESS "$f" 2>&1)
    if [[ -n "$OUTPUT" ]]; then
      echo "--- $f ---"
      echo "$OUTPUT"
      echo ""
      ISSUES=$((ISSUES + 1))
    fi
  fi
done

if [[ $ISSUES -eq 0 ]]; then
  echo "    No lint issues found."
else
  echo "    Found issues in $ISSUES file(s). These are advisory only."
fi

echo ""
echo "=== Lint complete (advisory — never blocks build) ==="
exit 0
