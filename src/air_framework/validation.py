# SPDX-License-Identifier: Apache-2.0
"""Dependency-free structural validation for public interchange files."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from .errors import ValidationError

SCHEMA_VERSION = "0.1.0"
OBJECT_TYPES = {
    "ai_system",
    "ai_platform",
    "configured_ai_application",
    "agent_skill",
    "connector",
    "model",
    "ai_use",
    "organization",
    "provider",
    "service",
    "contract",
    "clause_library",
    "generic",
}
FACT_STATES = {"known", "unknown", "conflicted", "not_applicable"}
FACT_TYPES = {"boolean", "string", "array", "number", "integer", "object"}
AUTHORITY_TYPES = {
    "binding_law",
    "regulatory_guidance",
    "voluntary_framework",
    "organizational_policy",
    "fictional_example",
}
CONDITION_OPERATORS = {"literal", "fact", "not", "all", "any", "related"}
FACT_OPERATORS = {
    "eq",
    "neq",
    "in",
    "not_in",
    "contains",
    "contains_any",
    "contains_all",
    "truthy",
    "exists",
    "gt",
    "gte",
    "lt",
    "lte",
}
ROUTE_SELECTORS = {
    "statuses",
    "levels",
    "finding_codes",
    "kinds",
    "rule_ids",
    "pack_ids",
}
RELATION_SIGNATURES = {
    "runs_on": (
        {"configured_ai_application", "ai_system"},
        {"ai_platform"},
    ),
    "loads_skill": (
        {"configured_ai_application", "ai_platform", "ai_system"},
        {"agent_skill"},
    ),
    "can_invoke": (
        {"configured_ai_application", "ai_platform", "ai_system"},
        {"connector"},
    ),
    "offers_model": ({"ai_platform", "ai_system"}, {"model"}),
    "implemented_by": (
        {"ai_use"},
        {"configured_ai_application", "ai_platform", "ai_system"},
    ),
}


def _require(mapping: Mapping[str, Any], key: str, expected: type, path: str) -> Any:
    if key not in mapping:
        raise ValidationError(f"{path}.{key}: required field is missing")
    value = mapping[key]
    if not isinstance(value, expected):
        raise ValidationError(
            f"{path}.{key}: expected {expected.__name__}, got {type(value).__name__}"
        )
    return value


def _unique(items: Iterable[Mapping[str, Any]], key: str, path: str) -> None:
    seen: set[str] = set()
    for index, item in enumerate(items):
        identifier = item.get(key)
        if not isinstance(identifier, str) or not identifier:
            raise ValidationError(f"{path}[{index}].{key}: expected a non-empty string")
        if identifier in seen:
            raise ValidationError(f"{path}: duplicate {key} {identifier!r}")
        seen.add(identifier)


def validate_fact(fact: Any, path: str) -> None:
    if not isinstance(fact, Mapping):
        raise ValidationError(f"{path}: expected an object")
    state = _require(fact, "state", str, path)
    if state not in FACT_STATES:
        raise ValidationError(f"{path}.state: unsupported value {state!r}")
    if state == "known" and "value" not in fact:
        raise ValidationError(f"{path}.value: required when state is 'known'")
    if "evidence" in fact:
        evidence = fact["evidence"]
        if not isinstance(evidence, list) or not all(isinstance(item, str) for item in evidence):
            raise ValidationError(f"{path}.evidence: expected a list of evidence identifiers")


def _validate_relation_path(value: Any, path: str) -> None:
    if not isinstance(value, list) or not value:
        raise ValidationError(f"{path}: expected a non-empty list")
    for index, step in enumerate(value):
        step_path = f"{path}[{index}]"
        if isinstance(step, str):
            if not step:
                raise ValidationError(f"{step_path}: relation name cannot be empty")
            continue
        if not isinstance(step, Mapping):
            raise ValidationError(f"{step_path}: expected a relation name or object")
        unknown = set(step) - {"relation", "direction"}
        if unknown:
            raise ValidationError(f"{step_path}: unsupported fields {sorted(unknown)!r}")
        relation = _require(step, "relation", str, step_path)
        if not relation:
            raise ValidationError(f"{step_path}.relation: cannot be empty")
        direction = step.get("direction", "outgoing")
        if direction not in {"outgoing", "incoming"}:
            raise ValidationError(
                f"{step_path}.direction: expected 'outgoing' or 'incoming'"
            )


def validate_condition(expression: Any, path: str = "condition") -> None:
    """Validate the complete v0.1 condition language recursively.

    A pack must have one unambiguous operator at every node. This prevents a
    typo or an extra operator from being silently accepted by the evaluator.
    """

    if not isinstance(expression, Mapping):
        raise ValidationError(f"{path}: expected an object")
    operators = set(expression).intersection(CONDITION_OPERATORS)
    unknown = set(expression) - CONDITION_OPERATORS
    if unknown:
        raise ValidationError(f"{path}: unsupported fields {sorted(unknown)!r}")
    if len(operators) != 1 or len(expression) != 1:
        raise ValidationError(
            f"{path}: expected exactly one of {sorted(CONDITION_OPERATORS)!r}"
        )
    operator = next(iter(operators))
    value = expression[operator]

    if operator == "literal":
        if not isinstance(value, bool):
            raise ValidationError(f"{path}.literal: expected a boolean")
        return

    if operator == "fact":
        if not isinstance(value, Mapping):
            raise ValidationError(f"{path}.fact: expected an object")
        unknown = set(value) - {"key", "operator", "value"}
        if unknown:
            raise ValidationError(
                f"{path}.fact: unsupported fields {sorted(unknown)!r}"
            )
        key = _require(value, "key", str, f"{path}.fact")
        if not key:
            raise ValidationError(f"{path}.fact.key: cannot be empty")
        fact_operator = value.get("operator", "eq")
        if fact_operator not in FACT_OPERATORS:
            raise ValidationError(
                f"{path}.fact.operator: unsupported value {fact_operator!r}"
            )
        if fact_operator in {"exists", "truthy"}:
            if "value" in value:
                raise ValidationError(
                    f"{path}.fact.value: not accepted with operator {fact_operator!r}"
                )
        elif "value" not in value:
            raise ValidationError(
                f"{path}.fact.value: required with operator {fact_operator!r}"
            )
        if fact_operator in {"in", "not_in", "contains_any", "contains_all"}:
            expected = value.get("value")
            if not isinstance(expected, list) or not expected:
                raise ValidationError(
                    f"{path}.fact.value: operator {fact_operator!r} requires a non-empty list"
                )
        return

    if operator == "not":
        validate_condition(value, f"{path}.not")
        return

    if operator in {"all", "any"}:
        if not isinstance(value, list) or not value:
            raise ValidationError(f"{path}.{operator}: expected a non-empty list")
        for index, child in enumerate(value):
            validate_condition(child, f"{path}.{operator}[{index}]")
        return

    if not isinstance(value, Mapping):
        raise ValidationError(f"{path}.related: expected an object")
    unknown = set(value) - {"path", "object_types", "quantifier", "where"}
    if unknown:
        raise ValidationError(f"{path}.related: unsupported fields {sorted(unknown)!r}")
    _validate_relation_path(value.get("path"), f"{path}.related.path")
    object_types = value.get("object_types", [])
    if not isinstance(object_types, list):
        raise ValidationError(f"{path}.related.object_types: expected a list")
    for object_type in object_types:
        if object_type not in OBJECT_TYPES:
            raise ValidationError(
                f"{path}.related.object_types: unsupported object type {object_type!r}"
            )
    quantifier = value.get("quantifier", "any")
    if quantifier not in {"any", "all", "none"}:
        raise ValidationError(
            f"{path}.related.quantifier: unsupported value {quantifier!r}"
        )
    if "where" not in value:
        raise ValidationError(f"{path}.related.where: required field is missing")
    validate_condition(value["where"], f"{path}.related.where")


def condition_fact_keys(expression: Mapping[str, Any]) -> set[str]:
    """Collect every fact id referenced by an already validated condition."""

    if "fact" in expression:
        return {expression["fact"]["key"]}
    if "not" in expression:
        return condition_fact_keys(expression["not"])
    if "all" in expression or "any" in expression:
        operator = "all" if "all" in expression else "any"
        return {
            key
            for child in expression[operator]
            for key in condition_fact_keys(child)
        }
    if "related" in expression:
        return condition_fact_keys(expression["related"]["where"])
    return set()


def validate_inventory(inventory: Mapping[str, Any]) -> None:
    """Validate the framework's inventory envelope and referential integrity."""

    version = _require(inventory, "schema_version", str, "inventory")
    if version != SCHEMA_VERSION:
        raise ValidationError(
            f"inventory.schema_version: expected {SCHEMA_VERSION!r}, got {version!r}"
        )
    _require(inventory, "inventory_id", str, "inventory")
    _require(inventory, "snapshot_id", str, "inventory")
    objects = _require(inventory, "objects", list, "inventory")
    relations = _require(inventory, "relations", list, "inventory")
    evidence = _require(inventory, "evidence", list, "inventory")

    if not all(isinstance(item, Mapping) for item in objects):
        raise ValidationError("inventory.objects: every item must be an object")
    if not all(isinstance(item, Mapping) for item in relations):
        raise ValidationError("inventory.relations: every item must be an object")
    if not all(isinstance(item, Mapping) for item in evidence):
        raise ValidationError("inventory.evidence: every item must be an object")
    _unique(objects, "id", "inventory.objects")
    _unique(relations, "id", "inventory.relations")
    _unique(evidence, "id", "inventory.evidence")

    object_ids = {item["id"] for item in objects}
    object_types = {item["id"]: item.get("type") for item in objects}
    evidence_ids = {item["id"] for item in evidence}
    for index, item in enumerate(objects):
        path = f"inventory.objects[{index}]"
        object_type = _require(item, "type", str, path)
        if object_type not in OBJECT_TYPES:
            raise ValidationError(f"{path}.type: unsupported object type {object_type!r}")
        _require(item, "name", str, path)
        facts = item.get("facts", {})
        if not isinstance(facts, Mapping):
            raise ValidationError(f"{path}.facts: expected an object keyed by fact id")
        for key, fact in facts.items():
            if not isinstance(key, str) or not key:
                raise ValidationError(f"{path}.facts: fact keys must be non-empty strings")
            validate_fact(fact, f"{path}.facts[{key!r}]")
            for evidence_id in fact.get("evidence", []):
                if evidence_id not in evidence_ids:
                    raise ValidationError(
                        f"{path}.facts[{key!r}]: unknown evidence id {evidence_id!r}"
                    )

    for index, item in enumerate(relations):
        path = f"inventory.relations[{index}]"
        source = _require(item, "source", str, path)
        target = _require(item, "target", str, path)
        relation_type = _require(item, "type", str, path)
        if source not in object_ids:
            raise ValidationError(f"{path}.source: unknown object id {source!r}")
        if target not in object_ids:
            raise ValidationError(f"{path}.target: unknown object id {target!r}")
        if relation_type in RELATION_SIGNATURES:
            allowed_sources, allowed_targets = RELATION_SIGNATURES[relation_type]
            if object_types[source] not in allowed_sources:
                raise ValidationError(
                    f"{path}: {relation_type!r} cannot start from "
                    f"{object_types[source]!r}"
                )
            if object_types[target] not in allowed_targets:
                raise ValidationError(
                    f"{path}: {relation_type!r} cannot target "
                    f"{object_types[target]!r}"
                )

    for index, item in enumerate(evidence):
        path = f"inventory.evidence[{index}]"
        _require(item, "kind", str, path)
        _require(item, "source", str, path)
        _require(item, "summary", str, path)


