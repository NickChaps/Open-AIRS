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

    def test_every_declared_fact_is_used_by_a_rule_or_inheritance(self):
        def collect_fact_keys(node, result):
            if isinstance(node, dict):
                fact = node.get("fact")
                if isinstance(fact, dict) and isinstance(fact.get("key"), str):
                    result.add(fact["key"])
                for value in node.values():
                    collect_fact_keys(value, result)
            elif isinstance(node, list):
                for value in node:
                    collect_fact_keys(value, result)

        for path in sorted(ROOT.glob("packs/*/*/pack.json")):
            pack = json.loads(path.read_text(encoding="utf-8"))
            used = set()
            for rule in pack["rules"]:
                collect_fact_keys(rule["when"], used)
            used.update(item["fact"] for item in pack.get("inheritance", []))
            declared = {item["id"] for item in pack["fact_catalog"]}
            with self.subTest(path=path):
                self.assertEqual(set(), declared - used)

    def test_every_example_inventory_validates(self):
        paths = sorted(ROOT.glob("examples/**/inventory.json"))
        self.assertGreaterEqual(len(paths), 2)
        for path in paths:
            with self.subTest(path=path):
                validate_inventory(json.loads(path.read_text(encoding="utf-8")))

    def test_skill_cannot_invoke_a_connector(self):
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

    def test_pack_requires_a_human_readable_finding_summary(self):
        pack = json.loads(
            (ROOT / "packs/eu-ai-act/1.0.0/pack.json").read_text(encoding="utf-8")
        )
        del pack["rules"][0]["finding"]["summary"]
        with self.assertRaises(ValidationError):
            validate_pack(pack)

    def test_inventory_requires_capture_time(self):
        inventory = json.loads(
            (ROOT / "examples/ai-governance/inventory.json").read_text(encoding="utf-8")
        )
        del inventory["captured_at"]
        with self.assertRaises(ValidationError):
            validate_inventory(inventory)

    def test_known_fact_requires_evidence(self):
        inventory = json.loads(
            (ROOT / "examples/ai-governance/inventory.json").read_text(encoding="utf-8")
        )
        target = next(
            item for item in inventory["objects"] if item["id"] == "use-recruiting-assistant"
        )
        target["facts"]["ai.is_ai_system"]["evidence"] = []
        with self.assertRaises(ValidationError):
            validate_inventory(inventory)

    def test_relation_evidence_must_resolve(self):
        inventory = json.loads(
            (ROOT / "examples/ai-governance/inventory.json").read_text(encoding="utf-8")
        )
        inventory["relations"][0]["evidence"] = ["missing-evidence"]
        with self.assertRaises(ValidationError):
            validate_inventory(inventory)

    def test_binding_packs_have_official_anchors(self):
        for path in ROOT.glob("packs/*/*/pack.json"):
            pack = json.loads(path.read_text(encoding="utf-8"))
            if pack["pack"]["authority_type"] != "binding_law":
                continue
            with self.subTest(path=path):
                self.assertTrue(pack["anchors"])
                binding_anchors = [
                    anchor
                    for anchor in pack["anchors"]
                    if anchor["source"].startswith(("Regulation", "Directive", "Commission"))
                ]
                self.assertTrue(binding_anchors)
                self.assertTrue(
                    all(
                        anchor["url"].startswith("https://eur-lex.europa.eu/")
                        for anchor in binding_anchors
                    )
                )

    def test_ai_act_1_1_covers_current_core_routes(self):
        pack = json.loads(
            (ROOT / "packs/eu-ai-act/1.1.0/pack.json").read_text(encoding="utf-8")
        )
        article5 = [
            item
            for item in pack["rules"]
            if item["finding"]["level"]
            in {"prohibited_practice", "prohibited_from_2026_12_02"}
        ]
        annex3 = [
            item
            for item in pack["rules"]
            if item["finding"]["level"] == "annex_iii_candidate"
        ]
        self.assertEqual(10, len(article5))
        self.assertEqual(25, len(annex3))
        self.assertTrue(
            {
                "EU-AIACT-ART22-MANDATE",
                "EU-AIACT-ART23-CHECKS",
                "EU-AIACT-ART24-CHECKS",
                "EU-AIACT-ART25-4",
                "EU-AIACT-ART26-OVERSIGHT",
                "EU-AIACT-ART27",
                "EU-AIACT-ART50-1",
                "EU-AIACT-ART53-A",
                "EU-AIACT-ART55-D",
            }.issubset({item["finding"]["code"] for item in pack["rules"]})
        )

    def test_nis2_1_1_covers_all_measure_families_and_reporting_stages(self):
        pack = json.loads(
            (ROOT / "packs/eu-nis2-baseline/1.1.0/pack.json").read_text(
                encoding="utf-8"
            )
        )
        codes = {item["finding"]["code"] for item in pack["rules"]}
        self.assertTrue(
            {f"EU-NIS2-ART21-2-{letter}" for letter in "ABCDEFGHIJ"}.issubset(codes)
        )
        self.assertTrue(
            {
                "EU-NIS2-ART23-24H",
                "EU-NIS2-ART23-72H",
                "EU-NIS2-ART23-INTERMEDIATE",
                "EU-NIS2-ART23-FINAL",
                "EU-NIS2-ART23-ONGOING",
            }.issubset(codes)
        )

    def test_gdpr_1_1_covers_core_controller_and_processor_governance(self):
        pack = json.loads(
            (ROOT / "packs/eu-gdpr-ai/1.1.0/pack.json").read_text(encoding="utf-8")
        )
        codes = {item["finding"]["code"] for item in pack["rules"]}
        self.assertTrue(
            {
                "EU-GDPR-ART24",
                "EU-GDPR-ART25",
                "EU-GDPR-ART26",
                "EU-GDPR-ART27",
                "EU-GDPR-ART28",
                "EU-GDPR-ART30",
                "EU-GDPR-ARTICLE-22",
                "EU-GDPR-ARTICLE-35",
            }.issubset(codes)
        )

    def test_nist_packs_expose_every_current_core_outcome(self):
        ai_rmf = json.loads(
            (ROOT / "packs/nist-ai-rmf/1.1.0/pack.json").read_text(encoding="utf-8")
        )
        csf = json.loads(
            (ROOT / "packs/nist-csf/2.1.0/pack.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            72,
            sum(item["title"].endswith("target outcome gap") for item in ai_rmf["rules"]),
        )
        self.assertEqual(
            106,
            sum(item["title"].endswith("target outcome gap") for item in csf["rules"]),
        )


if __name__ == "__main__":
    unittest.main()


class InheritanceCoverageTests(unittest.TestCase):
    """The flagship packs must keep exercising explicit inheritance."""

    def test_latest_flagship_packs_declare_inheritance(self):
        import json
        from pathlib import Path

        root = Path(__file__).resolve().parents[1]
        for pack_dir in ("eu-ai-act", "eu-gdpr-ai"):
            versions = sorted(
                (item.name for item in (root / "packs" / pack_dir).iterdir() if item.is_dir()),
                key=lambda value: tuple(int(part) for part in value.split(".")),
            )
            latest = versions[-1]
            pack = json.loads(
                (root / "packs" / pack_dir / latest / "pack.json").read_text(
                    encoding="utf-8"
                )
            )
            with self.subTest(pack=pack_dir, version=latest):
                self.assertTrue(
                    pack.get("inheritance"),
                    f"{pack_dir} {latest} must declare at least one inheritance "
                    "policy or justify its removal in the changelog and this test",
                )
