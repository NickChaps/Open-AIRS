# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


class RepositoryIntegrityTests(unittest.TestCase):
    def test_every_committed_json_file_parses(self):
        paths = [path for path in ROOT.rglob("*.json") if "reports" not in path.parts]
        self.assertGreaterEqual(len(paths), 15)
        for path in paths:
            with self.subTest(path=path):
                json.loads(path.read_text(encoding="utf-8"))

    def test_relative_markdown_links_resolve(self):
        for path in ROOT.rglob("*.md"):
            if ".git" in path.parts:
                continue
            for raw_target in MARKDOWN_LINK.findall(path.read_text(encoding="utf-8")):
                target = raw_target.split("#", 1)[0].strip()
                if not target or "://" in target or target.startswith(("mailto:", "<")):
                    continue
                with self.subTest(path=path, target=raw_target):
                    self.assertTrue((path.parent / target).resolve().exists())

    def test_cc_by_documentation_is_marked(self):
        for folder in [ROOT / "docs", ROOT / "spec"]:
            for path in folder.rglob("*.md"):
                with self.subTest(path=path):
                    self.assertTrue(
                        path.read_text(encoding="utf-8").startswith(
                            "<!-- SPDX-License-Identifier: CC-BY-4.0 -->"
                        )
                    )


if __name__ == "__main__":
    unittest.main()
