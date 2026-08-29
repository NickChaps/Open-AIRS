# SPDX-License-Identifier: Apache-2.0
"""Version-pinned multi-pack profiles."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .canonical import content_hash
from .engine import assess
from .errors import ValidationError
from .io import load_json
from .validation import validate_inventory, validate_pack, validate_pack_profile


def load_profile_packs(profile_path: str | Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Load a profile and verify that every local pack matches its pin."""

    source = Path(profile_path)
    profile = load_json(source)
    validate_pack_profile(profile)
    packs: list[dict[str, Any]] = []
    for pin in profile["packs"]:
        pack_path = (source.parent / pin["path"]).resolve()
        pack = load_json(pack_path)
        validate_pack(pack)
        metadata = pack["pack"]
        if metadata["id"] != pin["id"] or metadata["version"] != pin["version"]:
            raise ValidationError(
                f"Pack pin {pin['id']}@{pin['version']} does not match "
                f"{metadata['id']}@{metadata['version']} at {pack_path}"
            )
        expected_hash = pin.get("content_hash")
        actual_hash = content_hash(pack)
        if expected_hash and expected_hash != actual_hash:
            raise ValidationError(
                f"Pack pin {pin['id']} content hash mismatch: expected {expected_hash}, got {actual_hash}"
            )
        packs.append(pack)
    return profile, packs


def assess_profile(
    inventory: Mapping[str, Any],
    profile: Mapping[str, Any],
    packs: Sequence[Mapping[str, Any]],
    target_id: str,
    *,
    assessed_at: str | None = None,
) -> dict[str, Any]:
    """Assess one target with every compatible pack in a pinned profile."""

    validate_inventory(inventory)
    validate_pack_profile(profile)
    target = next((item for item in inventory["objects"] if item["id"] == target_id), None)
    if target is None:
        raise ValidationError(f"Unknown target object {target_id!r}")
    results = [
        assess(inventory, pack, target_id, assessed_at=assessed_at)
        for pack in packs
        if target["type"] in pack["pack"]["applies_to"]
    ]
    stable = {
        "schema_version": "0.1.0",
        "profile": {
            "id": profile["profile"]["id"],
            "version": profile["profile"]["version"],
            "content_hash": content_hash(profile),
        },
        "target": {"id": target["id"], "type": target["type"], "name": target["name"]},
    }
    hash_material = {
        **stable,
        "assessment_result_hashes": [item["result_hash"] for item in results],
    }
    result_hash = content_hash(hash_material)
    return {
        "profile_assessment_id": f"urn:air:profile-assessment:{result_hash[:24]}",
        "result_hash": result_hash,
        **stable,
        "assessments": results,
    }