def validate_pack(pack: Mapping[str, Any]) -> None:
    """Validate the stable core of a rule pack before evaluation."""

    version = _require(pack, "schema_version", str, "pack")
    if version != SCHEMA_VERSION:
        raise ValidationError(f"pack.schema_version: expected {SCHEMA_VERSION!r}, got {version!r}")
    metadata = _require(pack, "pack", dict, "pack")
    _require(metadata, "id", str, "pack.pack")
    _require(metadata, "name", str, "pack.pack")
    _require(metadata, "version", str, "pack.pack")
    authority_type = _require(metadata, "authority_type", str, "pack.pack")
    if authority_type not in AUTHORITY_TYPES:
        raise ValidationError(f"pack.pack.authority_type: unsupported value {authority_type!r}")
    _require(metadata, "jurisdiction", str, "pack.pack")
    _require(metadata, "reviewed_at", str, "pack.pack")
    _require(metadata, "coverage", list, "pack.pack")
    _require(metadata, "known_gaps", list, "pack.pack")
    applies_to = _require(metadata, "applies_to", list, "pack.pack")
    for object_type in applies_to:
        if object_type not in OBJECT_TYPES:
            raise ValidationError(f"pack.pack.applies_to: unsupported object type {object_type!r}")

    anchors = _require(pack, "anchors", list, "pack")
    rules = _require(pack, "rules", list, "pack")
    fact_catalog = pack.get("fact_catalog", [])
    inheritance = pack.get("inheritance", [])
    if not isinstance(fact_catalog, list):
        raise ValidationError("pack.fact_catalog: expected a list")
    if not isinstance(inheritance, list):
        raise ValidationError("pack.inheritance: expected a list")
    if not all(
        isinstance(item, Mapping)
        for item in anchors + rules + inheritance + fact_catalog
    ):
        raise ValidationError(
            "pack fact catalog, anchors, rules and inheritance items must be objects"
        )
    _unique(fact_catalog, "id", "pack.fact_catalog")
    _unique(anchors, "id", "pack.anchors")
    _unique(rules, "id", "pack.rules")
    _unique(inheritance, "id", "pack.inheritance")
    anchor_ids = {item["id"] for item in anchors}
    fact_ids = {item["id"] for item in fact_catalog}

    for index, fact in enumerate(fact_catalog):
        path = f"pack.fact_catalog[{index}]"
        fact_type = _require(fact, "type", str, path)
        if fact_type not in FACT_TYPES:
            raise ValidationError(f"{path}.type: unsupported value {fact_type!r}")
        _require(fact, "question", str, path)

    for index, anchor in enumerate(anchors):
        path = f"pack.anchors[{index}]"
        _require(anchor, "source", str, path)
        _require(anchor, "locator", str, path)
        _require(anchor, "url", str, path)
        _require(anchor, "summary", str, path)

    for index, rule in enumerate(rules):
        path = f"pack.rules[{index}]"
        _require(rule, "title", str, path)
        _require(rule, "kind", str, path)
        rule_types = _require(rule, "applies_to", list, path)
        if not rule_types:
            raise ValidationError(f"{path}.applies_to: at least one object type is required")
        for object_type in rule_types:
            if object_type not in OBJECT_TYPES:
                raise ValidationError(
                    f"{path}.applies_to: unsupported object type {object_type!r}"
                )
            if object_type not in applies_to:
                raise ValidationError(
                    f"{path}.applies_to: {object_type!r} is outside pack.pack.applies_to"
                )
        when = _require(rule, "when", dict, path)
        validate_condition(when, f"{path}.when")
        undeclared_facts = condition_fact_keys(when) - fact_ids
        if undeclared_facts:
            raise ValidationError(
                f"{path}.when: undeclared fact ids {sorted(undeclared_facts)!r}"
            )
        finding = _require(rule, "finding", dict, path)
        _require(finding, "code", str, f"{path}.finding")
        _require(finding, "level", str, f"{path}.finding")
        _require(finding, "title", str, f"{path}.finding")
        rule_anchors = _require(rule, "anchors", list, path)
        unknown_anchors = [item for item in rule_anchors if item not in anchor_ids]
        if unknown_anchors:
            raise ValidationError(f"{path}.anchors: unknown ids {unknown_anchors!r}")

    for index, policy in enumerate(inheritance):
        path = f"pack.inheritance[{index}]"
        fact_id = _require(policy, "fact", str, path)
        if fact_id not in fact_ids:
            raise ValidationError(f"{path}.fact: undeclared fact id {fact_id!r}")
        steps = _require(policy, "path", list, path)
        _validate_relation_path(steps, f"{path}.path")
        object_types = policy.get("object_types", [])
        if not isinstance(object_types, list):
            raise ValidationError(f"{path}.object_types: expected a list")
        for object_type in object_types:
            if object_type not in OBJECT_TYPES:
                raise ValidationError(
                    f"{path}.object_types: unsupported object type {object_type!r}"
                )


