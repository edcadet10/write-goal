"""Exercise real installs in isolated directories, never the user's live skills."""

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import shutil
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("installer", ROOT / "install.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="write goal test ")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.skills = self.base / "skills with spaces"

    def run_cli(self, *arguments):
        return subprocess.run([sys.executable, str(ROOT / "install.py"), *arguments], capture_output=True, text=True, encoding="utf-8")

    def test_both_hosts_install_complete_package_and_repeat_without_changes(self):
        for host in ("claude", "codex"):
            with self.subTest(host=host):
                target = self.skills / host
                args = ("--target", host, "--dest", str(target))
                first = self.run_cli(*args)
                self.assertEqual(first.returncode, 0, first.stderr)
                destination = target / "write-goal"
                self.assertEqual(installer.manifest(destination), installer.manifest(installer.SOURCE))
                before = {p.relative_to(destination): p.stat().st_mtime_ns for p in destination.rglob("*") if p.is_file()}
                second = self.run_cli(*args)
                self.assertEqual(second.returncode, 0, second.stderr)
                self.assertIn("Already current", second.stdout)
                self.assertEqual(before, {p.relative_to(destination): p.stat().st_mtime_ns for p in destination.rglob("*") if p.is_file()})
                self.assertIn("/write-goal" if host == "claude" else "$write-goal", second.stdout)
                self.assertFalse((destination / "write-goal").exists())

    def test_environment_overrides_and_default_directories(self):
        with patch.dict(os.environ, {}, clear=True), patch.object(Path, "home", return_value=self.base):
            self.assertEqual(installer.default_skills_dir("claude"), self.base / ".claude/skills")
            self.assertEqual(installer.default_skills_dir("codex"), self.base / ".agents/skills")
        for host, variable in (("claude", "CLAUDE_CONFIG_DIR"), ("codex", "CODEX_HOME")):
            with self.subTest(host=host), patch.dict(os.environ, {variable: str(self.base / host)}):
                self.assertEqual(installer.default_skills_dir(host), self.base / host / "skills")
                result = subprocess.run([sys.executable, str(ROOT / "install.py"), "--target", host], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue((self.base / host / "skills/write-goal/SKILL.md").is_file())

    def test_existing_changes_are_preserved_unless_force_is_explicit(self):
        destination, _ = installer.install(installer.SOURCE, self.skills)
        (destination / "SKILL.md").write_text("local edits", encoding="utf-8")
        (destination / "obsolete.txt").write_text("old", encoding="utf-8")
        sibling = self.skills / "other-skill.txt"
        sibling.write_text("keep", encoding="utf-8")
        result = self.run_cli("--dest", str(self.skills))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((destination / "SKILL.md").read_text(), "local edits")
        result = self.run_cli("--dest", str(self.skills), "--force")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(installer.manifest(destination), installer.manifest(installer.SOURCE))
        self.assertEqual(sibling.read_text(), "keep")
        self.assertEqual(sorted(p.name for p in self.skills.iterdir()), ["other-skill.txt", "write-goal"])

    def test_failed_replacement_restores_previous_installation(self):
        destination, _ = installer.install(installer.SOURCE, self.skills)
        (destination / "SKILL.md").write_text("previous", encoding="utf-8")
        original = Path.rename

        def fail_staged(path, target):
            if path.name == "new":
                raise OSError("simulated rename failure")
            return original(path, target)

        with patch.object(Path, "rename", fail_staged), self.assertRaises(OSError):
            installer.install(installer.SOURCE, self.skills, force=True)
        self.assertEqual((destination / "SKILL.md").read_text(), "previous")

    def test_rejects_source_overlap_and_missing_source(self):
        with self.assertRaises(ValueError):
            installer.install(installer.SOURCE, installer.SOURCE.parent, force=True)
        with self.assertRaises(ValueError):
            installer.install(self.base / "missing", self.skills)
        self.assertFalse(self.skills.exists())

    def test_failed_rollback_preserves_recoverable_previous_copy(self):
        destination, _ = installer.install(installer.SOURCE, self.skills)
        (destination / "SKILL.md").write_text("previous", encoding="utf-8")
        original = Path.rename

        def fail_install_and_restore(path, target):
            if path.name in ("new", "previous"):
                raise OSError("simulated blocked destination")
            return original(path, target)

        with patch.object(Path, "rename", fail_install_and_restore), self.assertRaises(OSError):
            installer.install(installer.SOURCE, self.skills, force=True)
        previous_files = list(self.skills.rglob("SKILL.md"))
        self.assertTrue(previous_files, "Previous copy must survive a failed rollback")
        self.assertIn("previous", [path.read_text() for path in previous_files])

    def test_shell_wrapper_forwards_target_and_options(self):
        bash = shutil.which("bash")
        if os.name == "nt":
            git_bash = Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git/bin/bash.exe"
            bash = str(git_bash) if git_bash.is_file() else None
        if not bash:
            self.skipTest("Bash is not installed; native Python installation remains covered")
        result = subprocess.run([bash, "./install.sh", "--target", "codex", "--dest", str(self.skills)], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("$write-goal", result.stdout)
        self.assertEqual(installer.manifest(self.skills / "write-goal"), installer.manifest(installer.SOURCE))

    def test_rejects_file_destination(self):
        self.skills.mkdir()
        destination = self.skills / "write-goal"
        destination.write_text("keep", encoding="utf-8")
        with self.assertRaises(ValueError):
            installer.install(installer.SOURCE, self.skills, force=True)
        self.assertEqual(destination.read_text(), "keep")

    def test_rejects_symlink_destination_without_touching_target(self):
        self.skills.mkdir()
        external = self.base / "external"
        external.mkdir()
        (external / "keep").write_text("keep", encoding="utf-8")
        try:
            (self.skills / "write-goal").symlink_to(external, target_is_directory=True)
        except OSError:
            self.skipTest("Directory symlinks unavailable on this machine")
        with self.assertRaises(ValueError):
            installer.install(installer.SOURCE, self.skills, force=True)
        self.assertEqual((external / "keep").read_text(), "keep")

    def test_help_and_invalid_arguments_do_not_install(self):
        self.assertEqual(self.run_cli("--help").returncode, 0)
        for argument in ("--unknown", "--target=other"):
            result = self.run_cli(argument, "--dest", str(self.skills))
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(self.skills.exists())


if __name__ == "__main__":
    unittest.main()
