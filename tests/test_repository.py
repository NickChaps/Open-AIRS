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

    def test_project_readmes_explain_the_model_visually(self):
        concept_links = {
            "README.md": "docs/en/concepts.md",
            "README.fr.md": "docs/fr/concepts.md",
        }
        for name, concept_link in concept_links.items():
            body = (ROOT / name).read_text(encoding="utf-8")
            with self.subTest(path=name):
                self.assertGreaterEqual(body.count("```mermaid"), 3)
                self.assertIn(concept_link, body)

    def test_every_pack_has_illustrated_english_and_french_guides(self):
        version_dirs = sorted(path.parent for path in ROOT.glob("packs/*/*/pack.json"))
        self.assertGreaterEqual(len(version_dirs), 6)
        for directory in version_dirs:
            for name in ["README.md", "README.fr.md"]:
                path = directory / name
                with self.subTest(path=path):
                    self.assertTrue(path.exists())
                    self.assertIn("```mermaid", path.read_text(encoding="utf-8"))

    def test_worked_examples_show_inputs_outputs_and_review_records(self):
        for folder in ["ai-governance", "contract-review"]:
            directory = ROOT / "examples" / folder
            with self.subTest(folder=folder):
                self.assertTrue((directory / "extraction.json").exists())
                self.assertTrue((directory / "assessment-note.json").exists())
                self.assertTrue((directory / "review.json").exists())
            for name in ["README.md", "README.fr.md"]:
                path = directory / name
                with self.subTest(path=path):
                    body = path.read_text(encoding="utf-8")
                    self.assertIn("```mermaid", body)
                    self.assertIn("extraction.json", body)
                    self.assertIn("assessment-note.json", body)
                    self.assertIn("review.json", body)
                    self.assertGreaterEqual(body.count("| ---"), 2)

    def test_public_object_type_is_skill(self):
        paths = [
            ROOT / "src/air_framework/validation.py",
            ROOT / "spec/schemas/inventory.schema.json",
            ROOT / "spec/schemas/pack.schema.json",
            ROOT / "examples/ai-governance/inventory.json",
            ROOT / "packs/eu-ai-act/1.0.0/pack.json",
        ]
        for path in paths:
            with self.subTest(path=path):
                body = path.read_text(encoding="utf-8")
                self.assertNotIn("agent_skill", body)
                self.assertIn("skill", body)

    def test_public_markdown_avoids_recurring_ai_tells(self):
        false_contrasts = re.compile(
            r"\b(?:not just|not only|rather than|instead of|pas seulement|"
            r"pas uniquement|plutôt que|au lieu de)\b|"
            r"^#{1,6} .*[,;:]\s*(?:not|pas)\b",
            re.IGNORECASE | re.MULTILINE,
        )
        for path in ROOT.rglob("*.md"):
            if ".git" in path.parts:
                continue
            body = path.read_text(encoding="utf-8")
            with self.subTest(path=path):
                self.assertNotIn("—", body)
                self.assertIsNone(false_contrasts.search(body))


if __name__ == "__main__":
    unittest.main()
