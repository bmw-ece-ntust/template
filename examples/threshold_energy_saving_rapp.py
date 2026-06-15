"""Energy-saving rApp loop using the mock platform and a threshold strategy.

Demonstrates the full core data flow without any network:

    MockPlatformFactory → collect telemetry → analyze → KpiReport
    → ThresholdBasedStrategy.evaluate → PolicyDecision
    → A1Adapter maps the decision to an A1 traffic-steering payload.

Run::

    PYTHONPATH=src python -m examples.threshold_energy_saving_rapp
"""

from __future__ import annotations

from controllers.strategies import ThresholdBasedStrategy
from factories.mock import MockPlatformFactory
from handlers.a1 import A1Adapter
from models import PolicyDecision
from models.parameters import ThreeGPPKpi


def run() -> PolicyDecision:
    """Evaluate one control cycle and return the policy decision."""
    # Low DL PRB utilization → the cell is under-used → SLEEP candidate.
    factory = MockPlatformFactory(
        fixture={
            ThreeGPPKpi.DRB_PRB_UTIL_DL.value: 0.05,
            ThreeGPPKpi.DRB_PRB_UTIL_UL.value: 0.04,
            ThreeGPPKpi.RRC_CONN_MEAN.value: 1.0,
        },
        cell_id="o-du-1111/cell-0",
        gnb_id="gnb-1",
    )
    collector = factory.create_telemetry_collector()
    analyzer = factory.create_kpi_analyzer()

    report = analyzer.analyze(collector.collect())
    strategy = ThresholdBasedStrategy(threshold_low=0.2)
    decision = strategy.evaluate(report)

    # A1Adapter would PUT this payload to the A1 Policy Management Service.
    payload = A1Adapter._decision_to_policy_data(report.cell_id, decision)

    print(f"cell={report.cell_id} prb_dl={report.prb_util_dl:.2f} -> {decision.value}")
    print(f"A1 traffic-steering payload: {payload}")
    return decision


if __name__ == "__main__":
    run()
