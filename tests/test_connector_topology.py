# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import unittest
from pathlib import Path

from air_framework.graph import InventoryGraph
from air_framework.validation import validate_inventory

ROOT = Path(__file__).resolve().parents[1]


class ConnectorTopologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = json.loads(
            (ROOT / "examples/connector-topologies/inventory.json").read_text(
                encoding="utf-8"
            )
        )
        validate_inventory(cls.inventory)
        cls.graph = InventoryGraph(cls.inventory)

    def test_company_connector_is_available_through_each_platform(self):
        for application in ["app-research", "app-casework", "app-payroll"]:
            with self.subTest(application=application):
                self.assertIn(
                    "connector-company-search",
                    self.graph.follow(application, ["runs_on", "can_invoke"]),
                )

    def test_private_connector_is_available_only_to_its_application(self):
        self.assertEqual(
            ["connector-case-export"],
            self.graph.follow("app-casework", ["can_invoke"]),
        )
        for application in ["app-research", "app-payroll"]:
            with self.subTest(application=application):
                self.assertNotIn(
                    "connector-case-export",
                    self.graph.follow(application, ["can_invoke"]),
                )
                self.assertNotIn(
                    "connector-case-export",
                    self.graph.follow(application, ["runs_on", "can_invoke"]),
                )


if __name__ == "__main__":
    unittest.main()
