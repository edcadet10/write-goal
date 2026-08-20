#!/usr/bin/env bash
set -euo pipefail

WRITE_GOAL_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WRITE_GOAL_TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$WRITE_GOAL_TMP_DIR"' EXIT

bash -n "$WRITE_GOAL_ROOT/install.sh"

python3 - "$WRITE_GOAL_ROOT" <<'PY'
from html import unescape
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

root = Path(sys.argv[1])
skill = root / "skills/write-goal/SKILL.md"
text = skill.read_text()
parts = text.split("---", 2)
assert len(parts) == 3 and not parts[0].strip(), "SKILL.md needs YAML frontmatter"
frontmatter, body = parts[1], parts[2]
assert re.search(r"^name: write-goal$", frontmatter, re.MULTILINE)
assert re.search(r"^description:\s*\S", frontmatter, re.MULTILINE)
assert re.search(r"^allowed-tools:\s*\S", frontmatter, re.MULTILINE)
assert body.strip(), "SKILL.md needs an instruction body"
assert len(text.splitlines()) < 500, "SKILL.md must stay below 500 lines"

ET.parse(root / "assets/banner.svg")

documents = [
    root / "README.md",
    root / "CONTRIBUTING.md",
    root / "CODE_OF_CONDUCT.md",
    root / "SECURITY.md",
]
missing = []
for document in documents:
    content = document.read_text()
    targets = re.findall(r"!?\[[^]]*\]\(([^)]+)\)", content)
    targets += [a or b for a, b in re.findall(r'(?:href|src)="([^"]+)"|<(https?://[^>]+)>', content)]
    for raw_target in targets:
        target = unescape(raw_target).split("#", 1)[0]
        if not target or re.match(r"^(?:https?://|mailto:)", target):
            continue
        if not (root / target).exists():
            missing.append(f"{document.name}: {target}")
assert not missing, "missing local links: " + ", ".join(missing)
print(f"skill metadata, SVG, and {len(documents)} documents validated")
PY

for WRITE_GOAL_RUN in 1 2; do
  CLAUDE_CONFIG_DIR="$WRITE_GOAL_TMP_DIR/claude" \
    "$WRITE_GOAL_ROOT/install.sh" >"$WRITE_GOAL_TMP_DIR/install-$WRITE_GOAL_RUN.log"
done

cmp \
  "$WRITE_GOAL_ROOT/skills/write-goal/SKILL.md" \
  "$WRITE_GOAL_TMP_DIR/claude/skills/write-goal/SKILL.md"
test ! -d "$WRITE_GOAL_TMP_DIR/claude/skills/write-goal/write-goal"
test "$(find "$WRITE_GOAL_TMP_DIR/claude" -type f | wc -l)" -eq 1
grep -q '/write-goal' "$WRITE_GOAL_TMP_DIR/install-2.log"

printf 'write-goal checks passed\n'
