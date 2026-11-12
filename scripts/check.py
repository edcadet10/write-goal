#!/usr/bin/env python3
"""Portable repository validation. Behavioral model evaluation is separate."""

from html import unescape
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]


def validate() -> None:
    text = (ROOT / "skills/write-goal/SKILL.md").read_text(encoding="utf-8")
    parts = text.split("---", 2)
    assert len(parts) == 3 and not parts[0].strip(), "SKILL.md needs YAML frontmatter"
    frontmatter, body = parts[1:]
    assert re.search(r"^name: write-goal$", frontmatter, re.MULTILINE)
    assert re.search(r"^description:\s*\S", frontmatter, re.MULTILINE)
    assert body.strip() and len(text.splitlines()) < 500
    assert not re.search(r"\b(?:TODO|FIXME)\b", text), "Unfinished skill placeholder"
    ET.parse(ROOT / "assets/banner.svg")
    documents = list(ROOT.glob("*.md")) + list((ROOT / "skills/write-goal").rglob("*.md"))
    for document in documents:
        content = document.read_text(encoding="utf-8")
        targets = re.findall(r"!?\[[^]]*\]\(([^)]+)\)", content)
        targets += [a or b for a, b in re.findall(r'(?:href|src)="([^"]+)"|<(https?://[^>]+)>', content)]
        for raw_target in targets:
            target = unescape(raw_target).split("#", 1)[0]
            if not target or re.match(r"^(?:https?://|mailto:)", target):
                continue
            assert (document.parent / unquote(target)).exists(), f"Missing local link: {document.name}: {target}"
    print(f"Skill structure, SVG, and links in {len(documents)} documents validated", flush=True)


if __name__ == "__main__":
    validate()
    result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT)
    raise SystemExit(result.returncode)
