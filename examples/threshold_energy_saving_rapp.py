"""Energy-saving rApp cycle on 3GPP-named telemetry (no network required).

Demonstrates the full core data flow with canned ICS-style data:

    canned 3GPP counters → OscKpiAnalyzer → KpiReport
    → EnergySavingStrategy.evaluate → PolicyDecision
    → A1Adapter maps the decision to an A1 policy payload.

In a deployment the same counters arrive via the ICS subscription of
``OscPlatformFactory`` (or a vendor factory such as ``ViaviPlatformFactory``,
see ``examples/vendor_viavi_adapter.py``); only the data source changes,
never the strategy or the models.

Run::

    PYTHONPATH=src python -m examples.threshold_energy_saving_rapp
"""

from __future__ import annotations

from controllers.strategies import EnergySavingStrategy
from factories.osc import OscKpiAnalyzer
from handlers.interfaces.a1 import A1Adapter
from models import PolicyDecision
from models.parameters import ThreeGPPKpi

#: Canned ICS payload — 3GPP counter names exactly as the Non-RT RIC
#: delivers them (TS 28.552).  Low PRB load + one UE → SLEEP candidate.
_FAKE_ICS_RESULT: dict[str, float] = {
    ThreeGPPKpi.DRB_PRB_UTIL_DL.value: 0.05,
    ThreeGPPKpi.DRB_PRB_UTIL_UL.value: 0.04,
    ThreeGPPKpi.RRC_CONN_MEAN.value: 1.0,
}


def run() -> PolicyDecision:
    """Evaluate one control cycle and return the policy decision."""
    analyzer = OscKpiAnalyzer("o-du-1111/cell-0")
    report = analyzer.analyze(_FAKE_ICS_RESULT)

    strategy = EnergySavingStrategy(prb_sleep_threshold=0.2, max_ues_for_sleep=2)
    decision = strategy.evaluate(report)

    # A1Adapter would PUT this payload to the A1 Policy Management Service.
    payload = A1Adapter._decision_to_policy_data(report.cell_id, decision)

    print(f"cell={report.cell_id} prb_dl={report.prb_util_dl:.2f} -> {decision.value}")
    print(f"A1 policy payload: {payload}")
    return decision


if __name__ == "__main__":
    run()
