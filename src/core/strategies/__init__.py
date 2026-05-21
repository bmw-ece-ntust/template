"""Strategy pattern — pluggable rApp optimization algorithms.

Implement :class:`OptimizationStrategy` to swap algorithms without
modifying the core rApp framework.

Reference: https://refactoring.guru/design-patterns/strategy
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.models import KpiReport, PolicyDecision


class OptimizationStrategy(ABC):
    """Abstract base for rApp optimization algorithms.

    :Example:

        >>> strategy = ThresholdBasedStrategy(threshold_low=0.2, threshold_high=0.8)
        >>> decision = strategy.evaluate(kpi_report)
    """

    @abstractmethod
    def evaluate(self, kpis: KpiReport) -> PolicyDecision:
        """Evaluate current KPIs and return a policy decision.

        :param kpis: Standardized KPI report from the telemetry collector.
        :return: Policy decision for the RAN controller.
        """


class ThresholdBasedStrategy(OptimizationStrategy):
    """Rule-based strategy using PRB utilization thresholds.

    :param threshold_low: PRB utilization below which the cell is put to sleep.
    :param threshold_high: PRB utilization above which the cell is kept active.
    """

    def __init__(self, threshold_low: float = 0.2, threshold_high: float = 0.8) -> None:
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high

    def evaluate(self, kpis: KpiReport) -> PolicyDecision:
        """Apply threshold rules to the DL PRB utilization.

        :param kpis: Standardized KPI report.
        :return: ``SLEEP`` if utilization is below ``threshold_low``, else ``ACTIVE``.
        """
        if kpis.prb_util_dl < self.threshold_low:
            return PolicyDecision.SLEEP
        return PolicyDecision.ACTIVE


class MlBasedStrategy(OptimizationStrategy):
    """Placeholder for ML-based optimization strategy.

    Replace ``_model`` with your trained model inference call.

    :param model: A callable that accepts a :class:`KpiReport` and returns a
        :class:`PolicyDecision`.
    """

    def __init__(self, model) -> None:
        self._model = model

    def evaluate(self, kpis: KpiReport) -> PolicyDecision:
        """Run ML model inference on the KPI report.

        :param kpis: Standardized KPI report.
        :return: Policy decision predicted by the ML model.
        """
        return self._model(kpis)
