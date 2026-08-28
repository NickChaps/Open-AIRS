# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import re
import unittest
from copy import deepcopy
from pathlib import Path

from air_framework.errors import ValidationError
from air_framework.validation import validate_inventory, validate_pack

ROOT = Path(__file__).resolve().parents[1]


class PackConformanceTests(unittest.TestCase):
    def test_every_pack_validates(self):
        pack_paths = sorted(ROOT.glob("packs/*/*/pack.json"))
        self.assertGreaterEqual(len(pack_paths), 6)
        for path in pack_paths:
            with self.subTest(path=path):
                validate_pack(json.loads(path.read_text(encoding="utf-8")))

    def test_every_example_inventory_validates(self):
        paths = sorted(ROOT.glob("examples/**/inventory.json"))
        self.assertGreaterEqual(len(paths), 2)
        for path in paths:
            with self.subTest(path=path):
                validate_inventory(json.loads(path.read_text(encoding="utf-8")))

    def test_agent_skill_cannot_invoke_a_connector(self):
        inventory = json.loads(
            (ROOT / "examples/ai-governance/inventory.json").read_text(encoding="utf-8")
        )
        invalid = deepcopy(inventory)
        invalid["relations"].append(
            {
                "id": "invalid-skill-call",
                "source": "skill-cv-screening",
                "type": "can_invoke",
                "target": "connector-candidate-mail",
            }
        )
        with self.assertRaises(ValidationError):
            validate_inventory(invalid)

    def test_public_packs_do_not_ship_company_traffic_lights(self):
        traffic_light = re.compile(r"\b(?:green|orange|red|vert|rouge)\b", re.IGNORECASE)
        for path in ROOT.glob("packs/*/*/pack.json"):
            if "contract-review-example" in str(path):
                continue
            body = path.read_text(encoding="utf-8")
            with self.subTest(path=path):
                self.assertIsNone(traffic_light.search(body))

    def test_pack_rejects_ambiguous_condition_node(self):
        pack = json.loads(
            (ROOT / "packs/eu-ai-act/1.0.0/pack.json").read_text(encoding="utf-8")
        )
        invalid = deepcopy(pack)
        invalid["rules"][0]["when"] = {
            "literal": True,
            "fact": {"key": "example", "operator": "eq", "value": True},
        }
        with self.assertRaises(ValidationError):
            validate_pack(invalid)

    def test_pack_rejects_unknown_nested_operator(self):
        pack = json.loads(
            (ROOT / "packs/eu-ai-act/1.0.0/pack.json").read_text(encoding="utf-8")
        )
        invalid = deepcopy(pack)
        invalid["rules"][0]["when"] = {
            "related": {
                "path": [{"relation": "uses", "direction": "sideways"}],
                "where": {"fact": {"key": "example", "operator": "eq", "value": True}},
            }
        }
        with self.assertRaises(ValidationError):
            validate_pack(invalid)

    def test_pack_rejects_undeclared_fact(self):
        pack = json.loads(
            (ROOT / "packs/eu-ai-act/1.0.0/pack.json").read_text(encoding="utf-8")
        )
        invalid = deepcopy(pack)
        invalid["rules"][0]["when"] = {
            "fact": {"key": "undeclared.fact", "operator": "eq", "value": True}
        }
        with self.assertRaises(ValidationError):
            validate_pack(invalid)

    def test_binding_packs_have_official_anchors(self):
        for relative in [
            "packs/eu-ai-act/1.0.0/pack.json",
            "packs/eu-gdpr-ai/1.0.0/pack.json",
            "packs/eu-nis2-baseline/1.0.0/pack.json",
        ]:
            pack = json.loads((ROOT / relative).read_text(encoding="utf-8"))
            self.assertEqual("binding_law", pack["pack"]["authority_type"])
            self.assertTrue(pack["anchors"])
            self.assertTrue(
                all(anchor["url"].startswith("https://eur-lex.europa.eu/") for anchor in pack["anchors"])
            )


if __name__ == "__main__":
    unittest.main()
