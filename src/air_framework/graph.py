# SPDX-License-Identifier: Apache-2.0
"""Object graph traversal and explicitly scoped fact inheritance."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from typing import Any

from .errors import EvaluationError


class InventoryGraph:
    """Indexed, read-only view of an inventory snapshot."""

    def __init__(self, inventory: Mapping[str, Any]) -> None:
        self.inventory = inventory
        self.objects = {item["id"]: item for item in inventory["objects"]}
        self.relations = list(inventory["relations"])

    def object(self, object_id: str) -> Mapping[str, Any]:
        try:
            return self.objects[object_id]
        except KeyError as exc:
            raise EvaluationError(f"Unknown target object {object_id!r}") from exc

    def neighbours(
        self,
        object_ids: Sequence[str],
        relation_type: str,
        direction: str = "outgoing",
    ) -> list[str]:
        """Return unique adjacent objects in deterministic inventory order."""

        if direction not in {"outgoing", "incoming"}:
            raise EvaluationError(f"Unsupported relation direction {direction!r}")
        wanted = set(object_ids)
        result: list[str] = []
        seen: set[str] = set()
        for relation in self.relations:
            if relation["type"] != relation_type:
                continue
            left = relation["source"] if direction == "outgoing" else relation["target"]
            right = relation["target"] if direction == "outgoing" else relation["source"]
            if left in wanted and right not in seen:
                seen.add(right)
                result.append(right)
        return result

    def follow(self, start_id: str, path: Sequence[Any]) -> list[str]:
        current = [start_id]
        for raw_step in path:
            if isinstance(raw_step, str):
                relation_type = raw_step
                direction = "outgoing"
            elif isinstance(raw_step, Mapping):
                relation_type = raw_step.get("relation")
                direction = raw_step.get("direction", "outgoing")
                if not isinstance(relation_type, str):
                    raise EvaluationError("A relation path step requires a string 'relation'")
            else:
                raise EvaluationError("Relation path steps must be strings or objects")
            current = self.neighbours(current, relation_type, direction)
            if not current:
                break
        return current

    def effective_facts(
        self,
        object_id: str,
        policies: Sequence[Mapping[str, Any]],
    ) -> dict[str, Any]:
        """Resolve direct facts plus pack-declared inheritance policies.

        Direct known facts win.  Multiple different inherited values become a
        conflict; the engine never guesses which parent is authoritative.
        """

        target = self.object(object_id)
        resolved = deepcopy(target.get("facts", {}))
        for policy in policies:
            fact_key = policy["fact"]
            if fact_key in resolved and resolved[fact_key].get("state") == "known":
                continue
            parent_ids = self.follow(object_id, policy["path"])
            object_types = set(policy.get("object_types", []))
            candidates: list[tuple[str, Mapping[str, Any]]] = []
            for parent_id in parent_ids:
                parent = self.object(parent_id)
                if object_types and parent["type"] not in object_types:
                    continue
                fact = parent.get("facts", {}).get(fact_key)
                if isinstance(fact, Mapping) and fact.get("state") == "known":
                    candidates.append((parent_id, fact))
            if not candidates:
                continue
            values: list[Any] = []
            for _, fact in candidates:
                if fact.get("value") not in values:
                    values.append(fact.get("value"))
            evidence = sorted(
                {
                    evidence_id
                    for _, fact in candidates
                    for evidence_id in fact.get("evidence", [])
                }
            )
            if len(values) == 1:
                resolved[fact_key] = {
                    "state": "known",
                    "value": values[0],
                    "evidence": evidence,
                    "provenance": "inherited",
                    "inherited_from": [parent_id for parent_id, _ in candidates],
                    "inheritance_policy": policy["id"],
                }
            else:
                resolved[fact_key] = {
                    "state": "conflicted",
                    "evidence": evidence,
                    "provenance": "inherited",
                    "inherited_from": [parent_id for parent_id, _ in candidates],
                    "candidate_values": values,
                    "inheritance_policy": policy["id"],
                }
        return resolved
