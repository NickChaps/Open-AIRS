# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path

from open_airs.engine import assess
from open_airs.errors import ValidationError
from open_airs.routing import apply_routes
from open_airs.validation import validate_route_profile

ROOT = Path(__file__).resolve().parents[1]


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class RoutingTests(unittest.TestCase):
    def test_profile_validates_and_routes_without_mutating_finding(self):
        profile = load("examples/organization-routing.json")
        validate_route_profile(profile)
        inventory = load("examples/ai-governance/inventory.json")
        use = next(
            item for item in inventory["objects"] if item["id"] == "use-recruiting-assistant"
        )
        use["facts"]["interaction.authorized_law_enforcement_exception"] = {
            "state": "unknown"
        }
        assessment = assess(
            inventory,
            load("packs/eu-ai-act/1.0.0/pack.json"),
            "use-recruiting-assistant",
            assessed_at="2026-08-29T12:00:00Z",
        )
        before_hash = assessment["result_hash"]
        routed = apply_routes([assessment], profile)
        route_ids = [item["route"]["id"] for item in routed["assignments"]]
        self.assertIn("formal_conformity_path", route_ids)
        self.assertIn("complete_evidence", route_ids)
        self.assertEqual(before_hash, assessment["result_hash"])

    def test_unknown_route_selector_fails_closed(self):
        profile = deepcopy(load("examples/organization-routing.json"))
        profile["mappings"][0]["match"] = {"mystery_selector": ["x"]}
        with self.assertRaises(ValidationError):
            validate_route_profile(profile)

    def test_boolean_route_priority_is_rejected(self):
        profile = deepcopy(load("examples/organization-routing.json"))
        profile["routes"][0]["priority"] = True
        with self.assertRaises(ValidationError):
            validate_route_profile(profile)


if __name__ == "__main__":
    unittest.main()
