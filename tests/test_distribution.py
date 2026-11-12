"""Exercise real distribution archives, including untracked-file exclusion."""

import importlib.util
import json
import posixpath
from pathlib import Path
import re
import shutil
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("builder", ROOT / "scripts/build_plugin.py")
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class DistributionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        self.source = self.base / "source"
        for relative in builder.FILES:
            destination = self.source / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, destination)

    def test_reproducible_archive_contains_the_complete_skill_and_declared_assets(self):
        first, second = self.base / "first.zip", self.base / "second.zip"
        builder.build(self.source, first)
        builder.build(self.source, second)
        self.assertEqual(first.read_bytes(), second.read_bytes())
        with zipfile.ZipFile(first) as archive:
            self.assertIsNone(archive.testzip())
            self.assertEqual(set(archive.namelist()), set(builder.FILES.values()))
            for source, target in builder.FILES.items():
                path = self.source / source
                expected = path.read_bytes() if path.suffix == ".png" else path.read_text(encoding="utf-8").encode("utf-8")
                self.assertEqual(archive.read(target), expected)

    def test_private_files_caches_and_repository_metadata_are_excluded(self):
        for relative in (".env", "private-notes.txt", ".git/config", "__pycache__/local.pyc"):
            path = self.source / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("do not distribute", encoding="utf-8")
        output = self.base / "plugin.zip"
        builder.build(self.source, output)
        with zipfile.ZipFile(output) as archive:
            self.assertFalse(any(archive.read(name) == b"do not distribute" for name in archive.namelist()))

    def test_packaged_skill_can_resolve_its_adapter_reference(self):
        output = self.base / "plugin.zip"
        builder.build(self.source, output)
        with zipfile.ZipFile(output) as archive:
            skill_path = "skills/write-goal/SKILL.md"
            targets = re.findall(r"\[[^]]*\]\(([^)]+)\)", archive.read(skill_path).decode("utf-8"))
            self.assertTrue(targets, "The shared skill must expose its optional application adapter")
            for target in targets:
                resolved = posixpath.normpath(posixpath.join(posixpath.dirname(skill_path), target))
                self.assertIn(resolved, archive.namelist(), f"Missing adapter resource: {target}")

    def test_inconsistent_version_and_missing_asset_fail_before_output(self):
        manifest = self.source / ".codex-plugin/plugin.json"
        original = manifest.read_text(encoding="utf-8")
        changed = json.loads(original)
        changed["version"] = "99.0.0"
        manifest.write_text(json.dumps(changed), encoding="utf-8")
        output = self.base / "plugin.zip"
        with self.assertRaises(ValueError):
            builder.build(self.source, output)
        self.assertFalse(output.exists())
        manifest.write_text(original, encoding="utf-8")
        (self.source / "assets/icon.png").unlink()
        with self.assertRaises(ValueError):
            builder.build(self.source, output)

    def test_output_cannot_overwrite_the_source_checkout(self):
        with self.assertRaises(ValueError):
            builder.build(self.source, self.source / "plugin.zip")


if __name__ == "__main__":
    unittest.main()
