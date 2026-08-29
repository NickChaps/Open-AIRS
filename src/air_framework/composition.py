# SPDX-License-Identifier: Apache-2.0
"""Deterministic derivation of composition facts from connector actions.

The language model reads intent. Connector capability, scope and approval
gates are captured configuration, so they are combined here without a model.
Derived facts never assert more than the captured snapshot supports: a
positive capability found on one connector is emitted even when other
connectors are undocumented, while a negative conclusion requires every
reachable connector to declare its actions.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .graph import InventoryGraph

DERIVATION_ID = "composition.v1"

ACTION_KINDS = (
    "read",
    "send_internal",
    "write",
    "execute",
    "delete",
    "send_external",
)

APPROVAL_LEVELS = (
    "none",
    "standing_user_authorization",
    "per_conversation",
    "per_action",
)

_AUTONOMOUS_APPROVALS = {"none", "standing_user_authorization"}
_APPROVAL_ORDER = {level: index for index, level in enumerate(APPROVAL_LEVELS)}

ENFORCEMENT_MECHANISMS = ("connector", "platform")

_CONNECTOR_PATHS: dict[str, tuple[tuple[str, ...], ...]] = {
    "ai_use": (
        ("implemented_by", "can_invoke"),
        ("implemented_by", "runs_on", "can_invoke"),
    ),
    "configured_ai_application": (
        ("can_invoke",),
        ("runs_on", "can_invoke"),
    ),
    "ai_system": (
        ("can_invoke",),
        ("runs_on", "can_invoke"),
    ),
    "ai_platform": (("can_invoke",),),
}


def reachable_connectors(graph: InventoryGraph, target_id: str) -> list[str]:
    """Return connectors reachable from the target in deterministic order."""

    target = graph.object(target_id)
    paths = _CONNECTOR_PATHS.get(target["type"], ())
    ordered: list[str] = []
    seen: set[str] = set()
    for path in paths:
        for connector_id in graph.follow(target_id, list(path)):
            if connector_id in seen:
                continue
            if graph.object(connector_id)["type"] != "connector":
                continue
            seen.add(connector_id)
            ordered.append(connector_id)
    return ordered


def _known_actions(
    graph: InventoryGraph, connector_ids: list[str]
) -> tuple[list[tuple[str, Mapping[str, Any]]], set[str], bool]:
    """Collect declared actions, their evidence and a completeness flag."""

    actions: list[tuple[str, Mapping[str, Any]]] = []
    evidence: set[str] = set()
    complete = True
    for connector_id in connector_ids:
        fact = graph.object(connector_id).get("facts", {}).get("connector.actions")
        if (
            not isinstance(fact, Mapping)
            or fact.get("state") != "known"
            or not isinstance(fact.get("value"), list)
        ):
            complete = False
            continue
        declared = [item for item in fact["value"] if isinstance(item, Mapping)]
        if len(declared) != len(fact["value"]):
            complete = False
        evidence.update(str(item) for item in fact.get("evidence", []))
        for action in declared:
            if action.get("kind") not in ACTION_KINDS:
                complete = False
                continue
            actions.append((connector_id, action))
    return actions, evidence, complete


_GATE_AUTONOMOUS = "autonomous"
_GATE_GATED = "gated"
_GATE_UNKNOWN = "unknown"


def _gate_state(action: Mapping[str, Any]) -> str:
    """Three-valued reading of one action's human gate.

    Autonomy is a positive claim, so it needs positive grounds: a permissive
    approval level, an explicitly or malformedly bypassable gate, or an
    approval that no technical mechanism imposes (a policy wish). A gate is
    demonstrable only when the declaration is complete: a gated approval,
    ``enforced_by`` connector or platform, and ``bypassable`` explicitly
    false. An enforced gate whose bypassability is simply not stated proves
    neither, so it stays unknown instead of becoming a reassuring gate or an
    established autonomy.
    """

    bypassable = action.get("bypassable")
    if bypassable is not None and not isinstance(bypassable, bool):
        return _GATE_AUTONOMOUS
    if bypassable is True:
        return _GATE_AUTONOMOUS
    approval = action.get("approval")
    if approval not in APPROVAL_LEVELS:
        return _GATE_AUTONOMOUS
    if approval in _AUTONOMOUS_APPROVALS:
        return _GATE_AUTONOMOUS
    if action.get("enforced_by") not in ENFORCEMENT_MECHANISMS:
        return _GATE_AUTONOMOUS
    if bypassable is False:
        return _GATE_GATED
    return _GATE_UNKNOWN


def derive_composition_facts(
    graph: InventoryGraph, target_id: str
) -> dict[str, dict[str, Any]]:
    """Derive connector-capability facts for one composition target.

    Returned facts carry ``provenance: "derived"`` and never overwrite a
    direct fact: the engine only uses them to fill gaps before pack-declared
    inheritance is applied.
    """

    connector_ids = reachable_connectors(graph, target_id)
    if not connector_ids:
        return {}
    actions, evidence, complete = _known_actions(graph, connector_ids)

    def known(value: Any) -> dict[str, Any]:
        return {
            "state": "known",
            "value": value,
            "evidence": sorted(evidence),
            "provenance": "derived",
            "derived_from": list(connector_ids),
            "derivation": DERIVATION_ID,
        }

    def unknown(note: str) -> dict[str, Any]:
        return {
            "state": "unknown",
            "note": note,
            "provenance": "derived",
            "derived_from": list(connector_ids),
            "derivation": DERIVATION_ID,
        }

    facts: dict[str, dict[str, Any]] = {}
    incomplete_note = (
        "At least one reachable connector does not declare connector.actions, "
        "so the absence of a capability cannot be established."
    )
    gate_note = (
        "A declared gate does not state whether it can be bypassed, so "
        "autonomy can be neither established nor excluded."
    )

    external_sends = [action for _, action in actions if action.get("kind") == "send_external"]
    if external_sends:
        facts["composition.can_send_external"] = known(True)
    elif complete:
        facts["composition.can_send_external"] = known(False)
    else:
        facts["composition.can_send_external"] = unknown(incomplete_note)

    send_gates = [_gate_state(action) for action in external_sends]
    if _GATE_AUTONOMOUS in send_gates:
        facts["composition.autonomous_external_send_possible"] = known(True)
    elif _GATE_UNKNOWN in send_gates:
        facts["composition.autonomous_external_send_possible"] = unknown(gate_note)
    elif complete:
        facts["composition.autonomous_external_send_possible"] = known(False)
    else:
        facts["composition.autonomous_external_send_possible"] = unknown(incomplete_note)

    engaging = [action for _, action in actions if action.get("kind") != "read"]
    if engaging:
        floors: list[str] = []
        floor_unknown = False
        for action in engaging:
            state = _gate_state(action)
            if state == _GATE_AUTONOMOUS:
                floors.append("none")
            elif state == _GATE_GATED:
                floors.append(action["approval"])
            else:
                floor_unknown = True
        floor = min(floors, key=lambda level: _APPROVAL_ORDER[level]) if floors else None
        if floor == "none":
            facts["composition.engaging_action_approval_floor"] = known(floor)
        elif floor_unknown:
            facts["composition.engaging_action_approval_floor"] = unknown(gate_note)
        elif complete:
            facts["composition.engaging_action_approval_floor"] = known(floor)
        else:
            facts["composition.engaging_action_approval_floor"] = unknown(incomplete_note)

    return facts
