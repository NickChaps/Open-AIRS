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


if __name__ == "__main__":
    unittest.main()
