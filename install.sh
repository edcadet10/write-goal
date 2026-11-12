#!/usr/bin/env bash
# Backward-compatible entrypoint; Python also supports native Windows installs.
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
if command -v python3 >/dev/null 2>&1; then
  exec python3 "$SRC/install.py" "$@"
fi
exec python "$SRC/install.py" "$@"
