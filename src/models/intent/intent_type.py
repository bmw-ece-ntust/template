"""Whitelisted intent types for contract-based IBN (IETF RFC 9315)."""

from __future__ import annotations

from enum import Enum


class IntentType(str, Enum):
    """Whitelisted intent types for contract-based IBN.

    Only types defined here are accepted by
    :class:`~models.intent.IntentResolutionService`.
    Adding a new type requires O-RAN WG2 / IETF SAIN review and a code review.
    """

    ENERGY_SAVING = "energy_saving"
    LOAD_BALANCING = "load_balancing"
    QOS_GUARANTEE = "qos_guarantee"
    COVERAGE_OPTIMIZATION = "coverage_optimization"
    HANDOVER_OPTIMIZATION = "handover_optimization"
