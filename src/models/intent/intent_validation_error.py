"""Error raised when an intent contract fails a security check."""

from __future__ import annotations


class IntentValidationError(ValueError):
    """Raised when an intent contract fails validation."""
