# SPDX-License-Identifier: Apache-2.0
"""Optional LLM orchestration around the deterministic AIR engine.

The model reads source material, proposes bounded facts and writes an
evidence-linked explanation.  The rule engine remains a separate pure step:
no model response may create a rule, legal anchor or obligation.
"""

from __future__ import annotations

import json
import os
import socket
import time
import urllib.error
import urllib.request
import uuid
from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib.resources import files
from pathlib import Path
from typing import Any, Protocol

from .canonical import content_hash
from .errors import LlmError, ValidationError
from .profiles import assess_profile, verify_profile_packs
from .validation import (
    fact_value_matches_type,
    validate_assessment_note,
    validate_extraction_record,
    validate_inventory,
    validate_pack,
    validate_pack_profile,
    validate_taxonomy,
)
from .version import __version__


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _prompt_template(name: str) -> str:
    return files("air_framework.prompts").joinpath(name).read_text(encoding="utf-8").strip()


@dataclass(frozen=True)
class JsonCompletion:
    """Parsed JSON plus the provider metadata needed for an audit record."""

    value: dict[str, Any]
    response_id: str | None = None
    model: str | None = None
    usage: Mapping[str, Any] | None = None


class JsonCompletionClient(Protocol):
    """Small provider boundary used by the pipeline and by test doubles."""

    provider_name: str
    model: str

    def complete_json(
        self,
        *,
        system: str,
        user: str,
        schema_name: str,
        schema: Mapping[str, Any],
    ) -> JsonCompletion: ...


class OpenAICompatibleClient:
    """Dependency-free Chat Completions client with structured JSON output."""

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str = "https://api.openai.com/v1",
        provider_name: str = "openai-compatible",
        response_format: str = "json_schema",
        reasoning_effort: str | None = None,
        max_tokens: int = 5000,
        timeout: float = 120.0,
        retries: int = 3,
    ) -> None:
        if not api_key.strip():
            raise LlmError("The model API key is empty.")
        if not model.strip():
            raise LlmError("The model id is empty.")
        if not base_url.strip():
            raise LlmError("The model base URL is empty.")
        if response_format not in {"json_schema", "json_object"}:
            raise LlmError("response_format must be 'json_schema' or 'json_object'.")
        if max_tokens < 1:
            raise LlmError("max_tokens must be greater than zero.")
        if timeout <= 0:
            raise LlmError("timeout must be greater than zero.")
        if retries < 0:
            raise LlmError("retries cannot be negative.")
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.provider_name = provider_name
        self.response_format = response_format
        self.reasoning_effort = reasoning_effort
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.retries = retries

    def complete_json(
        self,
        *,
        system: str,
        user: str,
        schema_name: str,
        schema: Mapping[str, Any],
    ) -> JsonCompletion:
        response_format: dict[str, Any]
        if self.response_format == "json_schema":
            response_format = {
                "type": "json_schema",
                "json_schema": {
                    "name": schema_name,
                    "strict": False,
                    "schema": schema,
                },
            }
        else:
            response_format = {"type": "json_object"}

        body: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "response_format": response_format,
            "max_tokens": self.max_tokens,
        }
        if self.reasoning_effort:
            body["reasoning_effort"] = self.reasoning_effort

        url = f"{self.base_url}/chat/completions"
        request = urllib.request.Request(
            url,
            data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
            method="POST",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "User-Agent": f"AIR-Framework/{__version__}",
            },
        )
        raw_response: dict[str, Any] | None = None
        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    raw_response = json.loads(response.read().decode("utf-8"))
                break
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")[:800]
                last_error = LlmError(f"Model endpoint returned HTTP {exc.code}: {detail}")
                if exc.code != 429 and exc.code < 500:
                    break
            except (urllib.error.URLError, TimeoutError, socket.timeout, json.JSONDecodeError) as exc:
                last_error = exc
            if attempt < self.retries:
                time.sleep(min(2**attempt, 8))

        if raw_response is None:
            raise LlmError(f"Model request failed: {last_error}")
        choices = raw_response.get("choices")
        if not isinstance(choices, list) or not choices:
            raise LlmError("Model response contains no completion choice.")
        if choices[0].get("finish_reason") == "length":
            raise LlmError("Model response was truncated by the completion limit.")
        message = choices[0].get("message", {})
        content = message.get("content")
        if not isinstance(content, str):
            raise LlmError("Model response contains no textual JSON content.")
        try:
            value = json.loads(content)
        except json.JSONDecodeError as exc:
            raise LlmError(
                f"Model response is not valid JSON at line {exc.lineno}, column {exc.colno}."
            ) from exc
        if not isinstance(value, dict):
            raise LlmError("Model response must be a JSON object.")
        return JsonCompletion(
            value=value,
            response_id=raw_response.get("id"),
            model=raw_response.get("model") or self.model,
            usage=raw_response.get("usage"),
        )


