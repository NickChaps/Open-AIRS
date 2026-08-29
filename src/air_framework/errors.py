# SPDX-License-Identifier: Apache-2.0
"""Exceptions exposed by the reference engine."""


class AirFrameworkError(Exception):
    """Base class for errors that can be shown directly to a CLI user."""


class ValidationError(AirFrameworkError):
    """Raised when an inventory, pack or assessment is structurally invalid."""


class EvaluationError(AirFrameworkError):
    """Raised when a valid-looking rule cannot be evaluated safely."""


class LlmError(AirFrameworkError):
    """Raised when the optional model-assisted qualification cannot complete safely."""
