"""Rule-based optimization strategy using a DL PRB utilization threshold."""

from __future__ import annotations

from controllers.strategies.optimization_strategy import OptimizationStrategy
from models import KpiReport, PolicyDecision


class ThresholdBasedStrategy(OptimizationStrategy):
    """Rule-based strategy using DL PRB utilization thresholds.

    :param threshold_low: PRB utilization below which the cell is put to sleep
        (`DRB.PrbUtilDL
        <https://www.3gpp.org/ftp/Specs/archive/28_series/28.552/28552-i50.zip>`_
        < ``threshold_low`` → ``SLEEP``, otherwise ``ACTIVE``).

    .. note::

        A second ``threshold_high`` only makes sense with hysteresis (to avoid
        a cell flapping on/off), which requires the cell's current on/off state
        as input. Add it there if needed — a single threshold is sufficient for
        the stateless ``KpiReport → PolicyDecision`` contract.
    """

    def __init__(self, threshold_low: float = 0.2) -> None:
        self.threshold_low = threshold_low

    def evaluate(self, kpis: KpiReport) -> PolicyDecision:
        """Apply PRB utilization threshold rules.

        :param kpis: Standardised KPI report.
        :return: ``SLEEP`` if DL PRB < ``threshold_low``, else ``ACTIVE``.
        """
        if kpis.prb_util_dl < self.threshold_low:
            return PolicyDecision.SLEEP
        return PolicyDecision.ACTIVE