EXTRACTION_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["fact_proposals", "analysis"],
    "properties": {
        "fact_proposals": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["fact_id", "state", "evidence", "confidence", "rationale"],
                "properties": {
                    "fact_id": {"type": "string"},
                    "state": {
                        "enum": ["known", "unknown", "conflicted", "not_applicable"]
                    },
                    "value": {},
                    "evidence": {"type": "array", "items": {"type": "string"}},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "rationale": {"type": "string"},
                },
                "additionalProperties": False,
            },
        },
        "analysis": {
            "type": "object",
            "required": ["summary", "scope", "observations", "unknowns", "cautions"],
            "properties": {
                "summary": {"type": "string"},
                "scope": {"type": "string"},
                "observations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["statement", "fact_ids", "evidence"],
                        "properties": {
                            "statement": {"type": "string"},
                            "fact_ids": {"type": "array", "items": {"type": "string"}},
                            "evidence": {"type": "array", "items": {"type": "string"}},
                        },
                        "additionalProperties": False,
                    },
                },
                "unknowns": {"type": "array", "items": {"type": "string"}},
                "cautions": {"type": "array", "items": {"type": "string"}},
            },
            "additionalProperties": False,
        },
        "proposed_uses": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "purpose_statement",
                    "purpose_tags",
                    "evidence",
                    "confidence",
                ],
                "properties": {
                    "purpose_statement": {"type": "string"},
                    "purpose_tags": {"type": "array", "items": {"type": "string"}},
                    "material_tasks": {"type": "array", "items": {"type": "string"}},
                    "affected_people": {"type": "array", "items": {"type": "string"}},
                    "decision_influence": {
                        "enum": ["none", "informative", "material", "determinative"]
                    },
                    "evidence": {"type": "array", "items": {"type": "string"}},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "alternative_interpretations": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "rationale": {"type": "string"},
                },
                "additionalProperties": False,
            },
        },
        "excluded_mentions": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["candidate_use", "classification", "evidence"],
                "properties": {
                    "candidate_use": {"type": "string"},
                    "classification": {
                        "enum": [
                            "prohibited_by_instructions",
                            "guardrail",
                            "example_reference",
                            "capability_only",
                        ]
                    },
                    "evidence": {"type": "array", "items": {"type": "string"}},
                    "note": {"type": "string"},
                },
                "additionalProperties": False,
            },
        },
    },
    "additionalProperties": False,
}


NOTE_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "required": ["summary", "scope", "statements", "cautions"],
    "properties": {
        "summary": {"type": "string"},
        "scope": {"type": "string"},
        "statements": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["statement_id", "kind", "text", "references"],
                "properties": {
                    "statement_id": {"type": "string"},
                    "kind": {"enum": ["fact", "finding", "unknown"]},
                    "text": {"type": "string"},
                    "references": {
                        "type": "object",
                        "properties": {
                            "fact_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "evidence": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "assessment_id": {"type": "string"},
                            "rule_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                            "anchor_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                        "additionalProperties": False,
                    },
                },
                "additionalProperties": False,
            },
        },
        "cautions": {"type": "array", "items": {"type": "string"}},
    },
    "additionalProperties": False,
}


