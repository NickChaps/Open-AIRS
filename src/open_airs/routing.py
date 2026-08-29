# SPDX-License-Identifier: Apache-2.0
"""Optional organisation-owned routing over immutable findings."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .canonical import content_hash
from .validation import validate_route_profile

SELECTORS = {
    "statuses": lambda assessment, finding: finding.get("status"),
    "levels": lambda assessment, finding: finding.get("finding", {}).get("level"),
    "finding_codes": lambda assessment, finding: finding.get("finding", {}).get("code"),
    "kinds": lambda assessment, finding: finding.get("kind"),
    "rule_ids": lambda assessment, finding: finding.get("rule_id"),
    "pack_ids": lambda assessment, finding: assessment.get("pack", {}).get("id"),
}


def _matches(
    assessment: Mapping[str, Any], finding: Mapping[str, Any], match: Mapping[str, Any]
) -> bool:
    for selector, allowed in match.items():
        if selector not in SELECTORS:
            return False
        if not isinstance(allowed, list) or SELECTORS[selector](assessment, finding) not in allowed:
            return False
    return True


def apply_routes(
    assessments: Sequence[Mapping[str, Any]], profile: Mapping[str, Any]
) -> dict[str, Any]:
    """Assign zero or more routes without mutating legal or framework results."""

    validate_route_profile(profile)
    route_index = {item["id"]: item for item in profile["routes"]}
    assignments: dict[str, dict[str, Any]] = {}
    for assessment in assessments:
        for finding in assessment.get("findings", []):
            for mapping in profile["mappings"]:
                if not _matches(assessment, finding, mapping["match"]):
                    continue
                route_id = mapping["route"]
                bucket = assignments.setdefault(
                    route_id,
                    {
                        "route": route_index[route_id],
                        "matches": [],
                    },
                )
                bucket["matches"].append(
                    {
                        "assessment_id": assessment.get("assessment_id"),
                        "target": assessment.get("target"),
                        "pack": assessment.get("pack"),
                        "rule_id": finding.get("rule_id"),
                        "status": finding.get("status"),
                        "finding": finding.get("finding"),
                        "mapping_id": mapping["id"],
                    }
                )
    ordered = sorted(
        assignments.values(),
        key=lambda item: (item["route"]["priority"], item["route"]["id"]),
    )
    stable_result = {
        "schema_version": "0.1.0",
        "profile": {
            "id": profile["profile"]["id"],
            "version": profile["profile"]["version"],
            "content_hash": content_hash(profile),
        },
        "assessment_ids": [item.get("assessment_id") for item in assessments],
        "assignments": ordered,
    }
    result_hash = content_hash(stable_result)
    return {
        "routing_id": f"urn:open-airs:routing:{result_hash[:24]}",
        "result_hash": result_hash,
        **stable_result,
    }
