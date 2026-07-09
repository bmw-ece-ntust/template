"""Optimization strategy wrapping an injected ML model callable."""

from __future__ import annotations

from collections.abc import Callable

from controllers.strategies.optimization_strategy import OptimizationStrategy
from models import KpiReport, PolicyDecision


class MlBasedStrategy(OptimizationStrategy):
    """Wraps any callable model returning a :class:`~models.PolicyDecision`.

    Pass a trained model's inference callable as ``model``.  For NVIDIA NIM,
    wrap :class:`~controllers.strategies.NvidiaModelStrategy` instead.

    :param model: Callable ``(KpiReport) → PolicyDecision``.
    """

    def __init__(self, model: Callable[[KpiReport], PolicyDecision]) -> None:
        self._model = model

    def evaluate(self, kpis: KpiReport) -> PolicyDecision:
        """Invoke the wrapped model.

        :param kpis: Standardised KPI report.
        :return: :class:`~models.PolicyDecision` predicted by the model.
        """
        return self._model(kpis)
