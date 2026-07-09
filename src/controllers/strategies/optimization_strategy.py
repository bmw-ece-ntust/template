"""Abstract base for all rApp / xApp optimization algorithms (Strategy).

Reference: https://refactoring.guru/design-patterns/strategy
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from models import KpiReport, PolicyDecision


class OptimizationStrategy(ABC):
    """Abstract base for rApp / xApp optimization algorithms.

    :Example:

        >>> strategy = ThresholdBasedStrategy(threshold_low=0.2)
        >>> decision = strategy.evaluate(kpi_report)
    """

    @abstractmethod
    def evaluate(self, kpis: KpiReport) -> PolicyDecision:
        """Evaluate current KPIs and return a policy decision.

        :param kpis: Standardised KPI report from the telemetry collector.
        :return: :class:`~models.PolicyDecision` for the RAN controller.
        """
