# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path
from typing import Any

from open_airs.canonical import content_hash
from open_airs.errors import ValidationError
from open_airs.judge import (
    JsonCompletion,
    _context,
    apply_extraction,
    extract_with_llm,
    qualify_with_llm,
    validate_extraction_context,
    validate_note_context,
)
from open_airs.profiles import assess_profile, load_profile_packs

ROOT = Path(__file__).resolve().parents[1]


def load(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class FakeJudge:
    provider_name = "test-provider"
    model = "test-model"

    def __init__(self) -> None:
        self.calls: list[str] = []

    def complete_json(self, *, system, user, schema_name, schema):
        del system, schema
        self.calls.append(schema_name)
        if schema_name == "air_fact_extraction":
            return JsonCompletion(
                response_id="extract-1",
                model=self.model,
                usage={"prompt_tokens": 100, "completion_tokens": 40},
                value={
                    "fact_proposals": [
                        {
                            "fact_id": "clause.audit_cooperation_present",
                            "state": "known",
                            "value": False,
                            "evidence": ["ev-contract"],
                            "confidence": 0.94,
                            "rationale": "The supplied text does not establish an audit right.",
                        }
                    ],
                    "analysis": {
                        "summary": "The agreement contains no established audit right.",
                        "scope": "The fictional cloud services agreement.",
                        "observations": [
                            {
                                "statement": "No audit right is established.",
                                "fact_ids": ["clause.audit_cooperation_present"],
                                "evidence": ["ev-contract"],
                            }
                        ],
                        "unknowns": [],
                        "cautions": ["The test uses a synthetic agreement."],
                    },
                },
            )
        payload = json.loads(user.split("\n\n", 1)[1])
        extraction = payload["extraction"]
        assessment = payload["profile_assessment"]["assessments"][0]
        finding = next(item for item in assessment["findings"] if item["status"] == "matched")
        return JsonCompletion(
            response_id="note-1",
            model=self.model,
            usage={"prompt_tokens": 80, "completion_tokens": 30},
            value={
                "summary": "The contract review found a clause gap.",
                "scope": extraction["analysis"]["scope"],
                "statements": [
                    {
                        "statement_id": "note.fact.audit",
                        "kind": "fact",
                        "text": "The supplied agreement does not establish an audit right.",
                        "references": {
                            "fact_ids": ["clause.audit_cooperation_present"],
                            "evidence": ["ev-contract"],
                        },
                    },
                    {
                        "statement_id": "note.finding.audit",
                        "kind": "finding",
                        "text": finding["finding"]["summary"],
                        "references": {
                            "assessment_id": assessment["assessment_id"],
                            "rule_ids": [finding["rule_id"]],
                            "anchor_ids": [item["id"] for item in finding["anchors"]],
                        },
                    },
                ],
                "cautions": ["This is a fictional example."],
            },
        )


class JudgePipelineTests(unittest.TestCase):
    def setUp(self):
        self.inventory = load("examples/contract-review/inventory.json")
        self.pack = load("packs/contract-review-example/1.0.0/pack.json")
        self.profile = {
            "schema_version": "0.1.0",
            "profile": {
                "id": "test-contract-profile",
                "version": "1.0.0",
                "name": "Test contract profile",
            },
            "packs": [
                {
                    "id": self.pack["pack"]["id"],
                    "version": self.pack["pack"]["version"],
                    "path": "unused-in-direct-api.json",
                    "content_hash": content_hash(self.pack),
                }
            ],
        }

    def test_end_to_end_pipeline_calls_model_before_and_after_engine(self):
        client = FakeJudge()
        bundle = qualify_with_llm(
            self.inventory,
            self.profile,
            [self.pack],
            "contract-cloud-demo",
            client,
            assessed_at="2026-08-29T16:00:00Z",
        )
        self.assertEqual(client.calls, ["air_fact_extraction", "air_assessment_note"])
        fact = bundle["resolved_inventory"]["objects"][0]["facts"][
            "clause.audit_cooperation_present"
        ]
        self.assertEqual(fact["state"], "known")
        self.assertFalse(fact["value"])
        self.assertEqual(fact["extractor"]["extraction_id"], bundle["extraction"]["extraction_id"])
        self.assertTrue(bundle["profile_assessment"]["assessments"])
        self.assertEqual(bundle["assessment_note"]["renderer"]["kind"], "llm")
        self.assertEqual(bundle["extraction"]["extractor"]["usage"]["prompt_tokens"], 100)
        self.assertEqual(bundle["assessment_note"]["renderer"]["usage"]["prompt_tokens"], 80)

    def test_object_level_source_is_sent_to_the_model_before_any_fact_exists(self):
        inventory = deepcopy(self.inventory)
        target = inventory["objects"][0]
        target["evidence"] = ["ev-contract"]
        target["facts"] = {}
        extraction = extract_with_llm(
            inventory, [self.pack], "contract-cloud-demo", FakeJudge()
        )
        self.assertIn("ev-contract", extraction["source_evidence"])

    def test_missing_linked_evidence_fails_before_a_model_call(self):
        inventory = deepcopy(self.inventory)
        inventory["objects"][0]["facts"] = {}
        inventory["objects"][0]["evidence"] = []
        client = FakeJudge()
        with self.assertRaises(ValidationError):
            extract_with_llm(
                inventory, [self.pack], "contract-cloud-demo", client
            )
        self.assertEqual(client.calls, [])

    def test_direct_api_rejects_a_pack_outside_the_pinned_profile(self):
        profile = deepcopy(self.profile)
        profile["packs"][0]["content_hash"] = "0" * 64
        client = FakeJudge()
        with self.assertRaises(ValidationError):
            qualify_with_llm(
                self.inventory,
                profile,
                [self.pack],
                "contract-cloud-demo",
                client,
            )
        self.assertEqual(client.calls, [])

    def test_model_cannot_propose_a_fact_outside_selected_packs(self):
        client = FakeJudge()
        extraction = extract_with_llm(
            self.inventory, [self.pack], "contract-cloud-demo", client
        )
        invalid = deepcopy(extraction)
        invalid["fact_proposals"][0]["fact_id"] = "invented.legal_conclusion"
        invalid["analysis"]["observations"][0]["fact_ids"] = [
            "invented.legal_conclusion"
        ]
        with self.assertRaises(ValidationError):
            validate_extraction_context(invalid, self.inventory, [self.pack])

    def test_direct_fact_conflict_stays_visible(self):
        extraction = extract_with_llm(
            self.inventory, [self.pack], "contract-cloud-demo", FakeJudge()
        )
        modified = deepcopy(extraction)
        modified["fact_proposals"][0]["fact_id"] = "clause.confidentiality_present"
        modified["analysis"]["observations"][0]["fact_ids"] = [
            "clause.confidentiality_present"
        ]
        resolved = apply_extraction(self.inventory, modified, packs=[self.pack])
        fact = resolved["objects"][0]["facts"]["clause.confidentiality_present"]
        self.assertEqual(fact["state"], "conflicted")
        self.assertEqual(len(fact["candidate_values"]), 2)

    def test_model_unknown_does_not_downgrade_an_existing_known_fact(self):
        extraction = extract_with_llm(
            self.inventory, [self.pack], "contract-cloud-demo", FakeJudge()
        )
        modified = deepcopy(extraction)
        proposal = modified["fact_proposals"][0]
        proposal["fact_id"] = "clause.confidentiality_present"
        proposal["state"] = "unknown"
        proposal.pop("value", None)
        proposal["evidence"] = []
        modified["analysis"]["observations"][0]["fact_ids"] = [
            "clause.confidentiality_present"
        ]
        resolved = apply_extraction(self.inventory, modified, packs=[self.pack])
        fact = resolved["objects"][0]["facts"]["clause.confidentiality_present"]
        self.assertEqual(fact["state"], "known")
        self.assertTrue(fact["value"])

    def test_known_proposal_must_match_the_pack_fact_type(self):
        extraction = extract_with_llm(
            self.inventory, [self.pack], "contract-cloud-demo", FakeJudge()
        )
        invalid = deepcopy(extraction)
        invalid["fact_proposals"][0]["value"] = "false"
        with self.assertRaises(ValidationError):
            validate_extraction_context(invalid, self.inventory, [self.pack])

    def test_directed_context_includes_shared_connector_without_platform_siblings(self):
        inventory = load("examples/connector-topologies/inventory.json")
        inventory["objects"].append(
            {
                "id": "use-casework",
                "type": "ai_use",
                "name": "Casework use",
                "facts": {},
            }
        )
        inventory["relations"].append(
            {
                "id": "rel-use-casework",
                "source": "use-casework",
                "type": "implemented_by",
                "target": "app-casework",
                "evidence": ["ev-atlas-inventory"],
            }
        )
        context = _context(inventory, "use-casework")
        object_ids = {item["id"] for item in context["objects"]}
        self.assertIn("connector-company-search", object_ids)
        self.assertIn("connector-case-export", object_ids)
        self.assertNotIn("app-research", object_ids)

    def test_readable_finding_requires_rule_and_anchor_references(self):
        client = FakeJudge()
        bundle = qualify_with_llm(
            self.inventory,
            self.profile,
            [self.pack],
            "contract-cloud-demo",
            client,
        )
        note = deepcopy(bundle["assessment_note"])
        finding = next(item for item in note["statements"] if item["kind"] == "finding")
        finding["references"]["anchor_ids"] = []
        with self.assertRaises(ValidationError):
            validate_note_context(
                note, bundle["extraction"], bundle["profile_assessment"]
            )

    def test_worked_notes_reference_current_assessments(self):
        contract_result = assess_profile(
            self.inventory,
            self.profile,
            [self.pack],
            "contract-cloud-demo",
            assessed_at="2026-08-29T12:00:00Z",
        )
        contract_extraction = load("examples/contract-review/extraction.json")
        contract_note = load("examples/contract-review/assessment-note.json")
        validate_note_context(contract_note, contract_extraction, contract_result)
        self.assertEqual(
            set(contract_note["inputs"]["assessment_ids"]),
            {item["assessment_id"] for item in contract_result["assessments"]},
        )

        ai_profile, ai_packs = load_profile_packs(
            ROOT / "examples/ai-governance/pack-profile.json"
        )
        ai_inventory = load("examples/ai-governance/inventory.json")
        ai_result = assess_profile(
            ai_inventory,
            ai_profile,
            ai_packs,
            "use-recruiting-assistant",
            assessed_at="2026-08-29T12:00:00Z",
        )
        ai_extraction = load("examples/ai-governance/extraction.json")
        ai_note = load("examples/ai-governance/assessment-note.json")
        validate_note_context(ai_note, ai_extraction, ai_result)
        self.assertEqual(
            set(ai_note["inputs"]["assessment_ids"]),
            {item["assessment_id"] for item in ai_result["assessments"]},
        )


if __name__ == "__main__":
    unittest.main()
