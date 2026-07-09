"""Worked O-RAN WG1 energy-saving strategy — the template's reference algorithm.

Implements the carrier / cell switch-off decision logic of the O-RAN WG1
Energy Saving use case: a capacity cell is only a switch-off candidate when
its radio resource load AND its user population are both low, so that no UE
is stranded when coverage is provided by an overlay cell.

O-RAN WG1 Energy Saving use case (Use Case 6, "Energy saving"):
    O-RAN.WG1.Use-Cases-Detailed-Specification — https://specifications.o-ran.org/
Input counters (TS 28.552):
    https://www.3gpp.org/ftp/Specs/archive/28_series/28.552/28552-i50.zip
"""

from __future__ import annotations

from controllers.strategies.optimization_strategy import OptimizationStrategy
from models import KpiReport, PolicyDecision


class EnergySavingStrategy(OptimizationStrategy):
    """Energy-saving decision rule combining PRB load and UE count guards.

    Decision table (evaluated in order):

    1. ``SLEEP`` when **both** DL and UL PRB utilization are below
       ``prb_sleep_threshold`` **and** the mean RRC-connected UE count is at
       most ``max_ues_for_sleep`` — the cell is idle enough to switch off.
    2. ``HANDOVER`` when PRB utilization is below ``prb_sleep_threshold``
       but too many UEs are still attached — offload them first, then a later
       cycle can put the cell to sleep.
    3. ``ACTIVE`` otherwise — the cell is carrying meaningful traffic.

    All three inputs are spec-traceable 3GPP counters
    (`DRB.PrbUtilDL / DRB.PrbUtilUL
    <https://www.3gpp.org/ftp/Specs/archive/28_series/28.552/28552-i50.zip>`_,
    TS 28.552 §5.1.1.12.1 / §5.1.1.12.2, and ``RRC.ConnMean``,
    TS 28.552 §5.1.1.1.1).

    :param prb_sleep_threshold: PRB utilization ratio (0 to 1) below which the
        cell is considered idle.  Applied to both DL and UL.
    :param max_ues_for_sleep: Highest mean RRC-connected UE count that still
        allows an immediate ``SLEEP``; above it the strategy first requests
        ``HANDOVER`` to drain the cell.

    :Example:

        >>> strategy = EnergySavingStrategy(prb_sleep_threshold=0.2, max_ues_for_sleep=2)
        >>> strategy.evaluate(KpiReport("cell-0", prb_util_dl=0.05, active_ue_count=0))
        <PolicyDecision.SLEEP: 'sleep'>
        >>> strategy.evaluate(KpiReport("cell-0", prb_util_dl=0.05, active_ue_count=9))
        <PolicyDecision.HANDOVER: 'handover'>
        >>> strategy.evaluate(KpiReport("cell-0", prb_util_dl=0.75))
        <PolicyDecision.ACTIVE: 'active'>
    """

    def __init__(
        self,
        prb_sleep_threshold: float = 0.2,
        max_ues_for_sleep: int = 2,
    ) -> None:
        self.prb_sleep_threshold = prb_sleep_threshold
        self.max_ues_for_sleep = int(max_ues_for_sleep)

    def evaluate(self, kpis: KpiReport) -> PolicyDecision:
        """Apply the energy-saving decision table.

        :param kpis: Standardised KPI report.
        :return: ``SLEEP``, ``HANDOVER``, or ``ACTIVE`` per the decision table.
        """
        cell_is_idle = (
            kpis.prb_util_dl < self.prb_sleep_threshold
            and kpis.prb_util_ul < self.prb_sleep_threshold
        )
        if not cell_is_idle:
            return PolicyDecision.ACTIVE
        if kpis.active_ue_count <= self.max_ues_for_sleep:
            return PolicyDecision.SLEEP
        return PolicyDecision.HANDOVER
