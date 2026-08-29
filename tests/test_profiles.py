# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from air_framework.errors import ValidationError
from air_framework.profiles import assess_profile, load_profile_packs

ROOT = Path(__file__).resolve().parents[1]


class ProfileTests(unittest.TestCase):
    def test_pinned_profile_assesses_every_compatible_pack(self):
        profile, packs = load_profile_packs(ROOT / "examples/ai-governance/pack-profile.json")
        inventory = json.loads(
            (ROOT / "examples/ai-governance/inventory.json").read_text(encoding="utf-8")
        )
        result = assess_profile(
            inventory,
            profile,
            packs,
            "use-recruiting-assistant",
            assessed_at="2026-08-29T12:00:00Z",
        )
        pack_ids = {item["pack"]["id"] for item in result["assessments"]}
        self.assertEqual(
            {"eu-ai-act-core", "eu-gdpr-ai-core", "nist-ai-rmf-core"}, pack_ids
        )
        versions = {
            item["pack"]["id"]: item["pack"]["version"]
            for item in result["assessments"]
        }
        self.assertEqual(
            {
                "eu-ai-act-core": "1.1.0",
                "eu-gdpr-ai-core": "1.1.0",
                "nist-ai-rmf-core": "1.1.0",
            },
            versions,
        )
        self.assertTrue(
            all(
                assessment["summary"]["indeterminate"] == 0
                for assessment in result["assessments"]
            )
        )

    def test_wrong_content_hash_breaks_a_pack_pin(self):
        source = ROOT / "examples/ai-governance/pack-profile.json"
        profile = deepcopy(json.loads(source.read_text(encoding="utf-8")))
        profile["packs"][0]["content_hash"] = "0" * 64
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".json",
            dir=source.parent,
            delete=False,
        ) as handle:
            json.dump(profile, handle)
            temporary_path = Path(handle.name)
        try:
            with self.assertRaises(ValidationError):
                load_profile_packs(temporary_path)
        finally:
            temporary_path.unlink(missing_ok=True)

    def test_profile_assessment_id_is_stable_across_run_times(self):
        profile, packs = load_profile_packs(ROOT / "examples/ai-governance/pack-profile.json")
        inventory = json.loads(
            (ROOT / "examples/ai-governance/inventory.json").read_text(encoding="utf-8")
        )
        first = assess_profile(
            inventory,
            profile,
            packs,
            "use-recruiting-assistant",
            assessed_at="2026-08-29T12:00:00Z",
        )
        second = assess_profile(
            inventory,
            profile,
            packs,
            "use-recruiting-assistant",
            assessed_at="2026-09-01T12:00:00Z",
        )
        self.assertEqual(first["profile_assessment_id"], second["profile_assessment_id"])
        self.assertEqual(first["result_hash"], second["result_hash"])
        self.assertNotEqual(
            first["assessments"][0]["assessed_at"],
            second["assessments"][0]["assessed_at"],
        )


if __name__ == "__main__":
    unittest.main()
