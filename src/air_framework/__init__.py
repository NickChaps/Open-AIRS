"""AIR Framework reference engine.

The public API deliberately stays small.  Integrators can load JSON inputs,
validate them and call :func:`assess` without adopting the command-line tool.
"""

from .engine import assess
from .validation import validate_inventory, validate_pack
from .version import __version__

__all__ = ["__version__", "assess", "validate_inventory", "validate_pack"]