def _walk_fact_values(condition: Any, output: dict[str, list[Any]]) -> None:
    if not isinstance(condition, Mapping):
        return
    fact = condition.get("fact")
    if isinstance(fact, Mapping) and isinstance(fact.get("key"), str):
        key = fact["key"]
        if "value" in fact:
            raw = fact["value"]
            values = raw if isinstance(raw, list) else [raw]
            bucket = output.setdefault(key, [])
            for value in values:
                if value not in bucket:
                    bucket.append(value)
    for operator in ("all", "any"):
        children = condition.get(operator)
        if isinstance(children, list):
            for child in children:
                _walk_fact_values(child, output)
    if "not" in condition:
        _walk_fact_values(condition["not"], output)
    related = condition.get("related")
    if isinstance(related, Mapping):
        _walk_fact_values(related.get("where"), output)


def _fact_catalogue(
    packs: Sequence[Mapping[str, Any]], target_type: str
) -> list[dict[str, Any]]:
    values: dict[str, list[Any]] = {}
    for pack in packs:
        for rule in pack.get("rules", []):
            if target_type in rule.get("applies_to", pack["pack"]["applies_to"]):
                _walk_fact_values(rule.get("when"), values)

    catalogue: dict[str, dict[str, Any]] = {}
    for pack in packs:
        if target_type not in pack["pack"]["applies_to"]:
            continue
        pack_id = pack["pack"]["id"]
        for fact in pack.get("fact_catalog", []):
            existing = catalogue.get(fact["id"])
            if existing is not None and existing["type"] != fact["type"]:
                raise ValidationError(
                    f"Selected packs declare incompatible types for fact {fact['id']!r}."
                )
            item = catalogue.setdefault(
                fact["id"],
                {
                    "id": fact["id"],
                    "type": fact["type"],
                    "question": fact["question"],
                    "packs": [],
                },
            )
            if pack_id not in item["packs"]:
                item["packs"].append(pack_id)
            if values.get(fact["id"]):
                item["values_used_by_rules"] = values[fact["id"]]
    return list(catalogue.values())


def _context(inventory: Mapping[str, Any], target_id: str, depth: int = 3) -> dict[str, Any]:
    """Select the target's directed composition without pulling in platform siblings."""

    objects = {item["id"]: item for item in inventory["objects"]}
    if target_id not in objects:
        raise ValidationError(f"Unknown target object {target_id!r}")
    selected = {target_id}
    frontier = {target_id}
    selected_relations: set[str] = set()
    for _ in range(depth):
        next_frontier: set[str] = set()
        for relation in inventory["relations"]:
            if relation["source"] in frontier:
                selected_relations.add(relation["id"])
                next_frontier.add(relation["target"])
        next_frontier -= selected
        selected |= next_frontier
        frontier = next_frontier
        if not frontier:
            break
    context_objects = [item for item in inventory["objects"] if item["id"] in selected]
    context_relations = [
        item
        for item in inventory["relations"]
        if item["id"] in selected_relations
    ]
    evidence_ids = {
        evidence_id
        for item in context_objects
        for evidence_id in item.get("evidence", [])
    }
    evidence_ids.update(
        evidence_id
        for item in context_objects
        for fact in item.get("facts", {}).values()
        if isinstance(fact, Mapping)
        for evidence_id in fact.get("evidence", [])
    )
    evidence_ids.update(
        evidence_id
        for relation in context_relations
        for evidence_id in relation.get("evidence", [])
    )
    context_evidence = [
        item for item in inventory["evidence"] if item["id"] in evidence_ids
    ]
    return {
        "objects": context_objects,
        "relations": context_relations,
        "evidence": context_evidence,
    }


