"""Check cross-host package identity and catalog paths without native clients."""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


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


if __name__ == "__main__":
    unittest.main()
