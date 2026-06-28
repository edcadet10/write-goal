#!/usr/bin/env bash
# Install the `write-goal` Claude Code skill.
set -euo pipefail

CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
SRC="$(cd "$(dirname "$0")" && pwd)"

echo "Installing write-goal into: $CLAUDE_DIR"
mkdir -p "$CLAUDE_DIR/skills"

cp -r "$SRC/skills/write-goal" "$CLAUDE_DIR/skills/"
echo "  ok   skill  ->  $CLAUDE_DIR/skills/write-goal/SKILL.md"

cat <<'SNIP'

Installed. Call it in Claude Code with:

  /write-goal <your rough task>

You get back one copy-paste /goal line with a measurable end state, a check
whose output lands in the transcript, the constraints to hold, and a turn cap
so it can't loop forever. No hook to wire up — run it whenever you're about to
kick off a "keep going until X is true" loop.
SNIP
