"""RAN policy decision output of every optimization strategy."""

from __future__ import annotations

from enum import Enum


class PolicyDecision(Enum):
    """RAN policy decision output from the optimization strategy."""

    ACTIVE = "active"
    SLEEP = "sleep"
    HANDOVER = "handover"
