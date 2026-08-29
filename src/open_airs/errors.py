# SPDX-License-Identifier: Apache-2.0
"""Exceptions exposed by the reference engine."""


class OpenAirsError(Exception):
    """Base class for errors that can be shown directly to a CLI user."""


class ValidationError(OpenAirsError):
    """Raised when an inventory, pack or assessment is structurally invalid."""


class EvaluationError(OpenAirsError):
    """Raised when a valid-looking rule cannot be evaluated safely."""


class LlmError(OpenAirsError):
    """Raised when the optional model-assisted qualification cannot complete safely."""
