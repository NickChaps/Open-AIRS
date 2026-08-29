# SPDX-License-Identifier: Apache-2.0
"""The qualification chain: facts → derived legal facts → obligations."""

from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from open_airs.engine import assess
from open_airs.errors import EvaluationError, ValidationError
from open_airs.judge import JsonCompletion, apply_extraction, extract_with_llm
from open_airs.validation import validate_inventory, validate_pack

ROOT = Path(__file__).resolve().parents[1]


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def _chain_pack():
    return {
        "schema_version": "0.1.0",
        "pack": {
            "id": "chain-test",
            "name": "Chain test pack",
            "version": "1.0.0",
            "authority_type": "fictional_example",
            "jurisdiction": "test",
            "reviewed_at": "2026-08-29",
            "coverage": ["emission chain"],
            "known_gaps": [],
            "applies_to": ["ai_use"],
        },
        "anchors": [
            {
                "id": "a1",
                "source": "test",
                "locator": "section 1",
                "url": "https://example.invalid/a1",
                "summary": "Test anchor.",
            }
        ],
        "fact_catalog": [
            {"id": "input.flag", "type": "boolean", "question": "Input?"},
            {
                "id": "derived.step",
                "type": "boolean",
                "question": "Derived step.",
                "derived": True,
            },
            {"id": "control.done", "type": "boolean", "question": "Control done?"},
        ],
        "rules": [
            {
                "id": "chain.qualify",
                "title": "Qualification",
                "kind": "legal_qualification",
                "applies_to": ["ai_use"],
                "when": {"fact": {"key": "input.flag", "operator": "eq", "value": True}},
                "finding": {
                    "code": "T-QUALIFY",
                    "level": "test",
                    "title": "Qualified",
                    "summary": "The input establishes the qualification.",
                },
                "anchors": ["a1"],
                "emits": [{"fact": "derived.step", "value": True}],
            },
            {
                "id": "chain.obligation-gap",
                "title": "Obligation gap",
                "kind": "obligation_gap",
                "applies_to": ["ai_use"],
                "when": {
                    "all": [
                        {"fact": {"key": "derived.step", "operator": "eq", "value": True}},
                        {"fact": {"key": "control.done", "operator": "eq", "value": False}},
                    ]
                },
                "finding": {
                    "code": "T-GAP",
                    "level": "test",
                    "title": "Missing control",
                    "summary": "The derived qualification requires the control.",
                },
                "anchors": ["a1"],
            },
        ],
    }


def _chain_inventory():
    return {
        "schema_version": "0.1.0",
        "inventory_id": "inv-chain",
        "snapshot_id": "snap-1",
        "captured_at": "2026-08-29T12:00:00Z",
        "objects": [
            {
                "id": "use-1",
                "type": "ai_use",
                "name": "Use",
                "facts": {
                    "input.flag": {
                        "state": "known",
                        "value": True,
                        "evidence": ["ev-1"],
                    },
                    "control.done": {
                        "state": "known",
                        "value": False,
                        "evidence": ["ev-1"],
                    },
                },
            }
        ],
        "relations": [],
        "evidence": [
            {"id": "ev-1", "kind": "configuration", "source": "test", "summary": "cfg"}
        ],
    }


