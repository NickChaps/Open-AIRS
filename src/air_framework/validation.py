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
    "skill",
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
EXTRACTOR_KINDS = {"llm", "human", "hybrid"}
REVIEW_TYPES = {"mandatory", "targeted", "sample", "appeal", "change"}
REVIEW_STRATEGIES = {
    "rule_trigger",
    "low_confidence",
    "unknown_or_conflict",
    "change",
    "random",
    "stratified",
    "manual",
}
REVIEW_OUTCOMES = {"confirmed", "corrected", "inconclusive"}
REVIEW_DECISIONS = {"confirmed", "corrected", "disputed", "unresolved"}
REVIEW_SUBJECTS = {"fact", "finding", "analysis"}
ERROR_CATEGORIES = {
    "source",
    "composition",
    "extraction",
    "pack",
    "routing",
    "explanation",
}
REVIEW_ACTIONS = {
    "new_inventory_snapshot",
    "extractor_candidate",
    "pack_candidate",
    "route_candidate",
    "evidence_request",
    "no_change",
}
NOTE_RENDERER_KINDS = {"template", "llm", "hybrid", "human"}
NOTE_STATEMENT_KINDS = {"fact", "finding", "unknown", "route", "review"}
NOTE_REVIEW_STATUSES = {
    "not_selected",
    "selected",
    "confirmed",
    "corrected",
    "inconclusive",
}
RELATION_SIGNATURES = {
    "runs_on": (
        {"configured_ai_application", "ai_system"},
        {"ai_platform"},
    ),
    "loads_skill": (
        {"configured_ai_application", "ai_platform", "ai_system"},
        {"skill"},
    ),
    "can_invoke": (
        {"configured_ai_application", "ai_platform", "ai_system"},
        {"connector"},
    ),
    "offers_model": ({"ai_platform", "ai_system"}, {"model"}),
    "uses_model": (
        {"configured_ai_application", "ai_system"},
        {"model"},
    ),
    "implemented_by": (
        {"ai_use"},
        {"configured_ai_application", "ai_platform", "ai_system"},
    ),
    "operated_by": (
        {"ai_system", "ai_platform", "configured_ai_application", "ai_use", "service"},
        {"organization"},
    ),
    "provided_by": (
        {
            "ai_system",
            "ai_platform",
            "configured_ai_application",
            "skill",
            "connector",
            "model",
            "service",
        },
        {"provider"},
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
    if state in {"known", "conflicted"} and not fact.get("evidence"):
        raise ValidationError(
            f"{path}.evidence: at least one evidence identifier is required for state {state!r}"
        )
    if "confidence" in fact:
        confidence = fact["confidence"]
        if (
            not isinstance(confidence, (int, float))
            or isinstance(confidence, bool)
            or not 0 <= confidence <= 1
        ):
            raise ValidationError(f"{path}.confidence: expected a number from 0 to 1")
    if "extractor" in fact and not isinstance(fact["extractor"], Mapping):
        raise ValidationError(f"{path}.extractor: expected an object")


def fact_value_matches_type(value: Any, fact_type: str) -> bool:
    """Return whether a known value matches a pack-declared fact type."""

    if fact_type == "boolean":
        return isinstance(value, bool)
    if fact_type == "string":
        return isinstance(value, str)
    if fact_type == "array":
        return isinstance(value, list)
    if fact_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if fact_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if fact_type == "object":
        return isinstance(value, Mapping)
    return False


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
    _require(inventory, "captured_at", str, "inventory")
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
        object_evidence = item.get("evidence", [])
        if not isinstance(object_evidence, list) or not all(
            isinstance(evidence_id, str) for evidence_id in object_evidence
        ):
            raise ValidationError(
                f"{path}.evidence: expected a list of evidence identifiers"
            )
        if len(object_evidence) != len(set(object_evidence)):
            raise ValidationError(f"{path}.evidence: duplicate evidence id")
        for evidence_id in object_evidence:
            if evidence_id not in evidence_ids:
                raise ValidationError(
                    f"{path}.evidence: unknown evidence id {evidence_id!r}"
                )
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
        relation_evidence = item.get("evidence", [])
        if not isinstance(relation_evidence, list) or not all(
            isinstance(evidence_id, str) for evidence_id in relation_evidence
        ):
            raise ValidationError(f"{path}.evidence: expected a list of evidence identifiers")
        for evidence_id in relation_evidence:
            if evidence_id not in evidence_ids:
                raise ValidationError(
                    f"{path}.evidence: unknown evidence id {evidence_id!r}"
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
        _require(finding, "summary", str, f"{path}.finding")
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
        priority = _require(route, "priority", int, path)
        if isinstance(priority, bool):
            raise ValidationError(f"{path}.priority: expected int, got bool")
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


DECISION_INFLUENCE_LEVELS = {"none", "informative", "material", "determinative"}

EXCLUDED_MENTION_CLASSES = {
    "prohibited_by_instructions",
    "guardrail",
    "example_reference",
    "capability_only",
}


def validate_taxonomy(taxonomy: Mapping[str, Any]) -> None:
    """Validate a versioned purpose taxonomy artefact."""

    version = _require(taxonomy, "schema_version", str, "taxonomy")
    if version != SCHEMA_VERSION:
        raise ValidationError(
            f"taxonomy.schema_version: expected {SCHEMA_VERSION!r}, got {version!r}"
        )
    metadata = _require(taxonomy, "taxonomy", dict, "taxonomy")
    _require(metadata, "id", str, "taxonomy.taxonomy")
    _require(metadata, "version", str, "taxonomy.taxonomy")
    _require(metadata, "reviewed_at", str, "taxonomy.taxonomy")
    tags = _require(taxonomy, "tags", list, "taxonomy")
    if not tags or not all(isinstance(item, Mapping) for item in tags):
        raise ValidationError("taxonomy.tags: expected non-empty tag objects")
    _unique(tags, "id", "taxonomy.tags")
    for index, tag in enumerate(tags):
        path = f"taxonomy.tags[{index}]"
        _require(tag, "id", str, path)
        _require(tag, "label", str, path)
        _require(tag, "definition", str, path)


def _validate_purpose_blocks(
    record: Mapping[str, Any],
    known_evidence: set[str],
    extractor_kind: str,
    taxonomy: Mapping[str, Any] | None,
) -> None:
    proposed_uses = record.get("proposed_uses", [])
    excluded = record.get("excluded_mentions", [])
    if not isinstance(proposed_uses, list) or not all(
        isinstance(item, Mapping) for item in proposed_uses
    ):
        raise ValidationError("extraction.proposed_uses: expected use objects")
    if not isinstance(excluded, list) or not all(
        isinstance(item, Mapping) for item in excluded
    ):
        raise ValidationError("extraction.excluded_mentions: expected mention objects")

    if proposed_uses:
        pin = record.get("taxonomy")
        if not isinstance(pin, Mapping):
            raise ValidationError(
                "extraction.taxonomy: a taxonomy pin is required when uses are proposed"
            )
        _require(pin, "id", str, "extraction.taxonomy")
        _require(pin, "version", str, "extraction.taxonomy")

    allowed_tags: set[str] | None = None
    if taxonomy is not None:
        validate_taxonomy(taxonomy)
        pin = record.get("taxonomy")
        if isinstance(pin, Mapping):
            metadata = taxonomy["taxonomy"]
            if pin.get("id") != metadata["id"] or pin.get("version") != metadata["version"]:
                raise ValidationError(
                    "extraction.taxonomy: pinned taxonomy does not match the supplied taxonomy"
                )
        allowed_tags = {tag["id"] for tag in taxonomy["tags"]}

    for index, use in enumerate(proposed_uses):
        path = f"extraction.proposed_uses[{index}]"
        _require(use, "purpose_statement", str, path)
        tags = _require(use, "purpose_tags", list, path)
        if not tags or not all(isinstance(item, str) and item for item in tags):
            raise ValidationError(f"{path}.purpose_tags: expected non-empty tag ids")
        if allowed_tags is not None:
            unknown_tags = set(tags) - allowed_tags
            if unknown_tags:
                raise ValidationError(
                    f"{path}.purpose_tags: unknown tags {sorted(unknown_tags)!r}"
                )
        for field in ("material_tasks", "affected_people", "alternative_interpretations"):
            values = use.get(field, [])
            if not isinstance(values, list) or not all(
                isinstance(item, str) and item for item in values
            ):
                raise ValidationError(f"{path}.{field}: expected a list of strings")
        influence = use.get("decision_influence")
        if influence is not None and influence not in DECISION_INFLUENCE_LEVELS:
            raise ValidationError(
                f"{path}.decision_influence: unsupported value {influence!r}"
            )
        evidence = _require(use, "evidence", list, path)
        if not evidence:
            raise ValidationError(f"{path}.evidence: at least one evidence id is required")
        unknown_evidence = set(evidence) - known_evidence
        if unknown_evidence:
            raise ValidationError(
                f"{path}.evidence: ids absent from source_evidence {sorted(unknown_evidence)!r}"
            )
        if extractor_kind in {"llm", "hybrid"} and "confidence" not in use:
            raise ValidationError(f"{path}.confidence: required for LLM or hybrid extraction")

    for index, mention in enumerate(excluded):
        path = f"extraction.excluded_mentions[{index}]"
        _require(mention, "candidate_use", str, path)
        classification = _require(mention, "classification", str, path)
        if classification not in EXCLUDED_MENTION_CLASSES:
            raise ValidationError(
                f"{path}.classification: unsupported value {classification!r}"
            )
        evidence = _require(mention, "evidence", list, path)
        if not evidence:
            raise ValidationError(f"{path}.evidence: at least one evidence id is required")
        unknown_evidence = set(evidence) - known_evidence
        if unknown_evidence:
            raise ValidationError(
                f"{path}.evidence: ids absent from source_evidence {sorted(unknown_evidence)!r}"
            )


def validate_extraction_record(
    record: Mapping[str, Any], taxonomy: Mapping[str, Any] | None = None
) -> None:
    """Validate a model or human extraction record kept outside the assessment."""

    version = _require(record, "schema_version", str, "extraction")
    if version != SCHEMA_VERSION:
        raise ValidationError(
            f"extraction.schema_version: expected {SCHEMA_VERSION!r}, got {version!r}"
        )
    _require(record, "extraction_id", str, "extraction")
    _require(record, "created_at", str, "extraction")

    target = _require(record, "target", dict, "extraction")
    _require(target, "id", str, "extraction.target")
    target_type = _require(target, "type", str, "extraction.target")
    if target_type not in OBJECT_TYPES:
        raise ValidationError(
            f"extraction.target.type: unsupported object type {target_type!r}"
        )

    inventory = _require(record, "inventory", dict, "extraction")
    _require(inventory, "inventory_id", str, "extraction.inventory")
    _require(inventory, "snapshot_id", str, "extraction.inventory")

    pack_inputs = _require(record, "pack_inputs", list, "extraction")
    if not pack_inputs or not all(isinstance(item, Mapping) for item in pack_inputs):
        raise ValidationError("extraction.pack_inputs: expected non-empty pack pins")
    _unique(pack_inputs, "id", "extraction.pack_inputs")
    for index, pin in enumerate(pack_inputs):
        path = f"extraction.pack_inputs[{index}]"
        _require(pin, "version", str, path)
        digest = _require(pin, "content_hash", str, path)
        if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
            raise ValidationError(f"{path}.content_hash: expected a lower-case SHA-256 digest")

    extractor = _require(record, "extractor", dict, "extraction")
    extractor_kind = _require(extractor, "kind", str, "extraction.extractor")
    if extractor_kind not in EXTRACTOR_KINDS:
        raise ValidationError(
            f"extraction.extractor.kind: unsupported value {extractor_kind!r}"
        )
    skill = _require(extractor, "skill", dict, "extraction.extractor")
    _require(skill, "id", str, "extraction.extractor.skill")
    _require(skill, "version", str, "extraction.extractor.skill")

    source_evidence = _require(record, "source_evidence", list, "extraction")
    if not source_evidence or not all(isinstance(item, str) for item in source_evidence):
        raise ValidationError(
            "extraction.source_evidence: expected a non-empty list of evidence ids"
        )
    if len(source_evidence) != len(set(source_evidence)):
        raise ValidationError("extraction.source_evidence: duplicate evidence id")
    known_evidence = set(source_evidence)

    proposals = _require(record, "fact_proposals", list, "extraction")
    if not proposals or not all(isinstance(item, Mapping) for item in proposals):
        raise ValidationError("extraction.fact_proposals: expected non-empty objects")
    _unique(proposals, "fact_id", "extraction.fact_proposals")
    proposal_ids = {item["fact_id"] for item in proposals}
    for index, proposal in enumerate(proposals):
        path = f"extraction.fact_proposals[{index}]"
        validate_fact(proposal, path)
        if extractor_kind in {"llm", "hybrid"} and "confidence" not in proposal:
            raise ValidationError(
                f"{path}.confidence: required for LLM or hybrid extraction"
            )
        _require(proposal, "rationale", str, path)
        unknown_evidence = set(proposal.get("evidence", [])) - known_evidence
        if unknown_evidence:
            raise ValidationError(
                f"{path}.evidence: ids absent from source_evidence {sorted(unknown_evidence)!r}"
            )

    _validate_purpose_blocks(record, known_evidence, extractor_kind, taxonomy)

    analysis = _require(record, "analysis", dict, "extraction")
    _require(analysis, "summary", str, "extraction.analysis")
    _require(analysis, "scope", str, "extraction.analysis")
    observations = _require(analysis, "observations", list, "extraction.analysis")
    unknowns = _require(analysis, "unknowns", list, "extraction.analysis")
    if not all(isinstance(item, str) for item in unknowns):
        raise ValidationError("extraction.analysis.unknowns: expected strings")
    cautions = analysis.get("cautions", [])
    if not isinstance(cautions, list) or not all(isinstance(item, str) for item in cautions):
        raise ValidationError("extraction.analysis.cautions: expected strings")
    if not observations or not all(isinstance(item, Mapping) for item in observations):
        raise ValidationError("extraction.analysis.observations: expected non-empty objects")
    for index, observation in enumerate(observations):
        path = f"extraction.analysis.observations[{index}]"
        _require(observation, "statement", str, path)
        fact_ids = _require(observation, "fact_ids", list, path)
        evidence_ids = _require(observation, "evidence", list, path)
        if not all(isinstance(item, str) for item in fact_ids + evidence_ids):
            raise ValidationError(f"{path}: fact_ids and evidence must contain strings")
        unknown_facts = set(fact_ids) - proposal_ids
        unknown_evidence = set(evidence_ids) - known_evidence
        if unknown_facts:
            raise ValidationError(
                f"{path}.fact_ids: unknown proposals {sorted(unknown_facts)!r}"
            )
        if unknown_evidence:
            raise ValidationError(
                f"{path}.evidence: unknown evidence ids {sorted(unknown_evidence)!r}"
            )


def validate_review_record(record: Mapping[str, Any]) -> None:
    """Validate an immutable human review, including sampled quality control."""

    version = _require(record, "schema_version", str, "review")
    if version != SCHEMA_VERSION:
        raise ValidationError(
            f"review.schema_version: expected {SCHEMA_VERSION!r}, got {version!r}"
        )
    _require(record, "review_id", str, "review")
    _require(record, "reviewed_at", str, "review")
    _require(record, "assessment_id", str, "review")

    target = _require(record, "target", dict, "review")
    _require(target, "id", str, "review.target")
    target_type = _require(target, "type", str, "review.target")
    if target_type not in OBJECT_TYPES:
        raise ValidationError(f"review.target.type: unsupported value {target_type!r}")

    review_type = _require(record, "review_type", str, "review")
    if review_type not in REVIEW_TYPES:
        raise ValidationError(f"review.review_type: unsupported value {review_type!r}")
    selection = _require(record, "selection", dict, "review")
    strategy = _require(selection, "strategy", str, "review.selection")
    if strategy not in REVIEW_STRATEGIES:
        raise ValidationError(f"review.selection.strategy: unsupported value {strategy!r}")
    _require(selection, "reason", str, "review.selection")
    reviewer = _require(record, "reviewer", dict, "review")
    _require(reviewer, "role", str, "review.reviewer")

    outcome = _require(record, "outcome", str, "review")
    if outcome not in REVIEW_OUTCOMES:
        raise ValidationError(f"review.outcome: unsupported value {outcome!r}")

    adjudications = _require(record, "adjudications", list, "review")
    if not adjudications or not all(
        isinstance(item, Mapping) for item in adjudications
    ):
        raise ValidationError("review.adjudications: expected non-empty objects")
    corrected = False
    decisions: list[str] = []
    for index, item in enumerate(adjudications):
        path = f"review.adjudications[{index}]"
        subject_type = _require(item, "subject_type", str, path)
        if subject_type not in REVIEW_SUBJECTS:
            raise ValidationError(f"{path}.subject_type: unsupported value {subject_type!r}")
        _require(item, "subject_id", str, path)
        decision = _require(item, "decision", str, path)
        if decision not in REVIEW_DECISIONS:
            raise ValidationError(f"{path}.decision: unsupported value {decision!r}")
        decisions.append(decision)
        corrected = corrected or decision == "corrected"
        _require(item, "rationale", str, path)
        evidence = item.get("evidence", [])
        if not isinstance(evidence, list) or not all(isinstance(value, str) for value in evidence):
            raise ValidationError(f"{path}.evidence: expected strings")

    categories = _require(record, "error_categories", list, "review")
    if len(categories) != len(set(categories)):
        raise ValidationError("review.error_categories: duplicate value")
    for category in categories:
        if category not in ERROR_CATEGORIES:
            raise ValidationError(
                f"review.error_categories: unsupported value {category!r}"
            )

    actions = _require(record, "actions", list, "review")
    if not actions or not all(isinstance(item, Mapping) for item in actions):
        raise ValidationError("review.actions: expected non-empty objects")
    action_types = []
    for index, action in enumerate(actions):
        path = f"review.actions[{index}]"
        action_type = _require(action, "type", str, path)
        if action_type not in REVIEW_ACTIONS:
            raise ValidationError(f"{path}.type: unsupported value {action_type!r}")
        action_types.append(action_type)

    if "no_change" in action_types and len(action_types) != 1:
        raise ValidationError(
            "review.actions: no_change cannot be combined with another action"
        )
    if outcome == "confirmed" and any(
        decision != "confirmed" for decision in decisions
    ):
        raise ValidationError(
            "review.outcome: confirmed requires every adjudication to be confirmed"
        )
    if outcome == "inconclusive" and not set(decisions).intersection(
        {"disputed", "unresolved"}
    ):
        raise ValidationError(
            "review.outcome: inconclusive requires a disputed or unresolved subject"
        )
    if outcome != "corrected" and corrected:
        raise ValidationError(
            "review.outcome: a corrected subject requires a corrected outcome"
        )

    if outcome == "corrected" and not corrected:
        raise ValidationError(
            "review.adjudications: a corrected outcome requires a corrected subject"
        )
    if outcome == "corrected" and not set(action_types).intersection(
        {"new_inventory_snapshot", "extractor_candidate", "pack_candidate", "route_candidate"}
    ):
        raise ValidationError(
            "review.actions: a corrected outcome requires a versioned corrective action"
        )
    if outcome == "corrected" and not categories:
        raise ValidationError(
            "review.error_categories: a corrected outcome requires an error category"
        )


def validate_assessment_note(record: Mapping[str, Any]) -> None:
    """Validate readable prose whose material claims resolve to structured records."""

    version = _require(record, "schema_version", str, "assessment_note")
    if version != SCHEMA_VERSION:
        raise ValidationError(
            "assessment_note.schema_version: "
            f"expected {SCHEMA_VERSION!r}, got {version!r}"
        )
    _require(record, "note_id", str, "assessment_note")
    _require(record, "created_at", str, "assessment_note")
    _require(record, "language", str, "assessment_note")

    target = _require(record, "target", dict, "assessment_note")
    _require(target, "id", str, "assessment_note.target")
    target_type = _require(target, "type", str, "assessment_note.target")
    if target_type not in OBJECT_TYPES:
        raise ValidationError(
            f"assessment_note.target.type: unsupported value {target_type!r}"
        )

    inputs = _require(record, "inputs", dict, "assessment_note")
    inventory = _require(inputs, "inventory", dict, "assessment_note.inputs")
    _require(inventory, "inventory_id", str, "assessment_note.inputs.inventory")
    _require(inventory, "snapshot_id", str, "assessment_note.inputs.inventory")
    extraction_ids = _require(
        inputs, "extraction_ids", list, "assessment_note.inputs"
    )
    assessment_ids = _require(
        inputs, "assessment_ids", list, "assessment_note.inputs"
    )
    if not all(isinstance(item, str) for item in extraction_ids):
        raise ValidationError(
            "assessment_note.inputs.extraction_ids: expected strings"
        )
    if len(extraction_ids) != len(set(extraction_ids)):
        raise ValidationError(
            "assessment_note.inputs.extraction_ids: duplicate identifier"
        )
    if not assessment_ids or not all(
        isinstance(item, str) for item in assessment_ids
    ):
        raise ValidationError(
            "assessment_note.inputs.assessment_ids: expected non-empty strings"
        )
    if len(assessment_ids) != len(set(assessment_ids)):
        raise ValidationError(
            "assessment_note.inputs.assessment_ids: duplicate identifier"
        )
    route_result_ids = inputs.get("route_result_ids", [])
    if not isinstance(route_result_ids, list) or not all(
        isinstance(item, str) for item in route_result_ids
    ):
        raise ValidationError(
            "assessment_note.inputs.route_result_ids: expected strings"
        )
    known_routes = set(route_result_ids)

    renderer = _require(record, "renderer", dict, "assessment_note")
    renderer_kind = _require(renderer, "kind", str, "assessment_note.renderer")
    if renderer_kind not in NOTE_RENDERER_KINDS:
        raise ValidationError(
            f"assessment_note.renderer.kind: unsupported value {renderer_kind!r}"
        )
    _require(renderer, "id", str, "assessment_note.renderer")
    _require(renderer, "version", str, "assessment_note.renderer")

    _require(record, "summary", str, "assessment_note")
    _require(record, "scope", str, "assessment_note")
    statements = _require(record, "statements", list, "assessment_note")
    if not statements or not all(isinstance(item, Mapping) for item in statements):
        raise ValidationError("assessment_note.statements: expected non-empty objects")
    _unique(statements, "statement_id", "assessment_note.statements")
    known_assessments = set(assessment_ids)
    for index, statement in enumerate(statements):
        path = f"assessment_note.statements[{index}]"
        kind = _require(statement, "kind", str, path)
        if kind not in NOTE_STATEMENT_KINDS:
            raise ValidationError(f"{path}.kind: unsupported value {kind!r}")
        _require(statement, "text", str, path)
        references = _require(statement, "references", dict, path)
        allowed_references = {
            "fact_ids",
            "evidence",
            "assessment_id",
            "rule_ids",
            "anchor_ids",
            "route_result_id",
            "route_ids",
            "review_id",
        }
        unknown_references = set(references) - allowed_references
        if unknown_references:
            raise ValidationError(
                f"{path}.references: unsupported fields {sorted(unknown_references)!r}"
            )
        for key in {"fact_ids", "evidence", "rule_ids", "anchor_ids", "route_ids"}:
            values = references.get(key, [])
            if not isinstance(values, list) or not all(
                isinstance(value, str) for value in values
            ):
                raise ValidationError(f"{path}.references.{key}: expected strings")
        assessment_id = references.get("assessment_id")
        if assessment_id is not None:
            if not isinstance(assessment_id, str):
                raise ValidationError(
                    f"{path}.references.assessment_id: expected a string"
                )
            if assessment_id not in known_assessments:
                raise ValidationError(
                    f"{path}.references.assessment_id: absent from note inputs"
                )
        if kind == "fact" and not (
            references.get("fact_ids") and references.get("evidence")
        ):
            raise ValidationError(
                f"{path}.references: fact statements require fact_ids and evidence"
            )
        if kind == "finding" and not (
            assessment_id
            and references.get("rule_ids")
            and references.get("anchor_ids")
        ):
            raise ValidationError(
                f"{path}.references: findings require assessment_id, rule_ids and anchor_ids"
            )
        if kind == "unknown" and not (
            references.get("fact_ids") or assessment_id
        ):
            raise ValidationError(
                f"{path}.references: unknowns require fact_ids or assessment_id"
            )
        if kind == "route" and not (
            isinstance(references.get("route_result_id"), str)
            and references.get("route_ids")
        ):
            raise ValidationError(
                f"{path}.references: route statements require route_result_id and route_ids"
            )
        if kind == "route" and references.get("route_result_id") not in known_routes:
            raise ValidationError(
                f"{path}.references.route_result_id: absent from note inputs"
            )
        if kind == "review" and not isinstance(references.get("review_id"), str):
            raise ValidationError(
                f"{path}.references: review statements require review_id"
            )

    cautions = record.get("cautions", [])
    if not isinstance(cautions, list) or not all(
        isinstance(item, str) for item in cautions
    ):
        raise ValidationError("assessment_note.cautions: expected strings")

    review_status = _require(record, "review_status", dict, "assessment_note")
    status = _require(review_status, "status", str, "assessment_note.review_status")
    if status not in NOTE_REVIEW_STATUSES:
        raise ValidationError(
            f"assessment_note.review_status.status: unsupported value {status!r}"
        )
    review_id = review_status.get("review_id")
    if status != "not_selected" and not isinstance(review_id, str):
        raise ValidationError(
            "assessment_note.review_status.review_id: required when review was selected"
        )
    if status == "not_selected" and review_id is not None:
        raise ValidationError(
            "assessment_note.review_status.review_id: forbidden when no review was selected"
        )
    statement_review_ids = {
        item["references"].get("review_id")
        for item in statements
        if item["kind"] == "review"
    }
    if review_id is not None and statement_review_ids and statement_review_ids != {
        review_id
    }:
        raise ValidationError(
            "assessment_note.statements: review references must match review_status"
        )
