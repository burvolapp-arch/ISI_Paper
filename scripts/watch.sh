#!/usr/bin/env bash
# scripts/watch.sh — Continuous build on file change (latexmk -pvc)
# Usage: ./scripts/watch.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "=== ISI_Paper: Watching for changes ==="
echo "    Press Ctrl+C to stop."
echo ""

# -pvc = preview continuously (recompile on change)
# -view=none = don't auto-open viewer (use VS Code / Skim instead)
latexmk -xelatex -pvc -view=none main.tex