class EmissionTests(unittest.TestCase):
    def test_emitted_fact_feeds_a_downstream_rule(self):
        result = assess(_chain_inventory(), _chain_pack(), "use-1")
        statuses = {item["rule_id"]: item["status"] for item in result["findings"]}
        self.assertEqual("matched", statuses["chain.qualify"])
        self.assertEqual("matched", statuses["chain.obligation-gap"])
        emitted = result["effective_facts"]["derived.step"]
        self.assertEqual(True, emitted["value"])
        self.assertEqual("rule", emitted["provenance"])
        self.assertEqual("chain.qualify", emitted["rule_id"])
        self.assertEqual(["ev-1"], emitted["evidence"])

    def test_without_the_input_the_chain_stays_indeterminate(self):
        inventory = _chain_inventory()
        del inventory["objects"][0]["facts"]["input.flag"]
        result = assess(inventory, _chain_pack(), "use-1")
        statuses = {item["rule_id"]: item["status"] for item in result["findings"]}
        self.assertEqual("indeterminate", statuses["chain.qualify"])
        self.assertEqual("indeterminate", statuses["chain.obligation-gap"])

    def test_emission_never_overrides_a_direct_fact(self):
        inventory = _chain_inventory()
        inventory["objects"][0]["facts"]["derived.step"] = {
            "state": "known",
            "value": False,
            "evidence": ["ev-1"],
        }
        result = assess(inventory, _chain_pack(), "use-1", include_not_matched=True)
        statuses = {item["rule_id"]: item["status"] for item in result["findings"]}
        self.assertEqual("matched", statuses["chain.qualify"])
        self.assertEqual("not_matched", statuses["chain.obligation-gap"])
        self.assertEqual(False, result["effective_facts"]["derived.step"]["value"])

    def test_not_matched_emission_uses_the_when_selector(self):
        pack = _chain_pack()
        pack["rules"][0]["emits"] = [
            {"fact": "derived.step", "value": True},
            {"fact": "derived.step", "value": False, "when": "not_matched"},
        ]
        inventory = _chain_inventory()
        inventory["objects"][0]["facts"]["input.flag"]["value"] = False
        result = assess(inventory, pack, "use-1", include_not_matched=True)
        self.assertEqual(False, result["effective_facts"]["derived.step"]["value"])

    def test_pack_validation_rejects_a_consumer_before_its_emitter(self):
        pack = _chain_pack()
        pack["rules"].reverse()
        with self.assertRaises(ValidationError):
            validate_pack(pack)

    def test_pack_validation_requires_emitted_facts_to_be_derived(self):
        pack = _chain_pack()
        for item in pack["fact_catalog"]:
            item.pop("derived", None)
        with self.assertRaises(ValidationError):
            validate_pack(pack)

    def test_pack_validation_checks_emitted_value_types(self):
        pack = _chain_pack()
        pack["rules"][0]["emits"][0]["value"] = "yes"
        with self.assertRaises(ValidationError):
            validate_pack(pack)


class WritePolicyTests(unittest.TestCase):
    def _engine_only_pack(self):
        pack = _chain_pack()
        catalog = {item["id"]: item for item in pack["fact_catalog"]}
        catalog["derived.step"]["engine_only"] = True
        return pack

    def test_engine_refuses_a_supplied_engine_only_conclusion(self):
        inventory = _chain_inventory()
        inventory["objects"][0]["facts"]["derived.step"] = {
            "state": "known",
            "value": False,
            "evidence": ["ev-1"],
        }
        with self.assertRaises(EvaluationError) as caught:
            assess(inventory, self._engine_only_pack(), "use-1")
        self.assertIn("derived.step", str(caught.exception))
        self.assertIn("attestation", str(caught.exception))

    def test_engine_only_without_supplied_conclusion_still_derives(self):
        result = assess(_chain_inventory(), self._engine_only_pack(), "use-1")
        statuses = {item["rule_id"]: item["status"] for item in result["findings"]}
        self.assertEqual("matched", statuses["chain.obligation-gap"])

    def test_pack_validation_requires_engine_only_to_be_derived(self):
        pack = _chain_pack()
        catalog = {item["id"]: item for item in pack["fact_catalog"]}
        catalog["input.flag"]["engine_only"] = True
        with self.assertRaises(ValidationError):
            validate_pack(pack)

    def test_shipped_packs_refuse_injected_conclusions(self):
        for pack_path, fact_id in [
            ("packs/eu-ai-act/1.3.1/pack.json", "aiact.high_risk_established"),
            ("packs/eu-gdpr-ai/1.3.1/pack.json", "gdpr.article22_established"),
        ]:
            with self.subTest(fact=fact_id):
                inventory = deepcopy(load("examples/ai-governance/inventory.json"))
                use = next(
                    item
                    for item in inventory["objects"]
                    if item["id"] == "use-recruiting-assistant"
                )
                use["facts"][fact_id] = {
                    "state": "known",
                    "value": False,
                    "evidence": ["ev-legal-review"],
                }
                with self.assertRaises(EvaluationError):
                    assess(inventory, load(pack_path), "use-recruiting-assistant")