def validate_route_profile(profile: Mapping[str, Any]) -> None:
    """Validate optional organisation-owned routing configuration."""

    version = _require(profile, "schema_version", str, "route_profile")
    if version != SCHEMA_VERSION:
        raise ValidationError(
            f"route_profile.schema_version: expected {SCHEMA_VERSION!r}, got {version!r}"
        )
    metadata = _require(profile, "profile", dict, "route_profile")
    _require(metadata, "id", str, "route_profile.profile")
    _require(metadata, "version", str, "route_profile.profile")
    _require(metadata, "name", str, "route_profile.profile")
    routes = _require(profile, "routes", list, "route_profile")
    mappings = _require(profile, "mappings", list, "route_profile")
    if not all(isinstance(item, Mapping) for item in routes + mappings):
        raise ValidationError("route_profile routes and mappings must contain objects")
    _unique(routes, "id", "route_profile.routes")
    _unique(mappings, "id", "route_profile.mappings")
    route_ids = {item["id"] for item in routes}
    for index, route in enumerate(routes):
        path = f"route_profile.routes[{index}]"
        _require(route, "label", str, path)
        _require(route, "priority", int, path)
    for index, mapping in enumerate(mappings):
        path = f"route_profile.mappings[{index}]"
        route_id = _require(mapping, "route", str, path)
        if route_id not in route_ids:
            raise ValidationError(f"{path}.route: unknown route id {route_id!r}")
        match = _require(mapping, "match", dict, path)
        if not match:
            raise ValidationError(f"{path}.match: at least one selector is required")
        for selector, allowed in match.items():
            if selector not in ROUTE_SELECTORS:
                raise ValidationError(
                    f"{path}.match: unsupported selector {selector!r}"
                )
            if not isinstance(allowed, list) or not allowed:
                raise ValidationError(
                    f"{path}.match.{selector}: expected a non-empty list"
                )


def validate_pack_profile(profile: Mapping[str, Any]) -> None:
    """Validate an explicit, version-pinned selection of packs."""

    version = _require(profile, "schema_version", str, "pack_profile")
    if version != SCHEMA_VERSION:
        raise ValidationError(
            f"pack_profile.schema_version: expected {SCHEMA_VERSION!r}, got {version!r}"
        )
    metadata = _require(profile, "profile", dict, "pack_profile")
    _require(metadata, "id", str, "pack_profile.profile")
    _require(metadata, "version", str, "pack_profile.profile")
    _require(metadata, "name", str, "pack_profile.profile")
    packs = _require(profile, "packs", list, "pack_profile")
    if not packs:
        raise ValidationError("pack_profile.packs: at least one pinned pack is required")
    if not all(isinstance(item, Mapping) for item in packs):
        raise ValidationError("pack_profile.packs: every item must be an object")
    _unique(packs, "id", "pack_profile.packs")
    for index, item in enumerate(packs):
        path = f"pack_profile.packs[{index}]"
        _require(item, "version", str, path)
        _require(item, "path", str, path)
