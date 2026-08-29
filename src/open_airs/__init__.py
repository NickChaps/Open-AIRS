"""Open AIRS reference engine.

The public API deliberately stays small.  Integrators can load JSON inputs,
validate them and call :func:`assess` without adopting the command-line tool.
"""

from .engine import assess
from .judge import apply_extraction, qualify_with_llm
from .validation import (
    validate_assessment_note,
    validate_extraction_record,
    validate_inventory,
    validate_pack,
    validate_review_record,
)
from .version import __version__

__all__ = [
    "__version__",
    "assess",
    "apply_extraction",
    "qualify_with_llm",
    "validate_assessment_note",
    "validate_extraction_record",
    "validate_inventory",
    "validate_pack",
    "validate_review_record",
]