class ConnectorActionValidationTests(unittest.TestCase):
    def _inventory_with_action(self, action):
        inventory = deepcopy(load("examples/ai-governance/inventory.json"))
        connector = next(
            item
            for item in inventory["objects"]
            if item["id"] == "connector-candidate-mail"
        )
        connector["facts"]["connector.actions"]["value"] = [action]
        return inventory

    def test_malformed_bypassable_fails_the_import(self):
        inventory = self._inventory_with_action(
            {
                "id": "send",
                "kind": "send_external",
                "approval": "per_action",
                "enforced_by": "platform",
                "bypassable": "yes",
            }
        )
        with self.assertRaises(ValidationError):
            validate_inventory(inventory)

    def test_unknown_enum_values_fail_the_import(self):
        for field, value in [
            ("kind", "email"),
            ("approval", "sometimes"),
            ("enforced_by", "policy"),
            ("target_criticality", "extreme"),
        ]:
            action = {
                "id": "send",
                "kind": "send_external",
                "approval": "per_action",
                "enforced_by": "platform",
                "bypassable": False,
            }
            action[field] = value
            with self.subTest(field=field):
                with self.assertRaises(ValidationError):
                    validate_inventory(self._inventory_with_action(action))

    def test_action_without_id_fails_the_import(self):
        inventory = self._inventory_with_action(
            {"kind": "read", "approval": "none"}
        )
        with self.assertRaises(ValidationError):
            validate_inventory(inventory)


class WorkedExampleChainTests(unittest.TestCase):
    """The shipped recruiting example carries no pre-filled legal conclusion."""

    def test_the_example_no_longer_declares_conclusions(self):
        inventory = load("examples/ai-governance/inventory.json")
        use = next(
            item
            for item in inventory["objects"]
            if item["id"] == "use-recruiting-assistant"
        )
        for concluded in [
            "aiact.high_risk_confirmed",
            "aiact.high_risk_route",
            "decision.solely_automated",
        ]:
            self.assertNotIn(concluded, use["facts"])

    def test_high_risk_obligations_fire_without_a_declared_conclusion(self):
        result = assess(
            load("examples/ai-governance/inventory.json"),
            load("packs/eu-ai-act/1.3.1/pack.json"),
            "use-recruiting-assistant",
        )
        statuses = {item["rule_id"]: item["status"] for item in result["findings"]}
        self.assertEqual("matched", statuses["aiact.core.high-risk-annex3"])
        self.assertEqual(
            "matched", statuses["aiact.core.controls-deployer-human-oversight-assigned-gap"]
        )
        emitted = result["effective_facts"]["aiact.high_risk_established"]
        self.assertEqual(True, emitted["value"])
        self.assertEqual("aiact.core.high-risk-annex3", emitted["rule_id"])
        self.assertEqual(
            "annex_iii", result["effective_facts"]["aiact.high_risk_route"]["value"]
        )
        self.assertEqual(0, result["summary"]["indeterminate"])

    def test_purpose_tags_alone_establish_the_employment_route(self):
        inventory = deepcopy(load("examples/ai-governance/inventory.json"))
        use = next(
            item
            for item in inventory["objects"]
            if item["id"] == "use-recruiting-assistant"
        )
        del use["facts"]["aiact.annex_iii_use_cases"]
        result = assess(
            inventory,
            load("packs/eu-ai-act/1.3.1/pack.json"),
            "use-recruiting-assistant",
        )
        statuses = {item["rule_id"]: item["status"] for item in result["findings"]}
        self.assertEqual(
            "matched", statuses["aiact.core.annex3-4a-recruitment-selection"]
        )
        self.assertEqual("matched", statuses["aiact.core.high-risk-annex3"])

    def test_article22_is_established_by_design(self):
        result = assess(
            load("examples/ai-governance/inventory.json"),
            load("packs/eu-gdpr-ai/1.3.1/pack.json"),
            "use-recruiting-assistant",
        )
        statuses = {item["rule_id"]: item["status"] for item in result["findings"]}
        self.assertEqual("matched", statuses["gdpr.ai.article22-restriction"])
        self.assertEqual("matched", statuses["gdpr.ai.article22-condition-gap"])
        facts = result["effective_facts"]
        self.assertEqual(
            True, facts["composition.autonomous_external_send_possible"]["value"]
        )
        self.assertEqual("derived", facts["composition.autonomous_external_send_possible"]["provenance"])
        self.assertEqual(True, facts["gdpr.article22_established"]["value"])

    def test_an_enforced_gate_leaves_the_question_open_not_established(self):
        """Gating the send removes the by-design path; the rule then stays
        indeterminate rather than not matched, because a solely automated
        practice is no longer established by the composition yet is not
        excluded either, absent an attestation or execution evidence."""

        inventory = deepcopy(load("examples/ai-governance/inventory.json"))
        connector = next(
            item
            for item in inventory["objects"]
            if item["id"] == "connector-candidate-mail"
        )
        for action in connector["facts"]["connector.actions"]["value"]:
            if action["kind"] == "send_external":
                action["approval"] = "per_action"
                action["enforced_by"] = "platform"
        result = assess(
            inventory,
            load("packs/eu-gdpr-ai/1.3.1/pack.json"),
            "use-recruiting-assistant",
            include_not_matched=True,
        )
        statuses = {item["rule_id"]: item["status"] for item in result["findings"]}
        self.assertEqual("indeterminate", statuses["gdpr.ai.article22-restriction"])
        facts = result["effective_facts"]
        self.assertEqual(
            False, facts["composition.autonomous_external_send_possible"]["value"]
        )
        self.assertNotIn("gdpr.article22_established", facts)