def _pack_inputs(packs: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    return [
        {
            "id": pack["pack"]["id"],
            "version": pack["pack"]["version"],
            "content_hash": content_hash(pack),
        }
        for pack in packs
    ]


def _anchor_context(packs: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "pack_id": pack["pack"]["id"],
            "anchors": [
                {
                    "id": anchor["id"],
                    "source": anchor.get("source"),
                    "locator": anchor.get("locator"),
                    "summary": anchor.get("summary"),
                }
                for anchor in pack.get("anchors", [])
            ],
        }
        for pack in packs
    ]


def _extraction_prompt(
    inventory: Mapping[str, Any],
    packs: Sequence[Mapping[str, Any]],
    target_id: str,
    *,
    language: str,
    taxonomy: Mapping[str, Any] | None = None,
) -> tuple[str, str, dict[str, Any]]:
    target = next(item for item in inventory["objects"] if item["id"] == target_id)
    context = _context(inventory, target_id)
    if not context["evidence"]:
        raise ValidationError(
            "The target composition contains no linked evidence for model extraction."
        )
    catalogue = _fact_catalogue(packs, target["type"])
    if not catalogue:
        raise ValidationError(
            f"No selected pack supplies facts for target type {target['type']!r}."
        )
    payload = {
        "language": language,
        "target": target,
        "composition": context,
        "allowed_fact_catalogue": catalogue,
        "legal_or_method_anchors": _anchor_context(packs),
    }
    if taxonomy is not None:
        payload["purpose_taxonomy"] = {
            "id": taxonomy["taxonomy"]["id"],
            "version": taxonomy["taxonomy"]["version"],
            "tags": [
                {"id": tag["id"], "label": tag["label"], "definition": tag["definition"]}
                for tag in taxonomy["tags"]
            ],
        }
    system = _prompt_template("extraction-system.txt")
    user = (
        "Prepare the bounded fact proposals and source analysis in "
        f"{language}. Facts may include controlled legal characterisations expressly "
        "requested by the catalogue, but their evidence and confidence must remain "
        "visible. Repeat an existing fact only when the analysis needs to cite it; "
        "keep the same value unless the supplied evidence conflicts.\n\n"
        + json.dumps(payload, ensure_ascii=False, sort_keys=True)
    )
    return system, user, payload


