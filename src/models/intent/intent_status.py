"""Lifecycle states of an active intent contract."""

from __future__ import annotations

from enum import Enum


class IntentStatus(str, Enum):
    """Lifecycle state of an active intent contract."""

    PENDING = "pending"
    ACTIVE = "active"
    FULFILLED = "fulfilled"
    VIOLATED = "violated"
    EXPIRED = "expired"