class _UseProposingJudge:
    provider_name = "test-provider"
    model = "test-model"

    def complete_json(self, *, system, user, schema_name, schema):
        del system, user, schema_name, schema
        return JsonCompletion(
            response_id="run-1",
            model=self.model,
            usage=None,
            value={
                "fact_proposals": [],
                "analysis": {
                    "summary": "One active use.",
                    "scope": "Test.",
                    "observations": [],
                    "unknowns": [],
                    "cautions": [],
                },
                "proposed_uses": [
                    {
                        "purpose_statement": "Do the thing.",
                        "purpose_tags": ["made_up"],
                        "material_tasks": [],
                        "affected_people": [],
                        "decision_influence": "informative",
                        "evidence": ["ev-1"],
                        "confidence": 0.9,
                        "alternative_interpretations": [],
                    }
                ],
            },
        )


class ExtractionGuardTests(unittest.TestCase):
    def test_model_proposed_uses_require_an_offered_taxonomy(self):
        with self.assertRaises(ValidationError) as caught:
            extract_with_llm(
                _chain_inventory(),
                [_chain_pack()],
                "use-1",
                _UseProposingJudge(),
            )
        self.assertIn("taxonomy", str(caught.exception))


class _MixedProfileJudge:
    """Minimal judge for the shipped five-pack profile: two of its packs do
    not apply to ai_use, and the apply step must revalidate against the same
    compatible packs the extraction was produced with."""

    provider_name = "test-provider"
    model = "test-model"

    def complete_json(self, *, system, user, schema_name, schema):
        del system, schema
        payload = json.loads(user.split("\n\n", 1)[1])
        if schema_name == "air_fact_extraction":
            return JsonCompletion(
                response_id="extract-mixed",
                model=self.model,
                usage=None,
                value={
                    "fact_proposals": [
                        {
                            "fact_id": "controls.dpia_completed",
                            "state": "known",
                            "value": False,
                            "evidence": ["ev-use-declaration"],
                            "confidence": 0.99,
                            "rationale": "The use owner declares no completed DPIA.",
                        }
                    ],
                    "analysis": {
                        "summary": "The captured facts already cover the catalogue.",
                        "scope": "Recruitment use, shipped example.",
                        "observations": [
                            {
                                "statement": "No completed DPIA is evidenced.",
                                "fact_ids": ["controls.dpia_completed"],
                                "evidence": ["ev-use-declaration"],
                            }
                        ],
                        "unknowns": [],
                        "cautions": [],
                    },
                },
            )
        assessment = payload["profile_assessment"]["assessments"][0]
        finding = next(
            item for item in assessment["findings"] if item["status"] == "matched"
        )
        return JsonCompletion(
            response_id="note-mixed",
            model=self.model,
            usage=None,
            value={
                "summary": "Derived qualification confirmed on the shipped example.",
                "scope": "Recruitment use, shipped example.",
                "statements": [
                    {
                        "statement_id": "note.finding.first",
                        "kind": "finding",
                        "text": finding["finding"]["summary"],
                        "references": {
                            "assessment_id": assessment["assessment_id"],
                            "rule_ids": [finding["rule_id"]],
                            "anchor_ids": [item["id"] for item in finding["anchors"]],
                        },
                    }
                ],
                "cautions": ["Fictional example."],
            },
        )


