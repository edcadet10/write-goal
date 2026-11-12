#!/usr/bin/env bash
set -euo pipefail
WRITE_GOAL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
bash -n "$WRITE_GOAL_ROOT/install.sh" "$WRITE_GOAL_ROOT/scripts/check.sh"
if command -v python3 >/dev/null 2>&1; then
  exec python3 "$WRITE_GOAL_ROOT/scripts/check.py"
fi
exec python "$WRITE_GOAL_ROOT/scripts/check.py"
