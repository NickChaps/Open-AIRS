# SPDX-License-Identifier: Apache-2.0
"""Three-valued condition language used by deterministic rule packs."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence

from .errors import EvaluationError
from .graph import InventoryGraph


class Truth(str, Enum):
    TRUE = "true"
    FALSE = "false"
    UNKNOWN = "unknown"


@dataclass
class Trace:
    truth: Truth
    facts: set[str] = field(default_factory=set)
    evidence: set[str] = field(default_factory=set)
    missing: set[str] = field(default_factory=set)
    conflicts: set[str] = field(default_factory=set)
    related_objects: set[str] = field(default_factory=set)

    def merge(self, other: "Trace") -> None:
        self.facts.update(other.facts)
        self.evidence.update(other.evidence)
        self.missing.update(other.missing)
        self.conflicts.update(other.conflicts)
        self.related_objects.update(other.related_objects)

    def as_dict(self) -> dict[str, Any]:
        return {
            "truth": self.truth.value,
            "facts": sorted(self.facts),
            "evidence": sorted(self.evidence),
            "missing_facts": sorted(self.missing),
            "conflicted_facts": sorted(self.conflicts),
            "related_objects": sorted(self.related_objects),
        }


def _compare(operator: str, actual: Any, expected: Any) -> bool:
    if operator == "eq":
        return actual == expected
    if operator == "neq":
        return actual != expected
    if operator == "in":
        return actual in expected
    if operator == "not_in":
        return actual not in expected
    if operator == "contains":
        return expected in actual
    if operator == "contains_any":
        return any(item in actual for item in expected)
    if operator == "contains_all":
        return all(item in actual for item in expected)
    if operator == "truthy":
        return bool(actual)
    if operator == "gt":
        return actual > expected
    if operator == "gte":
        return actual >= expected
    if operator == "lt":
        return actual < expected
    if operator == "lte":
        return actual <= expected
    raise EvaluationError(f"Unsupported fact operator {operator!r}")


def _fact_trace(spec: Mapping[str, Any], facts: Mapping[str, Any]) -> Trace:
    key = spec.get("key")
    if not isinstance(key, str):
        raise EvaluationError("A fact condition requires a string 'key'")
    operator = spec.get("operator", "eq")
    fact = facts.get(key)
    trace = Trace(Truth.UNKNOWN, facts={key})
    if operator == "exists":
        trace.truth = Truth.TRUE if fact is not None else Truth.FALSE
        if fact is None:
            trace.missing.add(key)
        return trace
    if not isinstance(fact, Mapping) or fact.get("state") in {None, "unknown"}:
        trace.missing.add(key)
        return trace
    if fact.get("state") == "conflicted":
        trace.conflicts.add(key)
        trace.evidence.update(fact.get("evidence", []))
        return trace
    if fact.get("state") == "not_applicable":
        trace.truth = Truth.FALSE
        return trace
    trace.evidence.update(fact.get("evidence", []))
    try:
        matched = _compare(operator, fact.get("value"), spec.get("value"))
    except (TypeError, ValueError) as exc:
        raise EvaluationError(
            f"Cannot apply operator {operator!r} to fact {key!r}: {exc}"
        ) from exc
    trace.truth = Truth.TRUE if matched else Truth.FALSE
    return trace


def evaluate_condition(
    expression: Mapping[str, Any],
    *,
    object_id: str,
    facts: Mapping[str, Any],
    graph: InventoryGraph,
    inheritance: Sequence[Mapping[str, Any]],
) -> Trace:
    """Evaluate an expression without collapsing missing facts into false."""

    if set(expression) == {"literal"}:
        return Trace(Truth.TRUE if expression["literal"] else Truth.FALSE)
    if "fact" in expression:
        spec = expression["fact"]
        if not isinstance(spec, Mapping):
            raise EvaluationError("'fact' must contain an object")
        return _fact_trace(spec, facts)
    if "not" in expression:
        child = evaluate_condition(
            expression["not"],
            object_id=object_id,
            facts=facts,
            graph=graph,
            inheritance=inheritance,
        )
        child.truth = {
            Truth.TRUE: Truth.FALSE,
            Truth.FALSE: Truth.TRUE,
            Truth.UNKNOWN: Truth.UNKNOWN,
        }[child.truth]
        return child
    if "all" in expression or "any" in expression:
        mode = "all" if "all" in expression else "any"
        children = expression[mode]
        if not isinstance(children, list) or not children:
            raise EvaluationError(f"'{mode}' requires a non-empty list")
        traces = [
            evaluate_condition(
                child,
                object_id=object_id,
                facts=facts,
                graph=graph,
                inheritance=inheritance,
            )
            for child in children
        ]
        truths = {item.truth for item in traces}
        if mode == "all":
            truth = Truth.FALSE if Truth.FALSE in truths else (
                Truth.UNKNOWN if Truth.UNKNOWN in truths else Truth.TRUE
            )
        else:
            truth = Truth.TRUE if Truth.TRUE in truths else (
                Truth.UNKNOWN if Truth.UNKNOWN in truths else Truth.FALSE
            )
        result = Trace(truth)
        contributors = traces
        if mode == "all" and truth == Truth.FALSE:
            contributors = [child for child in traces if child.truth == Truth.FALSE]
        elif mode == "any" and truth == Truth.TRUE:
            contributors = [child for child in traces if child.truth == Truth.TRUE]
        for child in contributors:
            result.merge(child)
        return result
    if "related" in expression:
        spec = expression["related"]
        if not isinstance(spec, Mapping):
            raise EvaluationError("'related' must contain an object")
        path = spec.get("path")
        where = spec.get("where")
        if not isinstance(path, list) or not isinstance(where, Mapping):
            raise EvaluationError("A related condition requires 'path' and 'where'")
        related_ids = graph.follow(object_id, path)
        object_types = set(spec.get("object_types", []))
        if object_types:
            related_ids = [
                item for item in related_ids if graph.object(item)["type"] in object_types
            ]
        quantifier = spec.get("quantifier", "any")
        if quantifier not in {"any", "all", "none"}:
            raise EvaluationError(f"Unsupported related quantifier {quantifier!r}")
        if not related_ids:
            return Trace(Truth.FALSE if quantifier in {"any", "all"} else Truth.TRUE)
        traces: list[Trace] = []
        for related_id in related_ids:
            related_facts = graph.effective_facts(related_id, inheritance)
            child = evaluate_condition(
                where,
                object_id=related_id,
                facts=related_facts,
                graph=graph,
                inheritance=inheritance,
            )
            child.related_objects.add(related_id)
            traces.append(child)
        truths = {item.truth for item in traces}
        if quantifier == "any":
            truth = Truth.TRUE if Truth.TRUE in truths else (
                Truth.UNKNOWN if Truth.UNKNOWN in truths else Truth.FALSE
            )
        elif quantifier == "all":
            truth = Truth.FALSE if Truth.FALSE in truths else (
                Truth.UNKNOWN if Truth.UNKNOWN in truths else Truth.TRUE
            )
        else:
            truth = Truth.FALSE if Truth.TRUE in truths else (
                Truth.UNKNOWN if Truth.UNKNOWN in truths else Truth.TRUE
            )
        result = Trace(truth)
        contributors = traces
        if quantifier == "any" and truth == Truth.TRUE:
            contributors = [child for child in traces if child.truth == Truth.TRUE]
        elif quantifier == "all" and truth == Truth.FALSE:
            contributors = [child for child in traces if child.truth == Truth.FALSE]
        elif quantifier == "none" and truth == Truth.FALSE:
            contributors = [child for child in traces if child.truth == Truth.TRUE]
        for child in contributors:
            result.merge(child)
        return result
    raise EvaluationError(
        "Condition must contain exactly one of: literal, fact, not, all, any, related"
    )
