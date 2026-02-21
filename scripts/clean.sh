#!/usr/bin/env bash
# scripts/clean.sh — Remove all build artefacts
# Usage: ./scripts/clean.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "=== ISI_Paper: Cleaning build artefacts ==="

latexmk -C 2>/dev/null || true

# Also nuke output dir contents (except .gitkeep if present)
if [[ -d "output" ]]; then
  find output -type f ! -name '.gitkeep' -delete 2>/dev/null || true
fi

echo "=== Clean complete ==="
