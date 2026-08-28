# SPDX-License-Identifier: Apache-2.0
"""Deterministic assessment engine."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Mapping

from .canonical import content_hash
from .conditions import Truth, evaluate_condition
from .errors import EvaluationError
from .graph import InventoryGraph
from .validation import validate_inventory, validate_pack
from .version import __version__


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def assess(
    inventory: Mapping[str, Any],
    pack: Mapping[str, Any],
    target_id: str,
    *,
    assessed_at: str | None = None,
    include_not_matched: bool = False,
) -> dict[str, Any]:
    """Evaluate one object against one immutable pack version.

    Missing and conflicting evidence produce an ``indeterminate`` rule result;
    they are never silently interpreted as compliance or non-applicability.
    """

    validate_inventory(inventory)
    validate_pack(pack)
    graph = InventoryGraph(inventory)
    target = graph.object(target_id)
    metadata = pack["pack"]
    if target["type"] not in metadata["applies_to"]:
        raise EvaluationError(
            f"Pack {metadata['id']!r} does not apply to object type {target['type']!r}"
        )
    inheritance = pack.get("inheritance", [])
    effective_facts = graph.effective_facts(target_id, inheritance)
    anchor_index = {item["id"]: item for item in pack["anchors"]}
    findings: list[dict[str, Any]] = []
    for rule in pack["rules"]:
        if target["type"] not in rule["applies_to"]:
            continue
        trace = evaluate_condition(
            rule["when"],
            object_id=target_id,
            facts=effective_facts,
            graph=graph,
            inheritance=inheritance,
        )
        status = {
            Truth.TRUE: "matched",
            Truth.FALSE: "not_matched",
            Truth.UNKNOWN: "indeterminate",
        }[trace.truth]
        if status == "not_matched" and not include_not_matched:
            continue
        finding = {
            "rule_id": rule["id"],
            "status": status,
            "kind": rule["kind"],
            "finding": deepcopy(rule["finding"]),
            "reason": deepcopy(
                rule.get(
                    "reason",
                    {
                        "matched": "The deterministic condition matched the supplied facts.",
                        "indeterminate": "The condition cannot be resolved from the available evidence.",
                        "not_matched": "The deterministic condition did not match the supplied facts.",
                    },
                ).get(status)
            ),
            "trace": trace.as_dict(),
            "anchors": [deepcopy(anchor_index[item]) for item in rule["anchors"]],
            "obligations": deepcopy(rule.get("obligations", [])) if status == "matched" else [],
        }
        findings.append(finding)

    stable_result = {
        "schema_version": "0.1.0",
        "engine_version": __version__,
        "inventory": {
            "inventory_id": inventory["inventory_id"],
            "snapshot_id": inventory["snapshot_id"],
            "content_hash": content_hash(inventory),
        },
        "pack": {
            "id": metadata["id"],
            "version": metadata["version"],
            "authority_type": metadata["authority_type"],
            "content_hash": content_hash(pack),
        },
        "target": {"id": target["id"], "type": target["type"], "name": target["name"]},
        "effective_facts": effective_facts,
        "findings": findings,
        "summary": {
            "matched": sum(item["status"] == "matched" for item in findings),
            "indeterminate": sum(item["status"] == "indeterminate" for item in findings),
            "not_matched": sum(item["status"] == "not_matched" for item in findings),
        },
    }
    result_hash = content_hash(stable_result)
    return {
        "assessment_id": f"urn:air:assessment:{result_hash[:24]}",
        "assessed_at": assessed_at or _utc_now(),
        "result_hash": result_hash,
        **stable_result,
    }


def diff_assessments(before: Mapping[str, Any], after: Mapping[str, Any]) -> dict[str, Any]:
    """Compare findings by stable rule id for drift review."""

    before_rules = {item["rule_id"]: item for item in before.get("findings", [])}
    after_rules = {item["rule_id"]: item for item in after.get("findings", [])}
    added = sorted(set(after_rules) - set(before_rules))
    removed = sorted(set(before_rules) - set(after_rules))
    changed = sorted(
        rule_id
        for rule_id in set(before_rules) & set(after_rules)
        if before_rules[rule_id].get("status") != after_rules[rule_id].get("status")
        or before_rules[rule_id].get("finding") != after_rules[rule_id].get("finding")
    )
    return {
        "before": before.get("assessment_id"),
        "after": after.get("assessment_id"),
        "added": [after_rules[item] for item in added],
        "removed": [before_rules[item] for item in removed],
        "changed": [
            {"rule_id": item, "before": before_rules[item], "after": after_rules[item]}
            for item in changed
        ],
        "has_drift": bool(added or removed or changed),
    }


def assess_inventory(
    inventory: Mapping[str, Any],
    pack: Mapping[str, Any],
    *,
    assessed_at: str | None = None,
    include_not_matched: bool = False,
) -> list[dict[str, Any]]:
    """Assess every object type declared by a pack in inventory order."""

    validate_inventory(inventory)
    validate_pack(pack)
    supported = set(pack["pack"]["applies_to"])
    return [
        assess(
            inventory,
            pack,
            item["id"],
            assessed_at=assessed_at,
            include_not_matched=include_not_matched,
        )
        for item in inventory["objects"]
        if item["type"] in supported
    ]


def pack_impact(
    inventory: Mapping[str, Any],
    before_pack: Mapping[str, Any],
    after_pack: Mapping[str, Any],
    *,
    assessed_at: str | None = None,
) -> dict[str, Any]:
    """Dry-run a candidate pack and report object-by-object assessment drift."""

    before_results = {
        item["target"]["id"]: item
        for item in assess_inventory(inventory, before_pack, assessed_at=assessed_at)
    }
    after_results = {
        item["target"]["id"]: item
        for item in assess_inventory(inventory, after_pack, assessed_at=assessed_at)
    }
    targets = sorted(set(before_results) | set(after_results))
    changes: list[dict[str, Any]] = []
    for target_id in targets:
        if target_id not in before_results:
            changes.append({"target_id": target_id, "change": "newly_applicable"})
        elif target_id not in after_results:
            changes.append({"target_id": target_id, "change": "no_longer_applicable"})
        else:
            diff = diff_assessments(before_results[target_id], after_results[target_id])
            if diff["has_drift"]:
                changes.append({"target_id": target_id, "change": "findings_changed", "diff": diff})
    return {
        "schema_version": "0.1.0",
        "inventory": {
            "inventory_id": inventory["inventory_id"],
            "snapshot_id": inventory["snapshot_id"],
        },
        "before_pack": {
            "id": before_pack["pack"]["id"],
            "version": before_pack["pack"]["version"],
            "content_hash": content_hash(before_pack),
        },
        "after_pack": {
            "id": after_pack["pack"]["id"],
            "version": after_pack["pack"]["version"],
            "content_hash": content_hash(after_pack),
        },
        "changes": changes,
        "has_impact": bool(changes),
    }