def extract_with_llm(
    inventory: Mapping[str, Any],
    packs: Sequence[Mapping[str, Any]],
    target_id: str,
    client: JsonCompletionClient,
    *,
    language: str = "fr",
    created_at: str | None = None,
    taxonomy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Call the semantic judge and return a validated extraction record."""

    validate_inventory(inventory)
    for pack in packs:
        validate_pack(pack)
    if taxonomy is not None:
        validate_taxonomy(taxonomy)
    system, user, payload = _extraction_prompt(
        inventory, packs, target_id, language=language, taxonomy=taxonomy
    )
    completion = client.complete_json(
        system=system,
        user=user,
        schema_name="air_fact_extraction",
        schema=EXTRACTION_RESPONSE_SCHEMA,
    )
    target = next(item for item in inventory["objects"] if item["id"] == target_id)
    source_evidence = [item["id"] for item in payload["composition"]["evidence"]]
    extractor = {
        "kind": "llm",
        "skill": {"id": "air-assess", "version": "0.3.0"},
        "model": {
            "provider": client.provider_name,
            "id": completion.model or client.model,
        },
        "prompt_hash": content_hash({"system": system, "user": user}),
        "prompt_template": {
            "id": "air-assess/extraction",
            "version": "0.3.0",
            "content_hash": content_hash(system),
        },
        "run_id": completion.response_id or f"local-{uuid.uuid4()}",
    }
    if completion.usage is not None:
        extractor["usage"] = dict(completion.usage)
    record = {
        "schema_version": "0.1.0",
        "extraction_id": f"urn:air:extraction:{uuid.uuid4()}",
        "created_at": created_at or _utc_now(),
        "target": {"id": target["id"], "type": target["type"], "name": target["name"]},
        "inventory": {
            "inventory_id": inventory["inventory_id"],
            "snapshot_id": inventory["snapshot_id"],
            "content_hash": content_hash(inventory),
        },
        "pack_inputs": _pack_inputs(packs),
        "extractor": extractor,
        "source_evidence": source_evidence,
        "fact_proposals": completion.value.get("fact_proposals", []),
        "analysis": completion.value.get("analysis"),
    }
    proposed_uses = completion.value.get("proposed_uses")
    excluded_mentions = completion.value.get("excluded_mentions")
    if proposed_uses:
        record["proposed_uses"] = proposed_uses
        if taxonomy is not None:
            record["taxonomy"] = {
                "id": taxonomy["taxonomy"]["id"],
                "version": taxonomy["taxonomy"]["version"],
            }
    if excluded_mentions:
        record["excluded_mentions"] = excluded_mentions
    validate_extraction_record(record, taxonomy=taxonomy)
    validate_extraction_context(record, inventory, packs)
    return record


def validate_extraction_context(
    record: Mapping[str, Any],
    inventory: Mapping[str, Any],
    packs: Sequence[Mapping[str, Any]],
) -> None:
    """Check the references that a standalone schema cannot resolve by itself."""

    target = next(
        (item for item in inventory["objects"] if item["id"] == record["target"]["id"]),
        None,
    )
    if target is None:
        raise ValidationError("Extraction target is absent from the inventory.")
    if target["type"] != record["target"]["type"]:
        raise ValidationError("Extraction target type does not match the inventory.")
    if record["inventory"]["inventory_id"] != inventory["inventory_id"]:
        raise ValidationError("Extraction inventory id does not match the inventory.")
    if record["inventory"]["snapshot_id"] != inventory["snapshot_id"]:
        raise ValidationError("Extraction snapshot does not match the inventory.")
    if record["inventory"].get("content_hash") != content_hash(inventory):
        raise ValidationError("Extraction inventory hash does not match the inventory.")
    expected_packs = _pack_inputs(packs)
    if record.get("pack_inputs") != expected_packs:
        raise ValidationError("Extraction pack pins do not match the selected packs.")
    allowed_facts = {
        item["id"] for item in _fact_catalogue(packs, target["type"])
    }
    unknown_facts = {
        item["fact_id"] for item in record["fact_proposals"]
    } - allowed_facts
    if unknown_facts:
        raise ValidationError(
            f"Extraction proposed facts outside the selected packs: {sorted(unknown_facts)!r}"
        )
    fact_types = {
        item["id"]: item["type"] for item in _fact_catalogue(packs, target["type"])
    }
    for proposal in record["fact_proposals"]:
        if proposal["state"] != "known":
            continue
        expected_type = fact_types[proposal["fact_id"]]
        if not fact_value_matches_type(proposal.get("value"), expected_type):
            raise ValidationError(
                f"Extracted fact {proposal['fact_id']!r} must contain a value of "
                f"type {expected_type!r}."
            )
    context_evidence = {
        item["id"] for item in _context(inventory, target["id"])["evidence"]
    }
    unknown_evidence = set(record["source_evidence"]) - context_evidence
    if unknown_evidence:
        raise ValidationError(
            "Extraction cites evidence outside the target composition: "
            f"{sorted(unknown_evidence)!r}"
        )


def apply_extraction(
    inventory: Mapping[str, Any],
    extraction: Mapping[str, Any],
    *,
    captured_at: str | None = None,
) -> dict[str, Any]:
    """Create a new snapshot without silently overwriting reliable direct facts."""

    validate_inventory(inventory)
    validate_extraction_record(extraction)
    output = deepcopy(inventory)
    target = next(
        (
            item
            for item in output["objects"]
            if item["id"] == extraction["target"]["id"]
        ),
        None,
    )
    if target is None:
        raise ValidationError("Extraction target is absent from the inventory.")
    if target["type"] != extraction["target"]["type"]:
        raise ValidationError("Extraction target type does not match the inventory.")
    if extraction["inventory"]["inventory_id"] != inventory["inventory_id"]:
        raise ValidationError("Extraction inventory id does not match the inventory.")
    if extraction["inventory"]["snapshot_id"] != inventory["snapshot_id"]:
        raise ValidationError("Extraction snapshot does not match the inventory.")
    expected_hash = extraction["inventory"].get("content_hash")
    if expected_hash is not None and expected_hash != content_hash(inventory):
        raise ValidationError("Extraction inventory hash does not match the inventory.")
    inventory_evidence = {item["id"] for item in inventory["evidence"]}
    if not set(extraction["source_evidence"]).issubset(inventory_evidence):
        raise ValidationError("Extraction cites evidence absent from the inventory.")
    facts = target.setdefault("facts", {})
    extractor = {
        "kind": extraction["extractor"]["kind"],
        "extraction_id": extraction["extraction_id"],
        "model": extraction["extractor"].get("model"),
        "prompt_hash": extraction["extractor"].get("prompt_hash"),
    }
    for proposal in extraction["fact_proposals"]:
        fact_id = proposal["fact_id"]
        existing = facts.get(fact_id)
        proposed = {
            key: deepcopy(value)
            for key, value in proposal.items()
            if key in {"state", "value", "evidence", "confidence"}
        }
        proposed["extractor"] = extractor
        proposed["note"] = proposal["rationale"]
        if not isinstance(existing, Mapping) or existing.get("state") == "unknown":
            facts[fact_id] = proposed
            continue
        if proposal["state"] == "unknown" or existing.get("state") == "conflicted":
            continue
        if (
            existing.get("state") == proposed.get("state")
            and existing.get("value") == proposed.get("value")
        ):
            continue
        facts[fact_id] = {
            "state": "conflicted",
            "evidence": sorted(
                set(existing.get("evidence", [])) | set(proposed.get("evidence", []))
            ),
            "candidate_values": [
                {"source": "existing_snapshot", "value": existing.get("value")},
                {
                    "source": extraction["extraction_id"],
                    "value": proposed.get("value"),
                    "confidence": proposed.get("confidence"),
                },
            ],
            "note": "A model proposal conflicts with an existing fact; review is required.",
        }
    output["captured_at"] = captured_at or _utc_now()
    snapshot_material = {
        "previous_snapshot": inventory["snapshot_id"],
        "extraction_id": extraction["extraction_id"],
        "objects": output["objects"],
        "relations": output["relations"],
        "evidence": output["evidence"],
    }
    output["snapshot_id"] = f"snapshot-{content_hash(snapshot_material)[:24]}"
    validate_inventory(output)
    return output


def _note_prompt(
    extraction: Mapping[str, Any],
    profile_result: Mapping[str, Any],
    *,
    language: str,
) -> tuple[str, str]:
    payload = {
        "language": language,
        "extraction": extraction,
        "profile_assessment": profile_result,
    }
    system = _prompt_template("note-system.txt")
    user = (
        f"Write the assessment note in {language}. Use kind=fact for source claims, "
        "kind=finding for deterministic results and kind=unknown for missing or "
        "conflicted information.\n\n"
        + json.dumps(payload, ensure_ascii=False, sort_keys=True)
    )
    return system, user


def _assessment_index(profile_result: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {
        item["assessment_id"]: item for item in profile_result.get("assessments", [])
    }


def validate_note_context(
    note: Mapping[str, Any],
    extraction: Mapping[str, Any],
    profile_result: Mapping[str, Any],
) -> None:
    """Resolve every model-written note reference against immutable records."""

    assessments = _assessment_index(profile_result)
    allowed_facts = {item["fact_id"] for item in extraction["fact_proposals"]}
    allowed_evidence = set(extraction["source_evidence"])
    for assessment in assessments.values():
        allowed_facts.update(assessment.get("effective_facts", {}))
        allowed_evidence.update(
            evidence_id
            for fact in assessment.get("effective_facts", {}).values()
            if isinstance(fact, Mapping)
            for evidence_id in fact.get("evidence", [])
        )
    for statement in note["statements"]:
        refs = statement["references"]
        fact_ids = refs.get("fact_ids", [])
        evidence_ids = refs.get("evidence", [])
        if statement["kind"] == "fact" and (not fact_ids or not evidence_ids):
            raise ValidationError(
                f"Note fact statement {statement['statement_id']!r} requires fact and evidence references."
            )
        if statement["kind"] == "unknown" and not (
            fact_ids or refs.get("assessment_id")
        ):
            raise ValidationError(
                f"Note unknown statement {statement['statement_id']!r} requires a fact or assessment reference."
            )
        if statement["kind"] in {"fact", "unknown"}:
            unknown_facts = set(fact_ids) - allowed_facts
            unknown_evidence = set(evidence_ids) - allowed_evidence
            if unknown_facts or unknown_evidence:
                raise ValidationError(
                    f"Note statement {statement['statement_id']!r} cites unknown facts or evidence."
                )
        if statement["kind"] != "finding":
            continue
        rule_ids = refs.get("rule_ids", [])
        anchor_ids = refs.get("anchor_ids", [])
        if not refs.get("assessment_id") or not rule_ids or not anchor_ids:
            raise ValidationError(
                f"Note finding statement {statement['statement_id']!r} requires assessment, rule and anchor references."
            )
        assessment = assessments.get(refs.get("assessment_id"))
        if assessment is None:
            raise ValidationError(
                f"Note statement {statement['statement_id']!r} cites an unknown assessment."
            )
        findings = {item["rule_id"]: item for item in assessment["findings"]}
        if any(rule_id not in findings for rule_id in rule_ids):
            raise ValidationError(
                f"Note statement {statement['statement_id']!r} cites an unknown rule."
            )
        anchors = {
            anchor["id"]
            for rule_id in rule_ids
            for anchor in findings[rule_id]["anchors"]
        }
        if not set(anchor_ids).issubset(anchors):
            raise ValidationError(
                f"Note statement {statement['statement_id']!r} cites an unrelated anchor."
            )


def render_note_with_llm(
    extraction: Mapping[str, Any],
    profile_result: Mapping[str, Any],
    client: JsonCompletionClient,
    *,
    language: str = "fr",
    created_at: str | None = None,
) -> dict[str, Any]:
    """Call the explainer after the engine and validate all prose references."""

    system, user = _note_prompt(extraction, profile_result, language=language)
    completion = client.complete_json(
        system=system,
        user=user,
        schema_name="air_assessment_note",
        schema=NOTE_RESPONSE_SCHEMA,
    )
    target = profile_result["target"]
    assessment_ids = [
        item["assessment_id"] for item in profile_result.get("assessments", [])
    ]
    assessed_inventory = profile_result["assessments"][0]["inventory"]
    draft = completion.value
    renderer = {
        "kind": "llm",
        "id": "air-assess",
        "version": "0.3.0",
        "model": {
            "provider": client.provider_name,
            "id": completion.model or client.model,
        },
        "run_id": completion.response_id or f"local-{uuid.uuid4()}",
        "prompt_hash": content_hash({"system": system, "user": user}),
        "prompt_template": {
            "id": "air-assess/note",
            "version": "0.3.0",
            "content_hash": content_hash(system),
        },
    }
    if completion.usage is not None:
        renderer["usage"] = dict(completion.usage)
    stable = {
        "schema_version": "0.1.0",
        "created_at": created_at or _utc_now(),
        "language": language,
        "target": target,
        "inputs": {
            "inventory": {
                "inventory_id": assessed_inventory["inventory_id"],
                "snapshot_id": assessed_inventory["snapshot_id"],
            },
            "extraction_ids": [extraction["extraction_id"]],
            "assessment_ids": assessment_ids,
        },
        "renderer": renderer,
        "summary": draft.get("summary"),
        "scope": draft.get("scope"),
        "statements": draft.get("statements", []),
        "cautions": draft.get("cautions", []),
        "review_status": {"status": "not_selected"},
    }
    note_hash = content_hash(stable)
    note = {"note_id": f"urn:air:note:{note_hash[:24]}", **stable}
    validate_assessment_note(note)
    validate_note_context(note, extraction, profile_result)
    return note


def qualify_with_llm(
    inventory: Mapping[str, Any],
    profile: Mapping[str, Any],
    packs: Sequence[Mapping[str, Any]],
    target_id: str,
    client: JsonCompletionClient,
    *,
    language: str = "fr",
    assessed_at: str | None = None,
    taxonomy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Run model extraction, deterministic packs, then model explanation."""

    validate_inventory(inventory)
    validate_pack_profile(profile)
    verify_profile_packs(profile, packs)
    target = next(
        (item for item in inventory["objects"] if item["id"] == target_id), None
    )
    if target is None:
        raise ValidationError(f"Unknown target object {target_id!r}")
    compatible_packs = [
        pack for pack in packs if target["type"] in pack["pack"]["applies_to"]
    ]
    extraction = extract_with_llm(
        inventory,
        compatible_packs,
        target_id,
        client,
        language=language,
        taxonomy=taxonomy,
    )
    resolved_inventory = apply_extraction(inventory, extraction)
    profile_result = assess_profile(
        resolved_inventory,
        profile,
        packs,
        target_id,
        assessed_at=assessed_at,
    )
    note = render_note_with_llm(
        extraction, profile_result, client, language=language
    )
    return {
        "schema_version": "0.1.0",
        "run_id": f"urn:air:qualification-run:{uuid.uuid4()}",
        "target": profile_result["target"],
        "extraction": extraction,
        "resolved_inventory": resolved_inventory,
        "profile_assessment": profile_result,
        "assessment_note": note,
    }


def write_qualification_bundle(bundle: Mapping[str, Any], output_dir: str | Path) -> None:
    """Write the four auditable stages as separate JSON files."""

    from .io import dump_json

    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    files = {
        "01-extraction.json": bundle["extraction"],
        "02-resolved-inventory.json": bundle["resolved_inventory"],
        "03-assessments.json": bundle["profile_assessment"],
        "04-readable-note.json": bundle["assessment_note"],
    }
    for name, value in files.items():
        (directory / name).write_text(dump_json(value), encoding="utf-8")
    manifest = {
        "schema_version": bundle["schema_version"],
        "run_id": bundle["run_id"],
        "target": bundle["target"],
        "files": list(files),
        "hashes": {name: content_hash(value) for name, value in files.items()},
    }
    (directory / "manifest.json").write_text(dump_json(manifest), encoding="utf-8")


def client_from_environment(
    *,
    model: str | None = None,
    base_url: str | None = None,
    api_key_env: str = "AIR_LLM_API_KEY",
    provider_name: str = "openai-compatible",
    response_format: str = "json_schema",
    reasoning_effort: str | None = None,
    max_tokens: int = 5000,
    timeout: float = 120.0,
) -> OpenAICompatibleClient:
    """Build a client without accepting secrets on the command line."""

    api_key = os.environ.get(api_key_env, "")
    resolved_model = model or os.environ.get("AIR_LLM_MODEL", "")
    resolved_base_url = base_url or os.environ.get(
        "AIR_LLM_BASE_URL", "https://api.openai.com/v1"
    )
    return OpenAICompatibleClient(
        api_key=api_key,
        model=resolved_model,
        base_url=resolved_base_url,
        provider_name=provider_name,
        response_format=response_format,
        reasoning_effort=reasoning_effort,
        max_tokens=max_tokens,
        timeout=timeout,
    )
