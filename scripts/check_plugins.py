#!/usr/bin/env python3
"""Smoke-test native plugin installation in temporary host profiles.

Requires installed Claude Code and Codex CLI. It installs from this checkout
or a supplied GitHub source, checks actual cached content against this checkout,
and never requests model inference.
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


def package_content(directory: Path) -> dict[str, bytes]:
    """Normalize text newlines across Git checkouts; preserve all other content."""
    return {
        path.relative_to(directory).as_posix(): (
            path.read_text(encoding="utf-8").encode("utf-8")
            if path.suffix in (".md", ".yaml", ".yml") else path.read_bytes()
        )
        for path in directory.rglob("*") if path.is_file()
    }


def run(command: list[str], env: dict[str, str]) -> str:
    result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", timeout=90)
    if result.returncode:
        raise RuntimeError(f"Native command failed ({result.returncode}): {' '.join(command[:4])}\n{result.stderr}")
    return result.stdout


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claude", default=shutil.which("claude"))
    parser.add_argument("--codex", default=shutil.which("codex.cmd") or shutil.which("codex"))
    parser.add_argument("--source", default=str(ROOT), help="Local root or GitHub owner/repo")
    parser.add_argument("--ref", help="Git ref for a GitHub source")
    args = parser.parse_args()
    if not args.claude or not args.codex:
        parser.error("Both native clients are required; use --claude and --codex to specify paths")
    if args.ref and Path(args.source).exists():
        parser.error("--ref requires a GitHub source")
    source = ROOT / "skills/write-goal/SKILL.md"
    expected_package = package_content(source.parent)
    report = {"skill_sha256_lf": hashlib.sha256(expected_package["SKILL.md"]).hexdigest(), "hosts": {}}
    with tempfile.TemporaryDirectory(prefix="write-goal-native-") as temporary:
        for host, executable in (("claude", args.claude), ("codex", args.codex)):
            env = os.environ.copy()
            profile = Path(temporary) / host
            profile.mkdir()
            env["CLAUDE_CONFIG_DIR" if host == "claude" else "CODEX_HOME"] = str(profile)
            version = run([executable, "--version"], env).strip()
            if host == "claude":
                marketplace = args.source + ("#" + args.ref if args.ref else "")
                run([executable, "plugin", "install", "write-goal", "--marketplace", marketplace, "--json"], env)
                inventory = run([executable, "plugin", "details", "write-goal"], env)
                assert "Skills (1)" in inventory and "write-goal" in inventory, inventory
            else:
                ref_args = ["--ref", args.ref] if args.ref else []
                run([executable, "plugin", "marketplace", "add", args.source, *ref_args, "--json"], env)
                run([executable, "plugin", "add", "write-goal@write-goal", "--json"], env)
                inventory = json.loads(run([executable, "plugin", "list", "--json", "--marketplace", "write-goal"], env))
                installed = inventory["installed"]
                assert len(installed) == 1 and installed[0]["enabled"], inventory
                assert installed[0]["pluginId"] == "write-goal@write-goal", inventory
            cached = list((profile / "plugins/cache").rglob("SKILL.md"))
            assert len(cached) == 1, f"{host}: expected exactly one cached skill, got {len(cached)}"
            assert package_content(cached[0].parent) == expected_package, f"{host}: installed package content differs from source"
            report["hosts"][host] = {"version": version, "enabled": True, "cached_package_content_matches": True}
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
