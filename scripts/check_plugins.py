#!/usr/bin/env python3
"""Smoke-test native plugin installation in temporary host profiles.

Requires installed Claude Code and Codex CLI. It installs from this checkout,
checks the actual cached skill bytes, and never requests model inference.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], env: dict[str, str]) -> str:
    result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", timeout=90)
    if result.returncode:
        raise RuntimeError(f"Native command failed ({result.returncode}): {' '.join(command[:4])}\n{result.stderr}")
    return result.stdout


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claude", default=shutil.which("claude"))
    parser.add_argument("--codex", default=shutil.which("codex.cmd") or shutil.which("codex"))
    args = parser.parse_args()
    if not args.claude or not args.codex:
        parser.error("Both native clients are required; use --claude and --codex to specify paths")
    source = ROOT / "skills/write-goal/SKILL.md"
    report = {"skill_sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "hosts": {}}
    with tempfile.TemporaryDirectory(prefix="write-goal-native-") as temporary:
        for host, executable in (("claude", args.claude), ("codex", args.codex)):
            env = os.environ.copy()
            profile = Path(temporary) / host
            profile.mkdir()
            env["CLAUDE_CONFIG_DIR" if host == "claude" else "CODEX_HOME"] = str(profile)
            version = run([executable, "--version"], env).strip()
            run([executable, "plugin", "marketplace", "add", str(ROOT), "--json"], env)
            run([executable, "plugin", "install" if host == "claude" else "add", "write-goal@write-goal", "--json"], env)
            if host == "claude":
                inventory = run([executable, "plugin", "details", "write-goal"], env)
                assert "Skills (1)" in inventory and "write-goal" in inventory, inventory
            else:
                inventory = json.loads(run([executable, "plugin", "list", "--json", "--marketplace", "write-goal"], env))
                installed = inventory["installed"]
                assert len(installed) == 1 and installed[0]["enabled"], inventory
                assert installed[0]["pluginId"] == "write-goal@write-goal", inventory
            cached = list((profile / "plugins/cache").rglob("SKILL.md"))
            assert len(cached) == 1, f"{host}: expected exactly one cached skill, got {len(cached)}"
            assert cached[0].read_bytes() == source.read_bytes(), f"{host}: installed skill differs from source"
            report["hosts"][host] = {"version": version, "enabled": True, "cached_skill_matches": True}
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
