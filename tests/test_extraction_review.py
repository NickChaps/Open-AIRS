# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from air_framework.engine import assess
from air_framework.errors import ValidationError
from air_framework.profiles import assess_profile, load_profile_packs
from air_framework.validation import (
    validate_assessment_note,
    validate_extraction_record,
    validate_review_record,
)

ROOT = Path(__file__).resolve().parents[1]


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class ExtractionAndReviewTests(unittest.TestCase):
    def test_example_extraction_and_review_records_validate(self):
        for folder in ["ai-governance", "contract-review"]:
            with self.subTest(folder=folder, record="extraction"):
                validate_extraction_record(load(f"examples/{folder}/extraction.json"))
            with self.subTest(folder=folder, record="review"):
                validate_review_record(load(f"examples/{folder}/review.json"))
            with self.subTest(folder=folder, record="assessment-note"):
                validate_assessment_note(
                    load(f"examples/{folder}/assessment-note.json")
                )

    def test_llm_extraction_requires_bounded_confidence(self):
        record = load("examples/ai-governance/extraction.json")
        invalid = deepcopy(record)
        invalid["fact_proposals"][0]["confidence"] = 1.5
        with self.assertRaises(ValidationError):
            validate_extraction_record(invalid)

    def test_analysis_observation_must_resolve_to_a_proposed_fact(self):
        record = load("examples/contract-review/extraction.json")
        invalid = deepcopy(record)
        invalid["analysis"]["observations"][0]["fact_ids"].append("missing.fact")
        with self.assertRaises(ValidationError):
            validate_extraction_record(invalid)

    def test_corrected_review_requires_versioned_corrective_action(self):
        record = load("examples/ai-governance/review.json")
        invalid = deepcopy(record)
        invalid["outcome"] = "corrected"
        invalid["adjudications"][0]["decision"] = "corrected"
        with self.assertRaises(ValidationError):
            validate_review_record(invalid)

    def test_confirmed_review_cannot_hide_an_unresolved_subject(self):
        record = load("examples/ai-governance/review.json")
        invalid = deepcopy(record)
        invalid["adjudications"][0]["decision"] = "unresolved"
        with self.assertRaises(ValidationError):
            validate_review_record(invalid)

    def test_no_change_cannot_be_combined_with_a_corrective_action(self):
        record = load("examples/ai-governance/review.json")
        invalid = deepcopy(record)
        invalid["actions"].append(
            {"type": "evidence_request", "summary": "Request another source."}
        )
        with self.assertRaises(ValidationError):
            validate_review_record(invalid)

    def test_finding_statement_requires_rule_and_anchor_references(self):
        record = load("examples/ai-governance/assessment-note.json")
        invalid = deepcopy(record)
        statement = next(
            item for item in invalid["statements"] if item["kind"] == "finding"
        )
        statement["references"]["anchor_ids"] = []
        with self.assertRaises(ValidationError):
            validate_assessment_note(invalid)

    def test_note_statement_cannot_reference_an_unlisted_assessment(self):
        record = load("examples/contract-review/assessment-note.json")
        invalid = deepcopy(record)
        statement = next(
            item for item in invalid["statements"] if item["kind"] == "finding"
        )
        statement["references"]["assessment_id"] = "urn:air:assessment:missing"
        with self.assertRaises(ValidationError):
            validate_assessment_note(invalid)

    def test_review_records_reference_current_example_assessments(self):
        cases = [
            (
                "ai-governance",
                "examples/ai-governance/inventory.json",
                "packs/eu-ai-act/1.3.1/pack.json",
                "use-recruiting-assistant",
            ),
            (
                "contract-review",
                "examples/contract-review/inventory.json",
                "packs/contract-review-example/1.0.0/pack.json",
                "contract-cloud-demo",
            ),
        ]
        for folder, inventory, pack, target in cases:
            with self.subTest(folder=folder):
                assessment = assess(load(inventory), load(pack), target)
                review = load(f"examples/{folder}/review.json")
                self.assertEqual(assessment["assessment_id"], review["assessment_id"])

    def test_note_finding_references_resolve_to_current_engine_outputs(self):
        inventory = load("examples/ai-governance/inventory.json")
        profile, packs = load_profile_packs(
            ROOT / "examples/ai-governance/pack-profile.json"
        )
        profile_result = assess_profile(
            inventory, profile, packs, "use-recruiting-assistant"
        )
        assessments = {
            item["assessment_id"]: item for item in profile_result["assessments"]
        }

        contract_assessment = assess(
            load("examples/contract-review/inventory.json"),
            load("packs/contract-review-example/1.0.0/pack.json"),
            "contract-cloud-demo",
        )
        assessments[contract_assessment["assessment_id"]] = contract_assessment

        for folder in ["ai-governance", "contract-review"]:
            note = load(f"examples/{folder}/assessment-note.json")
            review = load(f"examples/{folder}/review.json")
            self.assertEqual(note["review_status"]["review_id"], review["review_id"])
            for statement in note["statements"]:
                references = statement["references"]
                assessment_id = references.get("assessment_id")
                if assessment_id is None:
                    continue
                self.assertIn(assessment_id, assessments)
                findings = {
                    item["rule_id"]: item
                    for item in assessments[assessment_id]["findings"]
                }
                for rule_id in references.get("rule_ids", []):
                    self.assertIn(rule_id, findings)
                available_anchors = {
                    anchor["id"]
                    for rule_id in references.get("rule_ids", [])
                    for anchor in findings[rule_id]["anchors"]
                }
                self.assertTrue(
                    set(references.get("anchor_ids", [])).issubset(available_anchors)
                )


if __name__ == "__main__":
    unittest.main()
