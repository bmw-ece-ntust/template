"""KPI controller — the rApp/xApp control loop.

Ties the platform components (collector, analyzer from a
:class:`~factories.RAppPlatformFactory`) to an optimization
:class:`~controllers.strategies.OptimizationStrategy`. One cycle is:

    collect raw telemetry → analyze into a KpiReport → evaluate a decision.

The caller (``main.py``, or a scheduler) pushes the resulting
:class:`~models.PolicyDecision` to the Near-RT RIC via an A1/E2 handler.

Pattern reference
    Strategy (this class is the *Context*):
    https://refactoring.guru/design-patterns/strategy
"""

from __future__ import annotations

from controllers.strategies import OptimizationStrategy
from factories import KpiAnalyzer, TelemetryCollector
from models import KpiReport, PolicyDecision


class KpiController:
    """Runs the collect → analyze → decide control cycle.

    :param collector: Platform :class:`~factories.TelemetryCollector`.
    :param analyzer: Platform :class:`~factories.KpiAnalyzer`.
    :param strategy: The :class:`~controllers.strategies.OptimizationStrategy`
        that maps a :class:`~models.KpiReport` to a decision.
    """

    def __init__(
        self,
        collector: TelemetryCollector,
        analyzer: KpiAnalyzer,
        strategy: OptimizationStrategy,
    ) -> None:
        self._collector = collector
        self._analyzer = analyzer
        self._strategy = strategy

    def set_strategy(self, strategy: OptimizationStrategy) -> None:
        """Swap the optimization algorithm at runtime (Strategy pattern).

        This makes :class:`KpiController` the pattern's *Context*: the decision
        algorithm can change while the app runs without rebuilding the loop.

        :param strategy: The replacement :class:`OptimizationStrategy`.
        """
        self._strategy = strategy

    def evaluate_once(self) -> tuple[KpiReport, PolicyDecision]:
        """Run a single control cycle.

        :return: The analyzed :class:`~models.KpiReport` and the resulting
            :class:`~models.PolicyDecision`.
        """
        report = self._analyzer.analyze(self._collector.collect())
        decision = self._strategy.evaluate(report)
        return report, decision
