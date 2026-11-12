#!/usr/bin/env python3
"""Install the GitHub-managed skill with Python 3.10+; no third-party packages."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import sys
import tempfile


SOURCE = Path(__file__).resolve().parent / "skills" / "write-goal"


def default_skills_dir(target: str) -> Path:
    if target == "claude":
        return Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude") / "skills"
    if os.environ.get("CODEX_HOME"):
        return Path(os.environ["CODEX_HOME"]) / "skills"
    return Path.home() / ".agents" / "skills"


def manifest(directory: Path) -> dict[str, bytes]:
    files = {}
    for path in directory.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"Refusing a symbolic link inside skill: {path}")
        if path.is_file():
            files[path.relative_to(directory).as_posix()] = path.read_bytes()
    return files


def install(source: Path, skills_dir: Path, *, force: bool = False) -> tuple[Path, bool]:
    """Stage the full package; leave an existing, different skill alone by default."""
    destination = skills_dir.expanduser().absolute() / "write-goal"
    if destination.is_symlink():
        raise ValueError(f"Refusing symbolic-link destination: {destination}")
    resolved = destination.resolve()
    source = source.resolve()
    if resolved.is_relative_to(source) or source.is_relative_to(resolved):
        raise ValueError("Source and destination must not overlap")
    if not (source / "SKILL.md").is_file():
        raise ValueError("Source is missing SKILL.md")
    source_files = manifest(source)
    if destination.exists():
        if not destination.is_dir():
            raise ValueError(f"Destination is not a directory: {destination}")
        if manifest(destination) == source_files:
            return destination, False
        if not force:
            raise ValueError(f"Existing skill differs: {destination}; review it before using --force")

    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".write-goal-", dir=destination.parent) as temporary:
        staging = Path(temporary) / "new"
        shutil.copytree(source, staging)
        backup = None
        if destination.exists():
            # A separate directory survives even if both installation and
            # rollback fail (for example, another process locks the target).
            backup = Path(tempfile.mkdtemp(prefix=".write-goal-backup-", dir=destination.parent)) / "previous"
            destination.rename(backup)
        try:
            staging.rename(destination)
        except OSError:
            if backup is not None:
                try:
                    backup.rename(destination)
                except OSError as restore_error:
                    raise OSError(f"Rollback failed; previous skill preserved at {backup}") from restore_error
                backup.parent.rmdir()
            raise
        if backup is not None:
            shutil.rmtree(backup.parent)
    return destination, True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=("claude", "codex"), default="claude")
    parser.add_argument("--dest", type=Path, help="Skills parent directory; appends write-goal")
    parser.add_argument("--force", action="store_true", help="Replace a reviewed, different installation")
    args = parser.parse_args(argv)
    try:
        destination, changed = install(SOURCE, args.dest if args.dest is not None else default_skills_dir(args.target), force=args.force)
    except (OSError, ValueError) as error:
        print(f"Installation failed: {error}", file=sys.stderr)
        return 1
    print(f"{'Installed' if changed else 'Already current'}: {destination}")
    invocation = "/write-goal" if args.target == "claude" else "$write-goal"
    print(f"Invoke with {invocation} <your rough task>. The skill drafts; it does not start a loop.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