class MixedProfileTests(unittest.TestCase):
    def test_qualify_revalidates_against_the_compatible_packs_only(self):
        from open_airs.judge import qualify_with_llm
        from open_airs.profiles import load_profile_packs

        profile, packs = load_profile_packs(
            ROOT / "examples/ai-governance/pack-profile.json"
        )
        bundle = qualify_with_llm(
            load("examples/ai-governance/inventory.json"),
            profile,
            packs,
            "use-recruiting-assistant",
            _MixedProfileJudge(),
            assessed_at="2026-08-29T16:00:00Z",
        )
        result = bundle["profile_assessment"]
        skipped = {item["id"] for item in result.get("skipped_packs", [])}
        self.assertIn("eu-nis2-baseline", skipped)
        assessed = {item["pack"]["id"] for item in result["assessments"]}
        self.assertIn("eu-ai-act-core", assessed)
        self.assertIn("eu-gdpr-ai-core", assessed)


class PurposeApplicationTests(unittest.TestCase):
    def test_apply_extraction_reverifies_when_given_the_taxonomy(self):
        """An externally produced record with an invented tag must not slip
        into the inventory when the caller supplies the pinned taxonomy."""

        inventory = load("examples/ai-governance/inventory.json")
        extraction = deepcopy(load("examples/ai-governance/extraction.json"))
        extraction["proposed_uses"][0]["purpose_tags"] = ["made_up_tag"]
        taxonomy = load("taxonomies/purpose/1.0.0/taxonomy.json")
        with self.assertRaises(ValidationError):
            apply_extraction(
                inventory,
                extraction,
                taxonomy=taxonomy,
                trusted_prevalidated=True,
            )

    def test_apply_extraction_without_packs_fails_closed(self):
        inventory = load("examples/ai-governance/inventory.json")
        extraction = load("examples/ai-governance/extraction.json")
        with self.assertRaises(ValidationError) as caught:
            apply_extraction(inventory, extraction)
        self.assertIn("packs", str(caught.exception))

    def test_apply_extraction_synthesises_purpose_facts(self):
        inventory = deepcopy(load("examples/ai-governance/inventory.json"))
        use = next(
            item
            for item in inventory["objects"]
            if item["id"] == "use-recruiting-assistant"
        )
        for fact_id in list(use["facts"]):
            if fact_id.startswith("purpose."):
                del use["facts"][fact_id]
        extraction = deepcopy(load("examples/ai-governance/extraction.json"))
        extraction["inventory"].pop("content_hash", None)
        taxonomy = load("taxonomies/purpose/1.0.0/taxonomy.json")
        output = apply_extraction(
            inventory,
            extraction,
            captured_at="2026-08-29T13:00:00Z",
            taxonomy=taxonomy,
            trusted_prevalidated=True,
        )
        updated = next(
            item
            for item in output["objects"]
            if item["id"] == "use-recruiting-assistant"
        )
        self.assertEqual(
            ["candidate_selection", "recruitment"],
            updated["facts"]["purpose.tags"]["value"],
        )
        self.assertEqual(
            "determinative",
            updated["facts"]["purpose.decision_influence"]["value"],
        )
        self.assertEqual(
            ["job applicants"],
            updated["facts"]["purpose.affected_people"]["value"],
        )
        self.assertIn("extractor", updated["facts"]["purpose.tags"])


if __name__ == "__main__":
    unittest.main()
