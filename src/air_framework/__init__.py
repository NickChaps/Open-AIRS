"""AIR Framework reference engine.

The public API deliberately stays small.  Integrators can load JSON inputs,
validate them and call :func:`assess` without adopting the command-line tool.
"""

from .engine import assess
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
    "validate_assessment_note",
    "validate_extraction_record",
    "validate_inventory",
    "validate_pack",
    "validate_review_record",
]
