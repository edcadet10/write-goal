"""Check cross-host package identity and catalog paths without native clients."""

import json
import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("native_check", ROOT / "scripts/check_plugins.py")
native_check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(native_check)


class PluginPackageTests(unittest.TestCase):
    def test_hosts_publish_the_same_identity_and_version(self):
        claude = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        codex = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        for field in ("name", "version", "description", "author", "repository", "license"):
            self.assertEqual(claude[field], codex[field], field)
        self.assertRegex(claude["version"], r"^\d+\.\d+\.\d+$")
        self.assertEqual(claude["author"]["url"], "https://github.com/edcadet10")

    def test_marketplace_resolves_to_the_existing_skill(self):
        marketplace = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        self.assertEqual(len(marketplace["plugins"]), 1)
        entry = marketplace["plugins"][0]
        plugin_root = (ROOT / entry["source"]).resolve()
        self.assertTrue(plugin_root.is_relative_to(ROOT))
        plugin = json.loads((plugin_root / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(entry["name"], plugin["name"])
        codex = json.loads((plugin_root / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
        skill = plugin_root / codex["skills"] / "write-goal/SKILL.md"
        self.assertEqual(skill.resolve(), ROOT / "skills/write-goal/SKILL.md")

    def test_content_comparison_accepts_newlines_and_detects_changed_or_missing_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            first, second = Path(temporary) / "first", Path(temporary) / "second"
            first.mkdir()
            second.mkdir()
            (first / "SKILL.md").write_bytes(b"one\ntwo\n")
            (second / "SKILL.md").write_bytes(b"one\r\ntwo\r\n")
            self.assertEqual(native_check.package_content(first), native_check.package_content(second))
            (second / "SKILL.md").write_bytes(b"one\nchanged\n")
            self.assertNotEqual(native_check.package_content(first), native_check.package_content(second))
            (second / "SKILL.md").write_bytes(b"one\ntwo\n")
            (first / "openai.yaml").write_bytes(b"interface: {}\n")
            self.assertNotEqual(native_check.package_content(first), native_check.package_content(second))


if __name__ == "__main__":
    unittest.main()
