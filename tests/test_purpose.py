# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from air_framework.errors import ValidationError
from air_framework.validation import validate_extraction_record, validate_taxonomy

ROOT = Path(__file__).resolve().parents[1]

TAXONOMY = json.loads(
    (ROOT / "taxonomies/purpose/1.0.0/taxonomy.json").read_text(encoding="utf-8")
)


def _record():
    return {
        "schema_version": "0.1.0",
        "extraction_id": "urn:air:extraction:test",
        "created_at": "2026-08-29T12:00:00Z",
        "target": {"id": "use-1", "type": "ai_use", "name": "Contract review"},
        "inventory": {"inventory_id": "inv-1", "snapshot_id": "snap-1"},
        "pack_inputs": [
            {"id": "test-pack", "version": "1.0.0", "content_hash": "0" * 64}
        ],
        "extractor": {
            "kind": "llm",
            "skill": {"id": "air-assess", "version": "0.3.0"},
        },
        "source_evidence": ["ev-prompt"],
        "fact_proposals": [
            {
                "fact_id": "use.domain",
                "state": "known",
                "value": "procurement",
                "evidence": ["ev-prompt"],
                "confidence": 0.95,
                "rationale": "The prompt targets supplier contracts.",
            }
        ],
        "taxonomy": {"id": "air-purpose", "version": "1.0.0"},
        "proposed_uses": [
            {
                "purpose_statement": "Review supplier contracts for missing clauses.",
                "purpose_tags": ["contract_review"],
                "material_tasks": ["analyse_clauses", "flag_gaps"],
                "affected_people": [],
                "decision_influence": "informative",
                "evidence": ["ev-prompt"],
                "confidence": 0.97,
                "alternative_interpretations": [],
            }
        ],
        "excluded_mentions": [
            {
                "candidate_use": "Candidate selection",
                "classification": "prohibited_by_instructions",
                "evidence": ["ev-prompt"],
                "note": "The prompt forbids screening CVs.",
            }
        ],
        "analysis": {
            "summary": "One active procurement use; recruitment is forbidden.",
            "scope": "Prompt only.",
            "observations": [
                {
                    "statement": "The prompt requests clause analysis.",
                    "fact_ids": ["use.domain"],
                    "evidence": ["ev-prompt"],
                }
            ],
            "unknowns": [],
            "cautions": [],
        },
    }


class PurposeLayerTests(unittest.TestCase):
    def test_shipped_taxonomy_is_valid(self):
        validate_taxonomy(TAXONOMY)

    def test_guardrail_false_positive_is_representable(self):
        """The canonical case: a forbidden activity never becomes a use."""

        record = _record()
        validate_extraction_record(record, taxonomy=TAXONOMY)
        excluded = {item["candidate_use"] for item in record["excluded_mentions"]}
        proposed = {
            tag for use in record["proposed_uses"] for tag in use["purpose_tags"]
        }
        self.assertIn("Candidate selection", excluded)
        self.assertNotIn("candidate_selection", proposed)
        self.assertNotIn("recruitment", proposed)

    def test_unknown_tag_is_rejected_when_taxonomy_is_supplied(self):
        record = _record()
        record["proposed_uses"][0]["purpose_tags"] = ["made_up_tag"]
        with self.assertRaises(ValidationError):
            validate_extraction_record(record, taxonomy=TAXONOMY)

    def test_taxonomy_pin_is_required_with_proposed_uses(self):
        record = _record()
        del record["taxonomy"]
        with self.assertRaises(ValidationError):
            validate_extraction_record(record)

    def test_pin_must_match_supplied_taxonomy(self):
        record = _record()
        record["taxonomy"]["version"] = "9.9.9"
        with self.assertRaises(ValidationError):
            validate_extraction_record(record, taxonomy=TAXONOMY)

    def test_pin_content_hash_must_match_supplied_taxonomy(self):
        record = _record()
        record["taxonomy"]["content_hash"] = "0" * 64
        with self.assertRaises(ValidationError):
            validate_extraction_record(record, taxonomy=TAXONOMY)

    def test_excluded_mention_classification_is_bounded(self):
        record = _record()
        record["excluded_mentions"][0]["classification"] = "just_a_thought"
        with self.assertRaises(ValidationError):
            validate_extraction_record(record, taxonomy=TAXONOMY)

    def test_use_evidence_must_exist_in_source_evidence(self):
        record = _record()
        record["proposed_uses"][0]["evidence"] = ["ev-unknown"]
        with self.assertRaises(ValidationError):
            validate_extraction_record(record, taxonomy=TAXONOMY)

    def test_llm_uses_require_confidence(self):
        record = _record()
        del record["proposed_uses"][0]["confidence"]
        with self.assertRaises(ValidationError):
            validate_extraction_record(record, taxonomy=TAXONOMY)

    def test_record_without_purpose_blocks_remains_valid(self):
        record = _record()
        del record["taxonomy"]
        del record["proposed_uses"]
        del record["excluded_mentions"]
        validate_extraction_record(record)


if __name__ == "__main__":
    unittest.main()
