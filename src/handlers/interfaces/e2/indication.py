"""Decoded E2 Indication message from the Near-RT RIC."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class E2Indication:
    """Decoded E2 Indication message from the Near-RT RIC.

    :param subscription_id: ID returned by
        :meth:`~handlers.interfaces.e2.E2Client.subscribe_kpm`.
    :param ran_function_id: RAN function that produced this indication.
    :param cell_id: Source cell NR CGI.
    :param gnb_id: Source gNB identifier.
    :param pm_counters: 3GPP PM counter name → value mapping.
        Keys are :class:`~models.parameters.ThreeGPPKpi` values.
    :param timestamp_ms: Indication timestamp (Unix epoch milliseconds).
    """

    subscription_id: str
    ran_function_id: int
    cell_id: str
    gnb_id: str
    pm_counters: dict[str, float]
    timestamp_ms: int = 0
