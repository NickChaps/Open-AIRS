# SPDX-License-Identifier: Apache-2.0
"""Strict JSON input and output helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .errors import ValidationError


def load_json(path: str | Path) -> dict[str, Any]:
    """Load a UTF-8 JSON object and provide a useful validation error."""

    source = Path(path)
    try:
        value = json.loads(source.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValidationError(f"File not found: {source}") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError(
            f"Invalid JSON in {source} at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    if not isinstance(value, dict):
        raise ValidationError(f"Expected a JSON object at the root of {source}")
    return value


def dump_json(value: Any, *, pretty: bool = True) -> str:
    """Serialize JSON without losing non-ASCII legal and business terms."""

    if pretty:
        return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ) + "\n"
