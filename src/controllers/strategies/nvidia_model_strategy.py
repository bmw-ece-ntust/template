"""Optimization strategy backed by NVIDIA NeMo / NIM inference."""

from __future__ import annotations

from collections.abc import Callable

from controllers.strategies.optimization_strategy import OptimizationStrategy
from models import KpiReport, PolicyDecision


class NvidiaModelStrategy(OptimizationStrategy):
    """Optimization strategy backed by NVIDIA NeMo / NIM inference.

    Delegates evaluation to a NIM-compatible callable (e.g.
    ``NimAdapter.infer``).  Place all NIM HTTP logic in a dedicated adapter
    module (not under ``handlers/``, which is O-RAN-standard only) and pass
    the infer callable here — strategies must remain I/O-free.

    Security: authenticate via ``Authorization: Bearer <api_key>`` (NVIDIA NIM
    convention).  Pass keys through ``NVIDIA_API_KEY`` env var; never
    hard-code them.  Whitelist only models with known output schemas before
    production use.

    :param nim_infer: Callable ``(KpiReport) → str`` where the return value
        is a :class:`~models.PolicyDecision` string (``"active"``,
        ``"sleep"``, ``"handover"``).  Typically ``NimAdapter.infer``.

    :Example:

        >>> nim = NimAdapter(
        ...     base_url="https://integrate.api.nvidia.com/v1",
        ...     model_id="nvidia/network-optimization",
        ...     api_key=os.environ["NVIDIA_API_KEY"],
        ... )
        >>> strategy = NvidiaModelStrategy(nim_infer=nim.infer)
        >>> decision = strategy.evaluate(kpi_report)
    """

    def __init__(self, nim_infer: Callable[[KpiReport], str]) -> None:
        self._infer = nim_infer

    def evaluate(self, kpis: KpiReport) -> PolicyDecision:
        """Delegate KPI evaluation to the NVIDIA NIM callable.

        :param kpis: Standardised KPI report.
        :return: :class:`~models.PolicyDecision` from the NIM model.
        :raises ValueError: If the NIM response is not a valid PolicyDecision value.
        """
        result: str = self._infer(kpis)
        return PolicyDecision(result)
