# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import unittest
from copy import deepcopy

from air_framework.composition import derive_composition_facts, reachable_connectors
from air_framework.graph import InventoryGraph


def _fact(value, evidence=("ev-config",)):
    return {"state": "known", "value": value, "evidence": list(evidence)}


def _inventory():
    return {
        "schema_version": "0.1.0",
        "inventory_id": "inv-test",
        "snapshot_id": "snap-1",
        "captured_at": "2026-08-29T12:00:00Z",
        "objects": [
            {"id": "use-1", "type": "ai_use", "name": "Use", "facts": {}},
            {"id": "app-1", "type": "configured_ai_application", "name": "App", "facts": {}},
            {"id": "platform-1", "type": "ai_platform", "name": "Platform", "facts": {}},
            {
                "id": "conn-mail",
                "type": "connector",
                "name": "Mail connector",
                "facts": {
                    "connector.actions": _fact(
                        [
                            {"id": "search", "kind": "read", "approval": "none"},
                            {
                                "id": "send_email",
                                "kind": "send_external",
                                "approval": "per_action",
                                "enforced_by": "connector",
                                "bypassable": False,
                            },
                        ],
                        evidence=("ev-mail",),
                    )
                },
            },
            {
                "id": "conn-files",
                "type": "connector",
                "name": "File connector",
                "facts": {
                    "connector.actions": _fact(
                        [
                            {"id": "read_file", "kind": "read", "approval": "none"},
                            {
                                "id": "write_file",
                                "kind": "write",
                                "approval": "per_conversation",
                                "enforced_by": "platform",
                                "bypassable": False,
                            },
                        ],
                        evidence=("ev-files",),
                    )
                },
            },
        ],
        "relations": [
            {"id": "r1", "source": "use-1", "type": "implemented_by", "target": "app-1"},
            {"id": "r2", "source": "app-1", "type": "runs_on", "target": "platform-1"},
            {"id": "r3", "source": "app-1", "type": "can_invoke", "target": "conn-files"},
            {"id": "r4", "source": "platform-1", "type": "can_invoke", "target": "conn-mail"},
        ],
        "evidence": [
            {"id": "ev-mail", "kind": "configuration", "source": "test", "summary": "mail"},
            {"id": "ev-files", "kind": "configuration", "source": "test", "summary": "files"},
            {"id": "ev-config", "kind": "configuration", "source": "test", "summary": "config"},
        ],
    }


