# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from open_airs.engine import assess, diff_assessments, pack_impact
from open_airs.errors import EvaluationError

ROOT = Path(__file__).resolve().parents[1]


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class AssessmentTests(unittest.TestCase):
    def test_ai_act_employment_composition_is_high_risk(self):
        result = assess(
            load("examples/ai-governance/inventory.json"),
            load("packs/eu-ai-act/1.0.0/pack.json"),
            "use-recruiting-assistant",
            assessed_at="2026-08-29T12:00:00Z",
        )
        matched = {
            item["finding"]["code"]
            for item in result["findings"]
            if item["status"] == "matched"
        }
        self.assertIn("EU-AIACT-HIGH-RISK-ANNEX-III-4", matched)
        self.assertIn("EU-AIACT-ARTICLE-50-DISCLOSURE", matched)
        candidate = next(
            item
            for item in result["findings"]
            if item["rule_id"] == "aiact.core.annex3-employment-candidate"
        )
        self.assertIn("skill-cv-screening", candidate["trace"]["related_objects"])

    def test_non_ai_automation_cannot_match_ai_act_use_rules(self):
        inventory = deepcopy(load("examples/ai-governance/inventory.json"))
        use = next(item for item in inventory["objects"] if item["id"] == "use-recruiting-assistant")
        use["facts"]["ai.is_ai_system"] = {
            "state": "known",
            "value": False,
            "evidence": ["ev-legal-review"],
        }
        result = assess(
            inventory,
            load("packs/eu-ai-act/1.0.0/pack.json"),
            "use-recruiting-assistant",
            include_not_matched=True,
        )
        matched = [item for item in result["findings"] if item["status"] == "matched"]
        self.assertEqual([], matched)

    def test_passive_skill_can_contribute_to_use_purpose(self):
        inventory = deepcopy(load("examples/ai-governance/inventory.json"))
        use = next(item for item in inventory["objects"] if item["id"] == "use-recruiting-assistant")
        use["facts"]["use.tasks"] = {"state": "unknown", "evidence": []}
        use["facts"]["aiact.annex_iii_use_case"] = {"state": "unknown", "evidence": []}
        result = assess(
            inventory,
            load("packs/eu-ai-act/1.0.0/pack.json"),
            "use-recruiting-assistant",
        )
        high_risk = next(
            item
            for item in result["findings"]
            if item["rule_id"] == "aiact.core.annex3-employment-high-risk"
        )
        self.assertEqual("matched", high_risk["status"])
        self.assertIn("skill-cv-screening", high_risk["trace"]["related_objects"])

    def test_ai_act_rebranding_can_transfer_provider_role(self):
        inventory = deepcopy(load("examples/ai-governance/inventory.json"))
        use = next(item for item in inventory["objects"] if item["id"] == "use-recruiting-assistant")
        use["facts"]["change.name_or_trademark_on_existing_high_risk_system"] = {
            "state": "known",
            "value": True,
            "evidence": ["ev-legal-review"],
        }
        result = assess(
            inventory,
            load("packs/eu-ai-act/1.0.0/pack.json"),
            "use-recruiting-assistant",
        )
        provider_role = next(
            item
            for item in result["findings"]
            if item["rule_id"] == "aiact.core.value-chain-provider-role"
        )
        self.assertEqual("matched", provider_role["status"])

    def test_ai_act_law_enforcement_exception_prevents_interaction_finding(self):
        inventory = deepcopy(load("examples/ai-governance/inventory.json"))
        use = next(item for item in inventory["objects"] if item["id"] == "use-recruiting-assistant")
        use["facts"]["interaction.authorized_law_enforcement_exception"] = {
            "state": "known",
            "value": True,
            "evidence": ["ev-legal-review"],
        }
        result = assess(
            inventory,
            load("packs/eu-ai-act/1.0.0/pack.json"),
            "use-recruiting-assistant",
            include_not_matched=True,
        )
        disclosure = next(
            item
            for item in result["findings"]
            if item["rule_id"] == "aiact.core.direct-interaction-transparency"
        )
        self.assertEqual("not_matched", disclosure["status"])

    def test_platform_control_is_inherited_only_when_pack_declares_it(self):
        result = assess(
            load("examples/ai-governance/inventory.json"),
            load("packs/eu-ai-act/1.0.0/pack.json"),
            "use-recruiting-assistant",
        )
        fact = result["effective_facts"]["controls.ai_literacy_measures"]
        self.assertEqual("inherited", fact["provenance"])
        self.assertEqual(["platform-orbit"], fact["inherited_from"])

    def test_direct_conflict_is_not_overwritten_by_inheritance(self):
        inventory = deepcopy(load("examples/ai-governance/inventory.json"))
        use = next(
            item for item in inventory["objects"] if item["id"] == "use-recruiting-assistant"
        )
        use["facts"]["controls.ai_literacy_measures"] = {
            "state": "conflicted",
            "evidence": ["ev-use-declaration", "ev-platform-controls"],
        }
        result = assess(
            inventory,
            load("packs/eu-ai-act/1.0.0/pack.json"),
            "use-recruiting-assistant",
        )
        self.assertEqual(
            "conflicted",
            result["effective_facts"]["controls.ai_literacy_measures"]["state"],
        )

    def test_summary_counts_all_evaluated_rules_when_non_matches_are_hidden(self):
        result = assess(
            load("examples/ai-governance/inventory.json"),
            load("packs/eu-ai-act/1.0.0/pack.json"),
            "use-recruiting-assistant",
        )
        summary = result["summary"]
        self.assertEqual(
            summary["evaluated_rules"],
            summary["matched"] + summary["indeterminate"] + summary["not_matched"],
        )
        self.assertEqual(summary["returned_findings"], len(result["findings"]))
        self.assertGreater(summary["not_matched"], 0)
        self.assertGreater(summary["evaluated_rules"], summary["returned_findings"])

    def test_known_fact_value_must_match_pack_catalog_type(self):
        inventory = deepcopy(load("examples/ai-governance/inventory.json"))
        use = next(
            item for item in inventory["objects"] if item["id"] == "use-recruiting-assistant"
        )
        use["facts"]["ai.is_ai_system"] = {
            "state": "known",
            "value": "yes",
            "evidence": ["ev-legal-review"],
        }
        with self.assertRaises(EvaluationError):
            assess(
                inventory,
                load("packs/eu-ai-act/1.0.0/pack.json"),
                "use-recruiting-assistant",
            )

    def test_same_content_has_same_id_despite_run_time(self):
        inventory = load("examples/contract-review/inventory.json")
        pack = load("packs/contract-review-example/1.0.0/pack.json")
        first = assess(
            inventory, pack, "contract-cloud-demo", assessed_at="2026-08-29T12:00:00Z"
        )
        second = assess(
            inventory, pack, "contract-cloud-demo", assessed_at="2026-09-01T12:00:00Z"
        )
        self.assertEqual(first["assessment_id"], second["assessment_id"])
        self.assertEqual(first["result_hash"], second["result_hash"])
        self.assertNotEqual(first["assessed_at"], second["assessed_at"])

    def test_contract_ambiguous_clause_is_indeterminate(self):
        result = assess(
            load("examples/contract-review/inventory.json"),
            load("packs/contract-review-example/1.0.0/pack.json"),
            "contract-cloud-demo",
        )
        by_rule = {item["rule_id"]: item for item in result["findings"]}
        self.assertEqual("matched", by_rule["contract.demo.ip-missing"]["status"])
        self.assertEqual("matched", by_rule["contract.demo.security-notice-missing"]["status"])
        self.assertEqual("indeterminate", by_rule["contract.demo.audit-missing"]["status"])

    def test_decisive_any_trace_does_not_report_irrelevant_missing_facts(self):
        result = assess(
            load("examples/ai-governance/inventory.json"),
            load("packs/eu-gdpr-ai/1.0.0/pack.json"),
            "use-recruiting-assistant",
        )
        dpia = next(item for item in result["findings"] if item["rule_id"] == "gdpr.ai.dpia-trigger")
        self.assertEqual([], dpia["trace"]["missing_facts"])

    def test_gdpr_dpia_trigger_and_completion_gap_are_separate(self):
        result = assess(
            load("examples/ai-governance/inventory.json"),
            load("packs/eu-gdpr-ai/1.0.0/pack.json"),
            "use-recruiting-assistant",
        )
        by_rule = {item["rule_id"]: item for item in result["findings"]}
        self.assertEqual("matched", by_rule["gdpr.ai.dpia-trigger"]["status"])
        self.assertEqual("matched", by_rule["gdpr.ai.dpia-completion-gap"]["status"])

    def test_gdpr_article22_special_category_restriction_is_encoded(self):
        inventory = deepcopy(load("examples/ai-governance/inventory.json"))
        use = next(item for item in inventory["objects"] if item["id"] == "use-recruiting-assistant")
        use["facts"]["decision.solely_automated"] = {
            "state": "known",
            "value": True,
            "evidence": ["ev-legal-review"],
        }
        use["facts"]["data.special_categories_processed"] = {
            "state": "known",
            "value": True,
            "evidence": ["ev-use-declaration"],
        }
        use["facts"]["decision.based_on_special_categories"] = {
            "state": "known",
            "value": True,
            "evidence": ["ev-use-declaration"],
        }
        use["facts"]["decision.article22_4_special_category_condition_established"] = {
            "state": "known",
            "value": False,
            "evidence": ["ev-legal-review"],
        }
        result = assess(
            inventory,
            load("packs/eu-gdpr-ai/1.0.0/pack.json"),
            "use-recruiting-assistant",
        )
        special_category = next(
            item
            for item in result["findings"]
            if item["rule_id"] == "gdpr.ai.article22-special-category-gap"
        )
        self.assertEqual("matched", special_category["status"])

    def test_incompatible_object_type_fails_closed(self):
        with self.assertRaises(EvaluationError):
            assess(
                load("examples/contract-review/inventory.json"),
                load("packs/eu-ai-act/1.0.0/pack.json"),
                "contract-cloud-demo",
            )

    def test_diff_detects_status_change(self):
        before = {
            "assessment_id": "before",
            "findings": [{"rule_id": "r1", "status": "indeterminate", "finding": {}}],
        }
        after = {
            "assessment_id": "after",
            "findings": [{"rule_id": "r1", "status": "matched", "finding": {}}],
        }
        result = diff_assessments(before, after)
        self.assertTrue(result["has_drift"])
        self.assertEqual("r1", result["changed"][0]["rule_id"])

    def test_identical_pack_has_no_impact(self):
        inventory = load("examples/ai-governance/inventory.json")
        pack = load("packs/eu-ai-act/1.0.0/pack.json")
        result = pack_impact(inventory, pack, pack, assessed_at="2026-08-29T12:00:00Z")
        self.assertFalse(result["has_impact"])

    def test_candidate_pack_reports_finding_drift(self):
        inventory = load("examples/ai-governance/inventory.json")
        active = load("packs/eu-ai-act/1.0.0/pack.json")
        candidate = deepcopy(active)
        candidate["pack"]["version"] = "1.0.1"
        changed_rule = next(
            rule
            for rule in candidate["rules"]
            if rule["id"] == "aiact.core.annex3-employment-high-risk"
        )
        changed_rule["finding"]["title"] = "Changed candidate wording"
        result = pack_impact(
            inventory,
            active,
            candidate,
            assessed_at="2026-08-29T12:00:00Z",
        )
        self.assertTrue(result["has_impact"])
        self.assertTrue(any(item["change"] == "findings_changed" for item in result["changes"]))


if __name__ == "__main__":
    unittest.main()
