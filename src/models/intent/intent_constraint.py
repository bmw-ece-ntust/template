"""A single measurable constraint within an intent contract."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IntentConstraint:
    """A single measurable constraint within an intent contract.

    :param parameter: 3GPP KPI identifier string
        (use :class:`~models.parameters.ThreeGPPKpi` values).
    :param operator: Comparison operator — ``"gte"``, ``"lte"``, or ``"eq"``.
    :param value: Threshold value in the parameter's native unit.
    """

    parameter: str
    operator: str
    value: float