class CompositionDerivationTests(unittest.TestCase):
    def test_reachable_connectors_follow_use_and_platform_paths(self):
        graph = InventoryGraph(_inventory())
        self.assertEqual(
            reachable_connectors(graph, "use-1"), ["conn-files", "conn-mail"]
        )

    def test_gated_external_send_is_found_but_not_autonomous(self):
        graph = InventoryGraph(_inventory())
        facts = derive_composition_facts(graph, "use-1")
        can_send = facts["composition.can_send_external"]
        self.assertEqual(can_send["state"], "known")
        self.assertTrue(can_send["value"])
        self.assertEqual(can_send["provenance"], "derived")
        self.assertIn("ev-mail", can_send["evidence"])
        autonomous = facts["composition.autonomous_external_send_possible"]
        self.assertEqual(autonomous["state"], "known")
        self.assertFalse(autonomous["value"])
        floor = facts["composition.engaging_action_approval_floor"]
        self.assertEqual(floor["value"], "per_conversation")

    def test_negative_conclusions_require_complete_declarations(self):
        inventory = _inventory()
        inventory["objects"][4]["facts"] = {}
        graph = InventoryGraph(inventory)
        facts = derive_composition_facts(graph, "use-1")
        self.assertEqual(facts["composition.can_send_external"]["value"], True)
        self.assertEqual(
            facts["composition.autonomous_external_send_possible"]["state"], "unknown"
        )
        inventory = _inventory()
        inventory["objects"][3]["facts"] = {}
        graph = InventoryGraph(inventory)
        facts = derive_composition_facts(graph, "use-1")
        self.assertEqual(facts["composition.can_send_external"]["state"], "unknown")
        self.assertEqual(
            facts["composition.autonomous_external_send_possible"]["state"], "unknown"
        )

    def test_unenforced_approval_is_not_a_demonstrable_gate(self):
        """A per-action approval that nothing technically imposes is a policy
        wish, so the action still counts as autonomous."""

        for enforced_by in ["none", "policy", None]:
            inventory = _inventory()
            actions = inventory["objects"][3]["facts"]["connector.actions"]["value"]
            if enforced_by is None:
                actions[1].pop("enforced_by", None)
            else:
                actions[1]["enforced_by"] = enforced_by
            graph = InventoryGraph(inventory)
            facts = derive_composition_facts(graph, "use-1")
            with self.subTest(enforced_by=enforced_by):
                self.assertTrue(
                    facts["composition.autonomous_external_send_possible"]["value"]
                )
                self.assertEqual(
                    facts["composition.engaging_action_approval_floor"]["value"],
                    "none",
                )

    def test_bypassable_or_unlisted_approval_counts_as_autonomous(self):
        inventory = _inventory()
        actions = inventory["objects"][3]["facts"]["connector.actions"]["value"]
        actions[1]["bypassable"] = True
        graph = InventoryGraph(inventory)
        facts = derive_composition_facts(graph, "use-1")
        self.assertTrue(facts["composition.autonomous_external_send_possible"]["value"])
        self.assertEqual(
            facts["composition.engaging_action_approval_floor"]["value"], "none"
        )

    def test_no_reachable_connector_derives_nothing(self):
        inventory = _inventory()
        inventory["relations"] = [
            {"id": "r1", "source": "use-1", "type": "implemented_by", "target": "app-1"}
        ]
        graph = InventoryGraph(inventory)
        self.assertEqual(derive_composition_facts(graph, "use-1"), {})

    def test_direct_fact_wins_over_derived_in_engine(self):
        from air_framework.engine import assess

        inventory = _inventory()
        inventory["objects"][0]["facts"]["composition.can_send_external"] = _fact(False)
        pack = {
            "schema_version": "0.1.0",
            "pack": {
                "id": "test-pack",
                "name": "Test pack",
                "version": "1.0.0",
                "authority_type": "organizational_policy",
                "jurisdiction": "Test",
                "language": "en",
                "source_version": "test",
                "reviewed_at": "2026-08-29",
                "coverage": ["External send capability test"],
                "known_gaps": [],
                "applies_to": ["ai_use"],
            },
            "fact_catalog": [
                {
                    "id": "composition.can_send_external",
                    "type": "boolean",
                    "question": "Can the composition send externally?",
                }
            ],
            "anchors": [
                {
                    "id": "test.anchor",
                    "source": "Test source",
                    "locator": "Section 1",
                    "url": "https://example.org/test-anchor",
                    "summary": "Test anchor.",
                }
            ],
            "rules": [
                {
                    "id": "test.rule.external-send",
                    "title": "External send capability",
                    "kind": "control_gap",
                    "applies_to": ["ai_use"],
                    "when": {
                        "fact": {
                            "key": "composition.can_send_external",
                            "operator": "eq",
                            "value": True,
                        }
                    },
                    "finding": {
                        "code": "TEST-SEND",
                        "level": "informational",
                        "title": "External send available",
                        "summary": "The composition can send externally.",
                    },
                    "anchors": ["test.anchor"],
                }
            ],
        }
        declared = assess(inventory, pack, "use-1", assessed_at="2026-08-29T12:00:00Z")
        self.assertEqual(
            declared["effective_facts"]["composition.can_send_external"]["value"], False
        )
        self.assertEqual(declared["findings"], [])

        derived_inventory = _inventory()
        derived = assess(
            derived_inventory, pack, "use-1", assessed_at="2026-08-29T12:00:00Z"
        )
        derived_fact = derived["effective_facts"]["composition.can_send_external"]
        self.assertTrue(derived_fact["value"])
        self.assertEqual(derived_fact["provenance"], "derived")
        self.assertEqual(derived["findings"][0]["status"], "matched")


if __name__ == "__main__":
    unittest.main()
